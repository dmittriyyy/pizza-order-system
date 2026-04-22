from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timezone
from ..models.order import Order, OrderStatus
from ..models.users import User, UserRole
from ..repositories.order_repository import OrderRepository
from fastapi import HTTPException, status
from .notification_service import NotificationService


# допустимые переходов статусов
STATUS_TRANSITIONS = {
    OrderStatus.created: [OrderStatus.paid, OrderStatus.cooking, OrderStatus.cancelled],
    OrderStatus.paid: [OrderStatus.cooking, OrderStatus.cancelled],
    OrderStatus.cooking: [OrderStatus.ready],
    OrderStatus.ready: [OrderStatus.delivering, OrderStatus.completed],
    OrderStatus.delivering: [OrderStatus.completed, OrderStatus.cancelled],
    OrderStatus.completed: [],
    OrderStatus.cancelled: [],
}

# какие роли могут переходить в какие статусы
ROLE_STATUS_PERMISSIONS = {
    OrderStatus.paid: [UserRole.admin],
    OrderStatus.cooking: [UserRole.cook, UserRole.admin],
    OrderStatus.ready: [UserRole.cook, UserRole.admin],
    OrderStatus.delivering: [UserRole.courier, UserRole.admin],
    OrderStatus.completed: [UserRole.courier, UserRole.admin],
    OrderStatus.cancelled: [UserRole.admin, UserRole.client],
}


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = OrderRepository(db)
        self.notification_service = NotificationService(db)

    def get_user_orders(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        return self.repository.get_orders_by_user(user_id, skip, limit)

    def get_order(self, order_id: int) -> Optional[Order]:
        return self.repository.get_order_by_id(order_id)

    def get_all_orders(self, skip: int = 0, limit: int = 100) -> List[Order]:
        return self.repository.get_all_orders(skip, limit)

    def get_cook_orders(self, skip: int = 0, limit: int = 100) -> List[Order]:
        return self.repository.get_orders_for_cook(skip, limit)

    def get_courier_orders(self, skip: int = 0, limit: int = 100) -> List[Order]:
        return self.repository.get_orders_for_courier(skip, limit)

    def can_transition_status(self, current_status: OrderStatus, new_status: OrderStatus, 
                               user_role: UserRole) -> tuple[bool, str]:

        if new_status not in STATUS_TRANSITIONS.get(current_status, []):
            return False, f"Недопустимый переход из {current_status.value} в {new_status.value}"
        
        allowed_roles = ROLE_STATUS_PERMISSIONS.get(new_status, [])
        if user_role not in allowed_roles:
            return False, f"Недостаточно прав для перехода в {new_status.value}"
        
        return True, ""

    def update_order_status(self, order_id: int, new_status: OrderStatus, 
                            current_user: User) -> Order:

        order = self.repository.get_order_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заказ не найден"
            )
        
        user_role_str = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
        user_role = UserRole(user_role_str)
        
        can_transition, reason = self.can_transition_status(order.status, new_status, user_role)
        if not can_transition:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=reason
            )
        
        updated_order = self.repository.update_order_status(order, new_status)

        if new_status == OrderStatus.paid and not updated_order.paid_at:
            updated_order.paid_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(updated_order)

        self.notification_service.notify_order_status(
            updated_order,
            self._status_message(updated_order),
        )
        return updated_order

    def process_fake_payment(self, order: Order) -> Order:
        order.status = OrderStatus.paid
        order.paid_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(order)
        self.notification_service.notify_order_status(
            order,
            f"Заказ #{order.id} успешно оплачен в тестовом режиме и передан в обработку.",
        )
        return order

    def _status_message(self, order: Order) -> str:
        messages = {
            OrderStatus.paid: f"Заказ #{order.id} оплачен и передан на кухню.",
            OrderStatus.cooking: f"Заказ #{order.id} уже готовится.",
            OrderStatus.ready: f"Заказ #{order.id} готов и ждёт курьера.",
            OrderStatus.delivering: f"Заказ #{order.id} передан курьеру.",
            OrderStatus.completed: f"Заказ #{order.id} доставлен. Будем рады отзыву.",
            OrderStatus.cancelled: f"Заказ #{order.id} отменён.",
        }
        return messages.get(order.status, f"Статус заказа #{order.id} обновлён: {order.status.value}")

    def get_order_stats(self) -> Dict:
        stats = {}
        for s in OrderStatus:
            count = len(self.repository.get_orders_by_status(s))
            stats[s.value] = count
        return stats
