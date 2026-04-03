from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, func, Float
from sqlalchemy.orm import relationship
from ..database import Base
from enum import Enum as PyEnum

class OrderStatus(PyEnum):
    created = "created"
    paid = "paid"
    cooking = "cooking"
    ready = "ready"  # Готов к доставке
    delivering = "delivering"
    completed = "completed"
    cancelled = "cancelled"

class PaymentMethod(PyEnum):
    credit_card = "credit_card"
    sbp = "sbp"
    cash_on_delivery = "cash_on_delivery"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.created, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # доставка
    delivery_address = Column(String, nullable=False)
    delivery_comment = Column(String, nullable=True) 
    delivery_time = Column(String, nullable=True) 
    
    # Яндекс Карты
    delivery_lat = Column(Float, nullable=True)  # широта
    delivery_lng = Column(Float, nullable=True)  # долгота
    
    # время для курьера
    picked_up_at = Column(DateTime(timezone=True), nullable=True)
    
    # контактные данные
    customer_phone = Column(String, nullable=True)  # телефон клиента
    customer_name = Column(String, nullable=True)  # имя получателя
    
    # оплата
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    
    # комментарии
    order_comment = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    user = relationship("User", back_populates="orders")