"""聊天历史记录服务模块"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.chat_history import ChatHistory


def save_chat(
    db: Session,
    user_message: str,
    ai_reply: str,
    context_id: Optional[str] = None,
) -> ChatHistory:
    """保存一条聊天记录"""
    title = user_message[:30] + ("..." if len(user_message) > 30 else "")
    record = ChatHistory(
        context_id=context_id,
        title=title,
        user_message=user_message,
        ai_reply=ai_reply,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_chat_list(db: Session) -> List[ChatHistory]:
    """获取聊天历史列表（按 context_id 分组，每组取第一条）"""
    records = (
        db.query(ChatHistory)
        .order_by(ChatHistory.created_at.desc())
        .all()
    )
    # 按 context_id 去重：有 context_id 的只保留每组第一条，无 context_id 的每条独立
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
    """获取单条聊天记录详情"""
    return db.query(ChatHistory).filter(ChatHistory.id == history_id).first()


def get_chat_group(db: Session, context_id: str) -> List[ChatHistory]:
    """获取同一 context_id 下的所有聊天记录"""
    return (
        db.query(ChatHistory)
        .filter(ChatHistory.context_id == context_id)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )


def delete_chat(db: Session, history_id: int) -> bool:
    """删除聊天记录"""
    record = db.query(ChatHistory).filter(ChatHistory.id == history_id).first()
    if not record:
        return False
    # 同时删除同一 context_id 下的所有记录
    if record.context_id:
        db.query(ChatHistory).filter(ChatHistory.context_id == record.context_id).delete()
    else:
        db.delete(record)
    db.commit()
    return True
