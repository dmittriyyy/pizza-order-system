from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, func, Float
from sqlalchemy.orm import relationship
from ..database import Base

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False, default=1)
    price_at_time_of_order = Column(Float, nullable=False)
    special_requests = Column(String, nullable=True)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")