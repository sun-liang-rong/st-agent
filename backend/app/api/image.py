"""图片生成 API + 图片收藏"""
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.image_favorite import ImageFavorite
from app.models.user import User
from app.services.ai_service import AIService
from app.services.chat_history_service import save_chat
from app.utils.common import create_camel_response
from app.utils.security import get_current_user

router = APIRouter(prefix="/image", tags=["图片生成"])


# ─── 图片生成 ────────────────────────────────────────────────────


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


# ─── 图片收藏 ────────────────────────────────────────────────────


class FavoriteRequest(BaseModel):
    image_url: str = Field(..., alias="imageUrl", description="图片 URL")
    prompt: str | None = Field(None, description="原始提示词")
    style: str | None = Field(None, description="图片风格")
    ratio: str | None = Field(None, description="图片比例")

    model_config = {"populate_by_name": True}


@router.get("/favorites")
async def list_favorites(
    limit: int = 20, offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(SessionLocal),
):
    """获取收藏列表"""
    records = (
        db.query(ImageFavorite)
        .filter(ImageFavorite.user_id == current_user.id)
        .order_by(ImageFavorite.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    total = db.query(ImageFavorite).filter(ImageFavorite.user_id == current_user.id).count()

    results = []
    for r in records:
        results.append({
            "id": r.id,
            "imageUrl": r.image_url,
            "prompt": r.prompt,
            "style": r.style,
            "ratio": r.ratio,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        })
    return create_camel_response({"data": results, "total": total})


@router.post("/favorites")
async def add_favorite(
    request: FavoriteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(SessionLocal),
):
    """添加收藏"""
    # Check duplicate
    existing = db.query(ImageFavorite).filter(
        ImageFavorite.user_id == current_user.id,
        ImageFavorite.image_url == request.image_url,
    ).first()
    if existing:
        return create_camel_response({"ok": True, "id": existing.id, "message": "已收藏"})

    favorite = ImageFavorite(
        user_id=current_user.id,
        image_url=request.image_url,
        prompt=request.prompt,
        style=request.style,
        ratio=request.ratio,
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return create_camel_response({"ok": True, "id": favorite.id})


@router.delete("/favorites/{favorite_id}")
async def remove_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(SessionLocal),
):
    """取消收藏"""
    favorite = db.query(ImageFavorite).filter(
        ImageFavorite.id == favorite_id,
        ImageFavorite.user_id == current_user.id,
    ).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="收藏不存在")
    db.delete(favorite)
    db.commit()
    return create_camel_response({"ok": True})