from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from ..database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True, unique=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    sentiment = Column(String, nullable=False, default="neutral", index=True)
    is_public = Column(Boolean, nullable=False, default=False)
    needs_admin_attention = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User")
    order = relationship("Order")
