"""配置模块"""
import os
from functools import lru_cache


class Settings:
    """应用设置"""
    APP_NAME: str = "AI报表生成平台"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # MySQL 数据库配置
    DB_HOST: str = "mysql5.sqlpub.com"
    DB_PORT: int = 3310
    DB_USERNAME: str = "sunsun"
    DB_PASSWORD: str = "CIFfWtTYEXMzeGNU"
    DB_DATABASE: str = "nest_test"
    
    @property
    def DATABASE_URL(self) -> str:
        """获取数据库连接 URL"""
        return f"mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"
    
    REDIS_URL: str = "redis://redis:6379/0"
    
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "ai-report-files"
    
    SHANGTANG_API_KEY: str = ""
    SHANGTANG_PROMPT_MODEL: str = "shangtang-model-a"
    SHANGTANG_IMAGE_MODEL: str = "shangtang-model-b"
    
    # 书生大模型 API 配置
    SENSENOVA_API_KEY: str = "sk-8JEVTH1zNypwQqa9z9fghTfJ2coqpceD"
    SENSENOVA_PROMPT_MODEL: str = "sensenova-6.7-flash-lite"
    SENSENOVA_API_BASE: str = "https://token.sensenova.cn/v1"
    
    # SenseNova U1 Fast 图像生成模型
    SENSENOVA_U1_MODEL: str = "sensenova-u1-fast"
    SENSENOVA_U1_API_BASE: str = "https://token.sensenova.cn/v1"
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: str = "xlsx,xls,csv"
    
    def __init__(self):
        """从环境变量读取配置"""
        self.CORS_ORIGINS = os.getenv("CORS_ORIGINS", self.CORS_ORIGINS)
        self.DB_HOST = os.getenv("DB_HOST", self.DB_HOST)
        self.DB_PORT = int(os.getenv("DB_PORT", self.DB_PORT))
        self.DB_USERNAME = os.getenv("DB_USERNAME", self.DB_USERNAME)
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", self.DB_PASSWORD)
        self.DB_DATABASE = os.getenv("DB_DATABASE", self.DB_DATABASE)


@lru_cache()
def get_settings() -> Settings:
    """获取单例的配置"""
    return Settings()
