"""图片收藏模型"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.database import Base


class ImageFavorite(Base):
    """图片收藏表"""
    __tablename__ = "image_favorites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(String(512), nullable=False, comment="图片 URL")
    prompt = Column(String(1000), nullable=True, comment="原始提示词")
    style = Column(String(50), nullable=True, comment="图片风格")
    ratio = Column(String(20), nullable=True, comment="图片比例")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<ImageFavorite {self.id}: {self.image_url[:50]}>"