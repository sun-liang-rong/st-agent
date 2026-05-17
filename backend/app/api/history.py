"""历史记录 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models import get_db
from app.services.history_service import (
    get_history_list,
    get_history_detail,
    delete_history,
)
from app.utils.common import create_camel_response


router = APIRouter(prefix="/history", tags=["history"])


@router.get("")
async def get_history(
    db: Session = Depends(get_db),
):
    """获取历史记录列表（按时间倒序）"""
    records = get_history_list(db)
    data = [
        {
            "id": str(r.id),
            "file_id": r.file_id,
            "file_name": r.file_name,
            "user_prompt": r.user_prompt,
            "generated_prompt": r.generated_prompt,
            "image_url": r.image_url,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else "",
            "updated_at": r.updated_at.isoformat() if r.updated_at else "",
        }
        for r in records
    ]
    return create_camel_response({"data": data})


@router.get("/{history_id}")
async def get_history_detail_endpoint(
    history_id: int,
    db: Session = Depends(get_db),
):
    """获取单条历史记录详情"""
    record = get_history_detail(db, history_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return create_camel_response({
        "id": str(record.id),
        "file_id": record.file_id,
        "file_name": record.file_name,
        "user_prompt": record.user_prompt,
        "generated_prompt": record.generated_prompt,
        "image_url": record.image_url,
        "status": record.status,
        "created_at": record.created_at.isoformat() if record.created_at else "",
        "updated_at": record.updated_at.isoformat() if record.updated_at else "",
    })


@router.delete("/{history_id}")
async def delete_history_endpoint(
    history_id: int,
    db: Session = Depends(get_db),
):
    """删除历史记录"""
    success = delete_history(db, history_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"message": "删除成功"}
