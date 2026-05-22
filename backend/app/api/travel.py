"""旅游攻略生成 API — 流式 SSE 响应"""
import json
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.services.ai_service import aiservice
from app.models import get_db
from app.services.chat_history_service import save_chat

logger = logging.getLogger("app.api.travel")

router = APIRouter(prefix="/travel", tags=["travel"])


class TravelRequest(BaseModel):
    destination: str = Field(..., min_length=1, description='目的地（如 "上海一日游"）')
    days: int = Field(0, ge=0, le=30, description="旅行天数（0 表示让 AI 从目的地文本自行解析）")
    preferences: str = Field("", description="偏好（可空，AI 从目的地文本自行解析）")


def sse_event(event_type: str, data: dict) -> str:
    """格式化 SSE 事件"""
    return f"data: {json.dumps({'type': event_type, 'data': data}, ensure_ascii=False)}\n\n"


@router.post("")
async def generate_travel_stream(request: TravelRequest, db: Session = Depends(get_db)):
    """流式生成旅游攻略（SSE）"""

    async def event_stream():
        logger.info(
            "🟢 [旅游攻略] 收到请求 | destination=%s days=%d preferences=%s",
            request.destination, request.days, request.preferences or "无",
        )
        try:
            # 1. 开始事件
            yield sse_event("progress", {"message": "正在规划行程...", "step": 1, "total": 3})

            full_content = ""
            # 2. 流式生成攻略文本
            async for token in aiservice.generate_travel_itinerary_stream(
                destination=request.destination,
                days=request.days,
                preferences=request.preferences,
            ):
                full_content += token
                yield sse_event("token", {"content": token})

            # 3. 文本完成事件
            yield sse_event("text_done", {"full_content": full_content})

            # 4. 通知前端开始加载图片（显示 loading 占位）
            yield sse_event("image_loading", {"message": "正在生成目的地海报..."})

            # 5. 生成图片（耗时操作，把攻略内容传给模型参考）
            image_path = await aiservice.generate_travel_image(
                destination=request.destination,
                preferences=request.preferences,
                itinerary=full_content,
            )

            image_url = ""
            if image_path:
                image_url = "/" + image_path.replace("\\", "/")
                yield sse_event("image", {"url": image_url})
            else:
                yield sse_event("image", {"url": ""})

            # 6. 保存对话到历史记录
            try:
                user_msg = f"{request.destination}{request.days}日游"
                if request.preferences:
                    user_msg += f"，{request.preferences}"
                ai_reply = full_content
                if image_url:
                    ai_reply += f"\n\n![攻略海报]({image_url})"
                context_id = f"travel-{uuid.uuid4().hex}"
                save_chat(db=db, user_message=user_msg, ai_reply=ai_reply, context_id=context_id)
                logger.info("💾 [旅游攻略] 对话已保存 | destination=%s", request.destination)
            except Exception as e:
                logger.warning("⚠️ [旅游攻略] 保存对话失败 | error=%s", e)

            # 7. 完成
            logger.info(
                "✅ [旅游攻略] 全部完成 | destination=%s image_url=%s",
                request.destination, image_url or "无",
            )
            yield sse_event("done", {"message": "攻略生成完成"})

        except Exception as e:
            logger.error(
                "❌ [旅游攻略] 生成异常 | destination=%s error=%s",
                request.destination, str(e),
            )
            yield sse_event("error", {"message": str(e)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
