from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from ..models.order import OrderStatus, PaymentMethod

class OrderCreate(BaseModel):
    delivery_address: str
    payment_method: PaymentMethod

class ProductInOrder(BaseModel):
    id: int
    name: str
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class OrderItemResponse(BaseModel):
    product_id: int
    product: Optional[ProductInOrder] = None
    quantity: int
    price_at_time_of_order: float
    special_requests: Optional[str]
    subtotal: float 

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    status: OrderStatus
    total_price: float
    delivery_address: str
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True