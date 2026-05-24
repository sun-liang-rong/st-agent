"""AI chat API."""
import asyncio
import json
import logging
import uuid
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import get_db
from app.models.chat_history import ChatHistory
from app.services.ai_service import AIService
from app.services.chat_history_service import (
    delete_chat,
    get_chat_group,
    get_chat_list,
    get_session_list,
    rename_session,
    save_chat,
    stream_chat_message,
    search_sessions,
    get_deleted_sessions,
    restore_session,
    permanent_delete_session,
    clear_trash,
)
from app.utils.common import create_camel_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()


class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    context_id: Optional[str] = Field(None, alias="contextId", description="会话上下文ID")
    generate_image: Optional[bool] = Field(None, alias="generateImage", description="是否生成图片")
    image_style: Optional[str] = Field(None, alias="imageStyle", description="图片风格")
    image_ratio: Optional[str] = Field(None, alias="imageRatio", description="图片比例")

    model_config = {"populate_by_name": True}


class RegenerateRequest(BaseModel):
    message_id: int = Field(..., alias="messageId", description="要重新生成的消息ID")

    model_config = {"populate_by_name": True}


class RenameSessionRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="会话标题")


class SearchRequest(BaseModel):
    q: str = Field(..., min_length=1, description="搜索关键词")
    limit: Optional[int] = Field(20, ge=1, le=100, description="返回数量限制")


@router.post("/stream")
async def chat_stream(request: ChatRequest, http_request: Request, db: Session = Depends(get_db)):
    """SSE streaming chat endpoint with optional image generation."""
    context_id = request.context_id or f"chat-{uuid.uuid4().hex}"
    should_generate_image = request.generate_image or AIService.detect_image_intent(request.message)
    image_style = request.image_style or "旅行海报"
    image_ratio = request.image_ratio or "1:1"

    async def event_generator():
        full_reply = ""
        image_url = None
        try:
            # If image generation is requested, generate image first
            if should_generate_image:
                yield f"event: image_intent\ndata: {json.dumps({'message': '正在为你生成图片...'}, ensure_ascii=False)}\n\n"

                # Step 1: composing
                yield f"event: image_progress\ndata: {json.dumps({'step': 1, 'message': '正在构思画面...'}, ensure_ascii=False)}\n\n"

                # Step 2: generating
                yield f"event: image_progress\ndata: {json.dumps({'step': 2, 'message': '正在生成图片...'}, ensure_ascii=False)}\n\n"

                ai_svc = AIService()
                image_path = await ai_svc.generate_image(
                    prompt=request.message,
                    style=image_style,
                    ratio=image_ratio,
                )

                if image_path:
                    image_url = "/" + image_path.replace("\\", "/")
                    # Step 3: downloading
                    yield f"event: image_progress\ndata: {json.dumps({'step': 3, 'message': '正在下载图片...'}, ensure_ascii=False)}\n\n"
                    yield f"event: image_result\ndata: {json.dumps({'imageUrl': image_url, 'contextId': context_id}, ensure_ascii=False)}\n\n"
                else:
                    yield f"event: image_progress\ndata: {json.dumps({'step': 3, 'message': '图片生成失败，继续文字回复'}, ensure_ascii=False)}\n\n"

            # Continue with text chat stream
            async for chunk_json in stream_chat_message(request.message, context_id):
                if await http_request.is_disconnected():
                    logger.info("Client disconnected during stream")
                    return

                chunk = json.loads(chunk_json)
                if chunk["type"] == "token":
                    full_reply += chunk["content"]
                    yield f"event: token\ndata: {json.dumps({'content': chunk['content']}, ensure_ascii=False)}\n\n"
                elif chunk["type"] == "done":
                    try:
                        session_type = "chat"
                        if should_generate_image and image_url:
                            full_reply += f"\n\n![生成的图片]({image_url})"
                            session_type = "image"
                        save_chat(
                            db, request.message, full_reply, context_id,
                            session_type=session_type,
                            image_url=image_url,
                            image_ratio=image_ratio if should_generate_image else None,
                        )
                    except Exception as e:
                        logger.error(f"Failed to save chat after stream: {e}")
                    yield f"event: done\ndata: {json.dumps({'contextId': context_id}, ensure_ascii=False)}\n\n"
                elif chunk["type"] == "error":
                    yield f"event: error\ndata: {json.dumps({'message': chunk['message']}, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.error(f"Stream chat error: {e}")
            yield f"event: error\ndata: {json.dumps({'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Non-streaming chat endpoint with retry."""
    context_id = request.context_id or f"chat-{uuid.uuid4().hex}"
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    f"{settings.SENSENOVA_API_BASE}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.SENSENOVA_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.SENSENOVA_PROMPT_MODEL,
                        "messages": [
                            {"role": "system", "content": "你是一个智能助手。请用中文回复，语气友好、专业，回复简洁清晰。"},
                            {"role": "user", "content": request.message},
                        ],
                        "temperature": 0.8,
                        "max_tokens": 2000,
                    },
                )
                response.raise_for_status()
                data = response.json()
                reply = data["choices"][0]["message"]["content"]

            save_chat(db, request.message, reply, context_id)
            return create_camel_response({"reply": reply, "contextId": context_id})

        except httpx.HTTPStatusError as e:
            last_error = e
            logger.warning(
                "[聊天] 第%d次请求失败, status=%d | context_id=%s",
                attempt,
                e.response.status_code,
                context_id,
            )
            if e.response.status_code < 500 or e.response.status_code == 422:
                break
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            last_error = e
            logger.warning("[聊天] 第%d次请求失败 | context_id=%s error=%s", attempt, context_id, str(e))

        if attempt < MAX_RETRIES:
            await asyncio.sleep(RETRY_DELAYS[attempt - 1])

    logger.error("[聊天] 全部重试失败 | context_id=%s", context_id)
    raise HTTPException(status_code=502, detail=f"AI 服务暂时不可用: {str(last_error)}")


