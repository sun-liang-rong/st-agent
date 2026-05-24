"""分享 API"""
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.share import Share
from app.models.chat_history import ChatHistory
from app.models.user import User
from app.services.chat_history_service import get_chat_group
from app.utils.common import create_camel_response
from app.utils.security import get_current_user

router = APIRouter(prefix="/share", tags=["分享"])


class CreateShareRequest(BaseModel):
    type: str = Field(..., pattern="^(travel|image)$", description="分享类型")
    content_id: str = Field(..., alias="contentId", description="关联内容ID（context_id）")
    expires_in_hours: int = Field(72, ge=1, le=720, alias="expiresInHours", description="过期时间（小时）")

    model_config = {"populate_by_name": True}


@router.post("")
async def create_share(
    request: CreateShareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(SessionLocal),
):
    """创建分享链接"""
    # Verify content exists
    records = get_chat_group(db, request.content_id)
    if not records:
        raise HTTPException(status_code=404, detail="内容不存在")

    token = uuid.uuid4().hex
    expires_at = datetime.utcnow() + timedelta(hours=request.expires_in_hours)

    share = Share(
        user_id=current_user.id,
        type=request.type,
        content_id=request.content_id,
        token=token,
        expires_at=expires_at,
    )
    db.add(share)
    db.commit()
    db.refresh(share)

    return create_camel_response({
        "ok": True,
        "token": token,
        "shareUrl": f"/share/{token}",
        "expiresAt": expires_at.isoformat(),
    })


@router.get("/{token}")
async def get_share_content(token: str, db: Session = Depends(SessionLocal)):
    """访问分享内容（无需认证）"""
    share = db.query(Share).filter(Share.token == token).first()
    if not share:
        raise HTTPException(status_code=404, detail="分享不存在")

    # Check expiration
    if share.expires_at and datetime.utcnow() > share.expires_at.replace(tzinfo=None):
        raise HTTPException(status_code=410, detail="分享已过期")

    # Increment view count
    share.view_count = (share.view_count or 0) + 1
    db.commit()

    # Get content
    records = get_chat_group(db, share.content_id)
    if not records:
        raise HTTPException(status_code=404, detail="分享内容已被删除")

    content = ""
    image_url = None
    for r in records:
        if r.ai_reply:
            content += r.ai_reply + "\n\n"
        if r.image_url and not image_url:
            image_url = r.image_url

    return create_camel_response({
        "type": share.type,
        "title": records[0].title or "分享内容",
        "content": content.strip(),
        "imageUrl": image_url,
        "viewCount": share.view_count,
        "createdAt": share.created_at.isoformat() if share.created_at else "",
    })


@router.delete("/{token}")
async def cancel_share(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(SessionLocal),
):
    """取消分享（仅创建者）"""
    share = db.query(Share).filter(Share.token == token, Share.user_id == current_user.id).first()
    if not share:
        raise HTTPException(status_code=404, detail="分享不存在")
    db.delete(share)
    db.commit()
    return create_camel_response({"ok": True})


@router.get("/mine/all")
async def my_shares(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(SessionLocal),
):
    """获取我的分享列表"""
    shares = db.query(Share).filter(Share.user_id == current_user.id).order_by(Share.created_at.desc()).all()

    results = []
    for s in shares:
        results.append({
            "id": s.id,
            "token": s.token,
            "type": s.type,
            "contentId": s.content_id,
            "shareUrl": f"/share/{s.token}",
            "expiresAt": s.expires_at.isoformat() if s.expires_at else None,
            "viewCount": s.view_count,
            "isExpired": datetime.utcnow() > s.expires_at.replace(tzinfo=None) if s.expires_at else False,
            "createdAt": s.created_at.isoformat() if s.created_at else "",
        })
    return create_camel_response(results)