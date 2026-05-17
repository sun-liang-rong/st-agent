"""报表历史记录模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.database import Base


class ReportHistory(Base):
    """报表生成历史记录表"""
    __tablename__ = "report_histories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    file_id = Column(String(64), nullable=False, comment="上传文件 ID")
    file_name = Column(String(255), nullable=False, comment="原始文件名")
    user_prompt = Column(Text, nullable=False, comment="用户分析需求")
    generated_prompt = Column(Text, nullable=True, comment="AI 生成的提示词")
    image_url = Column(String(1024), nullable=True, comment="生成的图片 URL")
    status = Column(String(20), nullable=False, default="completed", comment="状态: completed/failed")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<ReportHistory {self.id} ({self.file_name})>"