@router.post("/regenerate/{message_id}")
async def chat_regenerate(message_id: int, http_request: Request, db: Session = Depends(get_db)):
    """SSE streaming regenerate endpoint."""
    record = db.query(ChatHistory).filter(ChatHistory.id == message_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="消息不存在")

    context_id = record.context_id
    user_message = record.user_message

    async def event_generator():
        full_reply = ""
        try:
            async for chunk_json in stream_chat_message(user_message, context_id):
                if await http_request.is_disconnected():
                    logger.info("Client disconnected during regenerate stream")
                    return

                chunk = json.loads(chunk_json)
                if chunk["type"] == "token":
                    full_reply += chunk["content"]
                    yield f"event: token\ndata: {json.dumps({'content': chunk['content']}, ensure_ascii=False)}\n\n"
                elif chunk["type"] == "done":
                    # Update the existing record's ai_reply
                    record.ai_reply = full_reply
                    db.commit()
                    db.refresh(record)
                    yield f"event: done\ndata: {json.dumps({'contextId': context_id, 'messageId': message_id}, ensure_ascii=False)}\n\n"
                elif chunk["type"] == "error":
                    yield f"event: error\ndata: {json.dumps({'message': chunk['message']}, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.error(f"Regenerate stream error: {e}")
            yield f"event: error\ndata: {json.dumps({'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]


# ─── 会话列表 ────────────────────────────────────────────────


@router.get("/sessions")
async def list_sessions(db: Session = Depends(get_db)):
    rows = get_session_list(db)
    return create_camel_response(rows)


@router.get("/sessions/search")
async def search_sessions_endpoint(q: str, limit: int = 20, db: Session = Depends(get_db)):
    """搜索会话"""
    results = search_sessions(db, q, limit)
    return create_camel_response(results)


@router.get("/session/{context_id}")
async def session_detail(context_id: str, db: Session = Depends(get_db)):
    rows = get_chat_group(db, context_id)
    if not rows:
        return create_camel_response([])
    return create_camel_response(rows)


@router.delete("/session/{context_id}")
async def session_delete(context_id: str, db: Session = Depends(get_db)):
    delete_chat(db, context_id)
    return create_camel_response({"ok": True})


@router.patch("/session/{context_id}")
async def session_rename(context_id: str, request: RenameSessionRequest, db: Session = Depends(get_db)):
    ok = rename_session(db, context_id, request.title)
    if not ok:
        raise HTTPException(status_code=404, detail="会话不存在")
    return create_camel_response({"ok": True, "context_id": context_id, "title": request.title.strip()})


# ─── 回收站 ──────────────────────────────────────────────────


@router.get("/trash")
async def trash_list(db: Session = Depends(get_db)):
    """获取回收站（已删除的会话列表）"""
    results = get_deleted_sessions(db)
    return create_camel_response(results)


@router.post("/trash/{context_id}/restore")
async def trash_restore(context_id: str, db: Session = Depends(get_db)):
    """恢复已删除的会话"""
    ok = restore_session(db, context_id)
    if not ok:
        raise HTTPException(status_code=404, detail="会话不存在")
    return create_camel_response({"ok": True})


@router.delete("/trash/{context_id}")
async def trash_permanent_delete(context_id: str, db: Session = Depends(get_db)):
    """永久删除会话"""
    ok = permanent_delete_session(db, context_id)
    if not ok:
        raise HTTPException(status_code=404, detail="会话不存在")
    return create_camel_response({"ok": True})


@router.delete("/trash")
async def trash_clear(db: Session = Depends(get_db)):
    """清空回收站"""
    count = clear_trash(db)
    return create_camel_response({"ok": True, "count": count})


# ─── 历史记录（旧接口） ──────────────────────────────────────


@router.get("/history")
async def list_history(db: Session = Depends(get_db)):
    rows = get_chat_list(db)
    return create_camel_response(rows)


@router.get("/history/{context_id}")
async def history_detail(context_id: str, db: Session = Depends(get_db)):
    rows = get_chat_group(db, context_id)
    if not rows:
        return create_camel_response([])
    return create_camel_response(rows)


@router.delete("/history/{context_id}")
async def history_delete(context_id: str, db: Session = Depends(get_db)):
    delete_chat(db, context_id)
    return create_camel_response({"ok": True})