from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from ..database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # NULL для анонимов
    session_id = Column(String, nullable=True)  # для анонимных пользователей
    
    message = Column(Text, nullable=False)  # вопрос пользователя
    response = Column(Text, nullable=False)  # ответ бота
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связь с пользователем (если авторизован)
    user = relationship("User", backref="chat_messages")
