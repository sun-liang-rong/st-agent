"""图片生成 API"""
import json
import uuid

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.services.ai_service import AIService
from app.services.chat_history_service import save_chat

router = APIRouter(prefix="/image", tags=["图片生成"])


@router.post("/generate/stream")
async def generate_image_stream(request: Request):
    """SSE 流式图片生成接口"""
    body = await request.json()
    prompt = body.get("prompt", "")
    style = body.get("style", "旅行海报")
    ratio = body.get("ratio", "1:1")
    context_id = body.get("contextId") or f"image-{uuid.uuid4().hex}"

    async def event_generator():
        db = SessionLocal()
        try:
            # 步骤1: 构思画面
            yield f"data: {json.dumps({'type': 'progress', 'step': 1, 'message': '正在构思画面...'}, ensure_ascii=False)}\n\n"

            ai_service = AIService()

            # 步骤2: 生成图片
            yield f"data: {json.dumps({'type': 'progress', 'step': 2, 'message': '正在生成图片...'}, ensure_ascii=False)}\n\n"
            image_url = await ai_service.generate_image(prompt, style, ratio)

            if not image_url:
                yield f"data: {json.dumps({'type': 'error', 'message': '图片生成失败，请重试'}, ensure_ascii=False)}\n\n"
                return

            # 步骤3: 下载完成
            yield f"data: {json.dumps({'type': 'progress', 'step': 3, 'message': '正在下载图片...'}, ensure_ascii=False)}\n\n"

            # 推送图片结果
            yield f"data: {json.dumps({'type': 'image', 'imageUrl': image_url, 'contextId': context_id, 'ratio': ratio}, ensure_ascii=False)}\n\n"

            # 保存聊天记录（user_message 存用户原始提示词，title 同步）
            save_chat(db=db, user_message=prompt,
                      ai_reply=f"[图片] {image_url}", context_id=context_id,
                      session_type="image", title=prompt, image_ratio=ratio)
            db.commit()

            # 完成
            yield f"data: {json.dumps({'type': 'done', 'message': '图片生成完成'}, ensure_ascii=False)}\n\n"

        except Exception as e:
            db.rollback()
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
        finally:
            db.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
