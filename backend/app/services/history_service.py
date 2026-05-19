"""历史记录服务模块"""
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.report_history import ReportHistory


def create_history(
    db: Session,
    file_id: str,
    file_name: str,
    user_prompt: str,
    generated_prompt: str = "",
    image_url: str = "",
    dashboard_spec: Optional[dict] = None,
    user_id: Optional[int] = None,
    status: str = "completed",
) -> ReportHistory:
    """创建一条历史记录"""
    record = ReportHistory(
        user_id=user_id,
        file_id=file_id,
        file_name=file_name,
        user_prompt=user_prompt,
        generated_prompt=generated_prompt,
        image_url=image_url,
        dashboard_spec=json.dumps(dashboard_spec, ensure_ascii=False) if dashboard_spec else None,
        status=status,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_history_list(db: Session, user_id: Optional[int] = None) -> List[ReportHistory]:
    """获取历史记录列表（按创建时间倒序）"""
    query = db.query(ReportHistory)
    if user_id is not None:
        query = query.filter(ReportHistory.user_id == user_id)
    return query.order_by(ReportHistory.created_at.desc()).all()


def get_history_detail(db: Session, history_id: int) -> Optional[ReportHistory]:
    """获取单条历史记录详情"""
    return db.query(ReportHistory).filter(ReportHistory.id == history_id).first()


def delete_history(db: Session, history_id: int, user_id: Optional[int] = None) -> bool:
    """删除历史记录，只允许删除自己的"""
    query = db.query(ReportHistory).filter(ReportHistory.id == history_id)
    if user_id is not None:
        query = query.filter(ReportHistory.user_id == user_id)
    record = query.first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True
