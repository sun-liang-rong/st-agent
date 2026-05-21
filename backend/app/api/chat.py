"""AI 聊天 API"""
import asyncio
import httpx
import logging
import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import get_db
from app.services.chat_history_service import save_chat, get_chat_list, get_chat_detail, get_chat_group, delete_chat
from app.utils.common import create_camel_response

logger = logging.getLogger("app.api.chat")

router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()

# ── 重试配置 ──
MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]

def _is_retryable_http_error(e: Exception) -> bool:
    """判断 HTTP 错误是否可重试"""
    if isinstance(e, httpx.HTTPStatusError):
        return e.response.status_code in (429,) or e.response.status_code >= 500
    if isinstance(e, (httpx.TimeoutException, httpx.ConnectError,
                      httpx.RemoteProtocolError, httpx.StreamError,
                      httpx.ReadTimeout, httpx.WriteTimeout)):
        return True
    return False


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户消息")
    contextId: Optional[str] = Field(None, description="会话分组ID，继续历史对话时传入历史记录ID")


@router.post("")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """与 AI 自由对话（自动保存聊天记录）"""
    url = f"{settings.SENSENOVA_API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.SENSENOVA_API_KEY}",
        "Content-Type": "application/json",
    }

    system_prompt = """你是一个智能助手，运行在 AI 报表生成平台中。你可以：
- 与用户自由对话，回答各种问题
- 帮助用户分析数据、提供建议
- 解释图表和数据相关的概念
- 提供 Excel 和数据分析方面的帮助

请用中文回复，保持友好、专业的语气。回答简洁清晰。"""

    data = {
        "model": settings.SENSENOVA_PROMPT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message},
        ],
        "temperature": 0.8,
        "max_tokens": 2000,
    }

    logger.info(
        "📤 [自由对话] 开始请求 | message_preview=%s model=%s",
        request.message[:50] + ("..." if len(request.message) > 50 else ""),
        settings.SENSENOVA_PROMPT_MODEL,
    )
    logger.debug(
        "📦 [自由对话] 完整请求 | message=%s system_prompt=%s",
        request.message, system_prompt[:100] + "...",
    )

    start_time = time.time()

    # ── 重试循环：最多 MAX_RETRIES 次 ──
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()

            elapsed = time.time() - start_time
            logger.info(
                "📡 [自由对话] 响应收到 (attempt %d/%d) | status=%s elapsed=%.2fs",
                attempt, MAX_RETRIES, response.status_code, elapsed,
            )

            if "choices" in result and len(result["choices"]) > 0:
                reply = result["choices"][0]["message"]["content"]
                logger.info(
                    "✅ [自由对话] 完成 (attempt %d/%d) | reply_len=%d chars elapsed=%.2fs",
                    attempt, MAX_RETRIES, len(reply), elapsed,
                )
                logger.debug(
                    "📦 [自由对话] 回复内容 | reply=%s",
                    reply[:200] + ("..." if len(reply) > 200 else ""),
                )

                # 保存聊天记录（同一会话用同一 context_id 分组）
                try:
                    context_id = request.contextId or None
                    save_chat(db=db, user_message=request.message, ai_reply=reply, context_id=context_id)
                except Exception as e:
                    logger.warning("⚠️ [自由对话] 保存聊天记录失败 | error=%s", e)

                return create_camel_response({"reply": reply})
            else:
                logger.error(
                    "❌ [自由对话] 返回格式异常 (attempt %d/%d) | result=%s elapsed=%.2fs",
                    attempt, MAX_RETRIES, result, elapsed,
                )
                raise HTTPException(status_code=500, detail="AI 返回格式错误")

        except Exception as e:
            elapsed = time.time() - start_time
            retryable = _is_retryable_http_error(e)

            if retryable and attempt < MAX_RETRIES:
                delay = RETRY_DELAYS[attempt - 1]
                logger.warning(
                    "⚠️ [自由对话] 第%d次失败, %ds后重试 (attempt %d/%d) | error=%s elapsed=%.2fs",
                    attempt, delay, attempt, MAX_RETRIES, str(e), elapsed,
                )
                await asyncio.sleep(delay)
            else:
                reason = "不可重试错误" if not retryable else "全部重试耗尽"
                if isinstance(e, httpx.HTTPStatusError):
                    logger.error(
                        "❌ [自由对话] HTTP错误 | status=%s response=%s elapsed=%.2fs",
                        e.response.status_code, e.response.text[:200], elapsed,
                    )
                    raise HTTPException(
                        status_code=502,
                        detail=f"AI 服务调用失败 ({e.response.status_code})",
                    )
                logger.error(
                    "❌ [自由对话] %s (attempt %d/%d) | error=%s elapsed=%.2fs",
                    reason, attempt, MAX_RETRIES, str(e), elapsed,
                )
                raise HTTPException(status_code=500, detail=f"聊天服务异常: {str(e)}")


# ── 聊天历史记录 ──


@router.get("/history")
async def get_chat_history(db: Session = Depends(get_db)):
    """获取聊天历史记录列表"""
    records = get_chat_list(db)
    data = [
        {
            "id": str(r.id),
            "context_id": r.context_id,
            "title": r.title or r.user_message[:30],
            "user_message": r.user_message,
            "ai_reply": r.ai_reply,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        }
        for r in records
    ]
    return create_camel_response({"data": data})


@router.get("/history/{history_id}")
async def get_chat_history_detail(history_id: int, db: Session = Depends(get_db)):
    """获取单条聊天记录"""
    record = get_chat_detail(db, history_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return create_camel_response({
        "id": str(record.id),
        "title": record.title,
        "user_message": record.user_message,
        "ai_reply": record.ai_reply,
        "created_at": record.created_at.isoformat() if record.created_at else "",
    })


@router.get("/history/group/{context_id}")
async def get_chat_group_endpoint(context_id: str, db: Session = Depends(get_db)):
    """获取同一会话分组的所有聊天记录（继续对话时加载完整上下文）"""
    records = get_chat_group(db, context_id)
    data = [
        {
            "id": str(r.id),
            "title": r.title,
            "user_message": r.user_message,
            "ai_reply": r.ai_reply,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        }
        for r in records
    ]
    return create_camel_response({"data": data})


@router.delete("/history/{history_id}")
async def delete_chat_history(history_id: int, db: Session = Depends(get_db)):
    """删除聊天记录"""
    ok = delete_chat(db, history_id)
    if not ok:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"message": "删除成功"}
