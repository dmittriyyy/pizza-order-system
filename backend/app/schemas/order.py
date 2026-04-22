from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from ..models.order import OrderStatus, PaymentMethod

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1
    comment: Optional[str] = None 

class OrderCreate(BaseModel):
    delivery_address: str
    payment_method: PaymentMethod
    simulate_payment: bool = True
    
    delivery_comment: Optional[str] = None  
    delivery_time: Optional[str] = None 
    
    # Яндекс Карты
    delivery_lat: Optional[float] = None  # широта
    delivery_lng: Optional[float] = None  # долгота
    
    customer_phone: Optional[str] = None  
    customer_name: Optional[str] = None  
    order_comment: Optional[str] = None 

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
    comment: Optional[str] = None
    special_requests: Optional[str] = None
    subtotal: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    status: OrderStatus
    total_price: float
    delivery_address: str
    delivery_comment: Optional[str] = None
    delivery_time: Optional[str] = None
    delivery_lat: Optional[float] = None
    delivery_lng: Optional[float] = None
    customer_phone: Optional[str] = None
    customer_name: Optional[str] = None
    payment_method: PaymentMethod
    order_comment: Optional[str] = None
    created_at: datetime
    picked_up_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True
