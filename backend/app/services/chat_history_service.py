"""聊天历史记录服务模块"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.chat_history import ChatHistory


def save_chat(
    db: Session,
    user_message: str,
    ai_reply: str,
) -> ChatHistory:
    """保存一条聊天记录"""
    title = user_message[:30] + ("..." if len(user_message) > 30 else "")
    record = ChatHistory(
        title=title,
        user_message=user_message,
        ai_reply=ai_reply,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_chat_list(db: Session) -> List[ChatHistory]:
    """获取聊天历史列表（按时间倒序）"""
    return (
        db.query(ChatHistory)
        .order_by(ChatHistory.created_at.desc())
        .all()
    )


def get_chat_detail(db: Session, history_id: int) -> Optional[ChatHistory]:
    """获取单条聊天记录详情"""
    return db.query(ChatHistory).filter(ChatHistory.id == history_id).first()


def delete_chat(db: Session, history_id: int) -> bool:
    """删除聊天记录"""
    record = db.query(ChatHistory).filter(ChatHistory.id == history_id).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True
