"""API 路由注册"""
from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.image import router as image_router
from app.api.travel import router as travel_router
from app.api.share import router as share_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(chat_router)
router.include_router(image_router)
router.include_router(travel_router)
router.include_router(share_router)