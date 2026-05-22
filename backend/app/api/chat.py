"""AI chat API."""
import asyncio
import json
import logging
import time
import uuid
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import get_db
from app.services.chat_history_service import (
    delete_chat,
    get_chat_group,
    get_chat_list,
    get_session_list,
    save_chat,
    stream_chat_message,
)
from app.utils.common import create_camel_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()


class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    context_id: Optional[str] = Field(None, alias="contextId", description="会话上下文ID")

    model_config = {"populate_by_name": True}


@router.post("/stream")
async def chat_stream(request: ChatRequest, http_request: Request, db: Session = Depends(get_db)):
    """SSE streaming chat endpoint."""
    context_id = request.context_id or f"chat-{uuid.uuid4().hex}"

    async def event_generator():
        full_reply = ""
        try:
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
                        save_chat(db, request.message, full_reply, context_id)
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


MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]


# ─── 会话列表 ────────────────────────────────────────────────


@router.get("/sessions")
async def list_sessions(db: Session = Depends(get_db)):
    rows = get_session_list(db)
    return create_camel_response(rows)


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
