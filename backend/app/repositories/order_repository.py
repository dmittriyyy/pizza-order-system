from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..models.order import Order, OrderStatus
from ..models.orderItem import OrderItem
from ..models.users import User


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_orders(self, skip: int = 0, limit: int = 100) -> List[Order]:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_orders_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(Order.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(Order.id == order_id)
            .first()
        )

    def get_orders_by_status(self, status: OrderStatus, skip: int = 0, limit: int = 100) -> List[Order]:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(Order.status == status)
            .order_by(Order.created_at.desc()) 
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_orders_for_cook(self, skip: int = 0, limit: int = 100) -> List[Order]:
        relevant_statuses = [
            OrderStatus.created,
            OrderStatus.paid,
            OrderStatus.cooking,
        ]
        return (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(Order.status.in_(relevant_statuses))
            .order_by(Order.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_orders_for_courier(self, skip: int = 0, limit: int = 100) -> List[Order]:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(Order.status == OrderStatus.ready)
            .order_by(Order.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_orders_for_courier_delivering(self, courier_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(
                Order.status == OrderStatus.delivering,
                Order.user_id == courier_id 
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_order_status(self, order: Order, new_status: OrderStatus) -> Order:
        order.status = new_status
        self.db.commit()
        self.db.refresh(order)
        return order

    def create_order(self, user_id: int, total_price: float, delivery_address: str,
                     payment_method: str, items: list, 
                     delivery_comment: str = None, delivery_time: str = None,
                     delivery_lat: float = None, delivery_lng: float = None,
                     customer_phone: str = None, customer_name: str = None,
                     order_comment: str = None) -> Order:
        new_order = Order(
            user_id=user_id,
            total_price=total_price,
            delivery_address=delivery_address,
            delivery_comment=delivery_comment,
            delivery_time=delivery_time,
            delivery_lat=delivery_lat,
            delivery_lng=delivery_lng,
            customer_phone=customer_phone,
            customer_name=customer_name,
            order_comment=order_comment,
            payment_method=payment_method,
            status=OrderStatus.created
        )
        self.db.add(new_order)
        self.db.flush()

        for item in items:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price_at_time_of_order=item['price'],
                comment=item.get('comment'),
                special_requests=item.get('special_requests')
            )
            self.db.add(order_item)

        self.db.commit()
        self.db.refresh(new_order)
        return new_order
