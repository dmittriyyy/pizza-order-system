from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from ..database import Base


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    source = Column(String, nullable=False, default="app", index=True)
    status = Column(String, nullable=False, default="open", index=True)
    user_message = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=True)
    admin_response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    answered_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")
