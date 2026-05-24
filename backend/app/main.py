"""FastAPI 主应用"""
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os
import subprocess

from app.config import get_settings
from app.api import router as api_router


settings = get_settings()

# ── 日志配置 ──
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.DEBUG if settings.APP_DEBUG else logging.INFO,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

# 设置第三方库的日志级别，避免过多干扰
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)

logger = logging.getLogger("app")

# 确保上传和生成目录存在
os.makedirs("uploads", exist_ok=True)
os.makedirs("generated", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时执行 Alembic 迁移"""
    logger.info("🚀 应用启动中...")
    try:
        import sys
        alembic_cmd = [sys.executable, "-m", "alembic", "upgrade", "head"]
        result = subprocess.run(
            alembic_cmd,
            capture_output=True, text=True, cwd=os.path.dirname(__file__) or ".",
        )
        if result.returncode == 0:
            logger.info("✅ Alembic 迁移完成")
        else:
            logger.warning("⚠️ Alembic 迁移警告: %s", result.stderr)
    except Exception as e:
        logger.warning("⚠️ Alembic 迁移失败: %s", e)
    yield
    logger.info("👋 应用关闭")


# 挂载静态文件目录（生成的图片可通过 /generated/xxx.png 访问）
app = FastAPI(
    title=settings.APP_NAME,
    description="AI 旅游攻略与图片生成平台后端 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.mount("/generated", StaticFiles(directory="generated"), name="generated")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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
        "message": "AI 旅游攻略与图片生成平台 API",
        "version": "1.0.0",
        "docs": "/docs",
    }