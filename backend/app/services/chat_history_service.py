"""Chat history service."""
import json
import logging
import asyncio
import time
from datetime import datetime
from typing import AsyncGenerator, List, Optional

import httpx
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.chat_history import ChatHistory

logger = logging.getLogger("app.chat_history_service")
settings = get_settings()

MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]


def _is_retryable_http_error(e: Exception) -> bool:
    """判断错误是否可重试"""
    if isinstance(e, httpx.HTTPStatusError):
        return e.response.status_code in (429,) or e.response.status_code >= 500
    return isinstance(
        e,
        (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.RemoteProtocolError,
            httpx.StreamError,
            httpx.ReadTimeout,
            httpx.WriteTimeout,
        ),
    )


def save_chat(
    db: Session,
    user_message: str,
    ai_reply: str,
    context_id: Optional[str] = None,
    session_type: Optional[str] = "chat",
    title: Optional[str] = None,
    image_url: Optional[str] = None,
    image_ratio: Optional[str] = None,
) -> ChatHistory:
    """Save one chat record."""
    display_title = title if title is not None else user_message[:30] + ("..." if len(user_message) > 30 else "")
    record = ChatHistory(
        context_id=context_id,
        session_type=session_type,
        image_url=image_url,
        image_ratio=image_ratio,
        title=display_title,
        user_message=user_message,
        ai_reply=ai_reply,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


async def stream_chat_message(
    message: str,
    context_id: str,
) -> AsyncGenerator[str, None]:
    """
    流式调用 AI 聊天接口，逐 token 产出内容。
    生成完成后，调用方需自行将完整消息存入数据库。

    yield 的每个值是一个 JSON 字符串，格式为：
      {"type": "token", "content": "..."}  -- 文本片段
      {"type": "done", "contextId": "..."} -- 生成完成
      {"type": "error", "message": "..."}  -- 错误
    """
    url = f"{settings.SENSENOVA_API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.SENSENOVA_API_KEY}",
        "Content-Type": "application/json",
    }

    system_prompt = (
        "你是一个智能助手。请用中文回复，语气友好、专业，回复简洁清晰。"
    )

    data = {
        "model": settings.SENSENOVA_PROMPT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
        "temperature": 0.8,
        "max_tokens": 2000,
        "stream": True,
    }

    start_time = time.time()
    token_count = 0

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST", url, headers=headers, json=data,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        json_str = line[6:].strip()
                        if json_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(json_str)
                            choices = chunk.get("choices", [])
                            if not choices:
                                continue
                            delta = choices[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                token_count += 1
                                yield json.dumps(
                                    {"type": "token", "content": content},
                                    ensure_ascii=False,
                                )
                        except json.JSONDecodeError:
                            continue

            # 流式正常完成
            elapsed = time.time() - start_time
            logger.info(
                "[流式聊天] 完成 | context_id=%s tokens=%d elapsed=%.2fs attempt=%d",
                context_id, token_count, elapsed, attempt,
            )
            yield json.dumps(
                {"type": "done", "contextId": context_id}, ensure_ascii=False
            )
            return

        except Exception as e:
            elapsed = time.time() - start_time
            retryable = _is_retryable_http_error(e) and token_count == 0

            if retryable and attempt < MAX_RETRIES:
                delay = RETRY_DELAYS[attempt - 1]
                logger.warning(
                    "[流式聊天] 第%d次失败, %ds后重试 | error=%s elapsed=%.2fs",
                    attempt, delay, str(e), elapsed,
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    "[流式聊天] 失败 | context_id=%s attempt=%d/%d error=%s elapsed=%.2fs",
                    context_id, attempt, MAX_RETRIES, str(e), elapsed,
                )
                yield json.dumps(
                    {"type": "error", "message": str(e)}, ensure_ascii=False
                )
                return


def get_chat_list(db: Session) -> List[ChatHistory]:
    """Get chat history list (excluding deleted)."""
    records = (
        db.query(ChatHistory)
        .filter(ChatHistory.is_deleted == False)
        .order_by(ChatHistory.created_at.desc())
        .all()
    )
    seen_contexts = set()
    result = []
    for r in records:
        if r.context_id:
            if r.context_id not in seen_contexts:
                seen_contexts.add(r.context_id)
                result.append(r)
        else:
            result.append(r)
    return result


def get_chat_detail(db: Session, history_id: int) -> Optional[ChatHistory]:
    return db.query(ChatHistory).filter(
        ChatHistory.id == history_id,
        ChatHistory.is_deleted == False,
    ).first()


def get_chat_group(db: Session, context_id: str) -> List[ChatHistory]:
    return (
        db.query(ChatHistory)
        .filter(ChatHistory.context_id == context_id, ChatHistory.is_deleted == False)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )


def get_session_list(db: Session):
    grouped = (
        db.query(
            ChatHistory.context_id.label("context_id"),
            func.max(ChatHistory.created_at).label("updated_at"),
            func.min(ChatHistory.id).label("first_id"),
        )
        .filter(ChatHistory.context_id.isnot(None), ChatHistory.is_deleted == False)
        .group_by(ChatHistory.context_id)
        .order_by(func.max(ChatHistory.created_at).desc())
        .all()
    )

    result = []
    for g in grouped:
        first = db.query(ChatHistory).filter(ChatHistory.id == g.first_id).first()
        if not first:
            continue
        result.append(
            {
                "context_id": g.context_id,
                "title": first.title or first.user_message[:30],
                "summary": first.user_message or "",
                "session_type": first.session_type or "chat",
                "updated_at": g.updated_at.isoformat() if g.updated_at else "",
            }
        )
    return result


def delete_chat(db: Session, context_id: str) -> bool:
    """Soft delete: mark all records in a session as deleted."""
    now = datetime.utcnow()
    count = (
        db.query(ChatHistory)
        .filter(ChatHistory.context_id == context_id, ChatHistory.is_deleted == False)
        .update({ChatHistory.is_deleted: True, ChatHistory.deleted_at: now}, synchronize_session=False)
    )
    if count == 0:
        return False
    db.commit()
    return True


def rename_session(db: Session, context_id: str, title: str) -> bool:
    """Rename all records in one session."""
    normalized_title = title.strip()
    if not normalized_title:
        return False
    count = (
        db.query(ChatHistory)
        .filter(ChatHistory.context_id == context_id, ChatHistory.is_deleted == False)
        .update({ChatHistory.title: normalized_title}, synchronize_session=False)
    )
    if count == 0:
        return False
    db.commit()
    return True


# ─── 搜索功能 ───────────────────────────────────────────────────


def search_sessions(db: Session, keyword: str, limit: int = 20) -> List[dict]:
    """搜索会话：匹配标题、用户消息、AI回复"""
    pattern = f"%{keyword}%"
    results = (
        db.query(ChatHistory)
        .filter(
            ChatHistory.is_deleted == False,
            ChatHistory.context_id.isnot(None),
            or_(
                ChatHistory.title.like(pattern),
                ChatHistory.user_message.like(pattern),
                ChatHistory.ai_reply.like(pattern),
            ),
        )
        .order_by(ChatHistory.created_at.desc())
        .limit(limit * 5)  # Get more to deduplicate
        .all()
    )

    seen_contexts = set()
    out = []
    for r in results:
        if r.context_id in seen_contexts:
            continue
        seen_contexts.add(r.context_id)

        # Extract matching snippet
        snippet = ""
        if keyword.lower() in (r.user_message or "").lower():
            snippet = r.user_message[:80]
        elif keyword.lower() in (r.ai_reply or "").lower():
            # Find the line containing the keyword
            for line in (r.ai_reply or "").split("\n"):
                if keyword.lower() in line.lower():
                    snippet = line[:80]
                    break
            if not snippet:
                snippet = r.ai_reply[:80]

        out.append({
            "context_id": r.context_id,
            "title": r.title or r.user_message[:30],
            "session_type": r.session_type or "chat",
            "snippet": snippet,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        })
    return out[:limit]


# ─── 回收站功能 ─────────────────────────────────────────────────


def get_deleted_sessions(db: Session) -> List[dict]:
    """获取已软删除的会话列表"""
    grouped = (
        db.query(
            ChatHistory.context_id.label("context_id"),
            func.max(ChatHistory.created_at).label("updated_at"),
            func.min(ChatHistory.id).label("first_id"),
            func.max(ChatHistory.deleted_at).label("deleted_at"),
        )
        .filter(ChatHistory.context_id.isnot(None), ChatHistory.is_deleted == True)
        .group_by(ChatHistory.context_id)
        .order_by(func.max(ChatHistory.deleted_at).desc())
        .all()
    )

    result = []
    for g in grouped:
        first = db.query(ChatHistory).filter(ChatHistory.id == g.first_id).first()
        if not first:
            continue
        result.append({
            "context_id": g.context_id,
            "title": first.title or first.user_message[:30],
            "session_type": first.session_type or "chat",
            "deleted_at": g.deleted_at.isoformat() if g.deleted_at else "",
        })
    return result


def restore_session(db: Session, context_id: str) -> bool:
    """恢复已删除的会话"""
    count = (
        db.query(ChatHistory)
        .filter(ChatHistory.context_id == context_id, ChatHistory.is_deleted == True)
        .update({ChatHistory.is_deleted: False, ChatHistory.deleted_at: None}, synchronize_session=False)
    )
    if count == 0:
        return False
    db.commit()
    return True


def permanent_delete_session(db: Session, context_id: str) -> bool:
    """永久删除会话（从数据库中彻底移除）"""
    count = db.query(ChatHistory).filter(
        ChatHistory.context_id == context_id, ChatHistory.is_deleted == True
    ).delete()
    if count == 0:
        return False
    db.commit()
    return True


def clear_trash(db: Session) -> int:
    """清空回收站：永久删除所有已软删除的记录"""
    count = db.query(ChatHistory).filter(ChatHistory.is_deleted == True).delete()
    db.commit()
    return count