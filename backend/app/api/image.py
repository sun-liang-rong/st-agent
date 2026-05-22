"""Image generation API."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models import get_db
from app.services.ai_service import aiservice
from app.services.chat_history_service import save_chat
from app.utils.common import create_camel_response

router = APIRouter(prefix="/image", tags=["image"])


class ImageRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    contextId: str | None = None


@router.post("/generate")
async def generate_image(request: ImageRequest, db: Session = Depends(get_db)):
    context_id = request.contextId or f"image-{uuid.uuid4().hex}"

    image_path = await aiservice.generate_travel_image(
        destination=request.prompt,
        preferences="",
        itinerary=request.prompt,
    )

    if not image_path:
        raise HTTPException(status_code=500, detail="图片生成失败")

    image_url = "/" + image_path.replace("\\", "/")
    ai_reply = f"![AI生成图片]({image_url})"
    save_chat(
        db=db,
        user_message=request.prompt,
        ai_reply=ai_reply,
        context_id=context_id,
    )

    return create_camel_response({"imageUrl": image_url, "contextId": context_id})
