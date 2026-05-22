"""API routes."""
from fastapi import APIRouter
from app.api import upload, generate, task, history, auth, sse, chat, travel, image

router = APIRouter()

router.include_router(auth.router)
router.include_router(upload.router)
router.include_router(generate.router)
router.include_router(task.router)
router.include_router(history.router)
router.include_router(sse.router)
router.include_router(chat.router)
router.include_router(travel.router)
router.include_router(image.router)
