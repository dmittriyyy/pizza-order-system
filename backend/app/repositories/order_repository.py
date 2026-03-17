from sqlalchemy.orm import Session
from ..models.order import Order
from ..models.orderItem import OrderItem
from ..models.products import Product

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_order_from_cart(self, user_id: int, address: str, payment_method: str, cart_items: list):
        total = sum(item.product.price * item.quantity for item in cart_items) if cart_items else 0

        new_order = Order(
            user_id = user_id,
            total_price = total,
            delivery_address = address,
            payment_method = payment_method
        )
        self.db.add(new_order)
        self.db.flush()  # id заказа до коммита

        for cart_item in cart_items:
            order_item = OrderItem(
                order_id = new_order.id,
                product_id = cart_item.product_id,
                quantity = cart_item.quantity,
                price_at_time_of_order = cart_item.product.price,
                special_requests=getattr(cart_item, 'comment', None)
            )
            self.db.add(order_item)

        self.db.commit()
        self.db.refresh(new_order)
        return new_order

        