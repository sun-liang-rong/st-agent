"""分享模型"""
import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.database import Base


def generate_share_token():
    return uuid.uuid4().hex


class Share(Base):
    """分享表"""
    __tablename__ = "shares"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(20), nullable=False, comment="分享类型：travel 或 image")
    content_id = Column(String(64), nullable=False, comment="关联内容ID（context_id）")
    token = Column(String(64), unique=True, nullable=False, default=generate_share_token, comment="分享令牌")
    expires_at = Column(DateTime(timezone=True), nullable=True, comment="过期时间，NULL 表示永不过期")
    view_count = Column(Integer, default=0, nullable=False, comment="浏览次数")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<Share {self.token} ({self.type})>"