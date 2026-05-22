"""聊天记录模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.models.database import Base


class ChatHistory(Base):
    """聊天历史记录表"""
    __tablename__ = "chat_histories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=True, index=True, comment="用户 ID（预留）")
    context_id = Column(String(64), nullable=True, index=True, comment="会话分组ID，同一组表示同一轮对话")
    session_type = Column(String(20), nullable=True, default="chat", comment="会话类型：chat 或 image")
    image_url = Column(String(512), nullable=True, comment="生成的海报图片URL")
    image_ratio = Column(String(20), nullable=True, comment="图片比例，如 1:1, 16:9")
    title = Column(String(255), nullable=True, comment="聊天标题，取用户消息的前30个字")
    user_message = Column(Text, nullable=False, comment="用户发送的消息")
    ai_reply = Column(Text, nullable=False, comment="AI 的回复")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<ChatHistory {self.id}: {self.title}>"
