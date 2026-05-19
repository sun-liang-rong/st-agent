"""FastAPI 主应用"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import os

from app.config import get_settings
from app.api import router as api_router
from app.models import Base, engine


settings = get_settings()

# 确保上传和生成目录存在
os.makedirs("uploads", exist_ok=True)


# 创建数据库表
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.APP_NAME,
    description="AI 智能报表生成平台后端 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置 CORS
origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(api_router, prefix="/api/v1", tags=["api"])



# 健康检查
@app.get("/health", tags=["health"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
    }


@app.get("/", tags=["root"])
async def root():
    """根路径"""
    return {
        "message": "AI 报表生成平台 API",
        "version": "1.0.0",
        "docs": "/docs",
    }
