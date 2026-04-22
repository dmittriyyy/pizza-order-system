from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.notification import Notification
from ..models.order import Order, OrderStatus
from .ollama_service import ollama_service


TRACKING_MESSAGES = {
    OrderStatus.created: "Заказ принят и ожидает подтверждения оплаты.",
    OrderStatus.paid: "Оплата подтверждена, заказ передан на кухню.",
    OrderStatus.cooking: "Заказ уже готовится на кухне.",
    OrderStatus.ready: "Заказ приготовлен и ждёт курьера.",
    OrderStatus.delivering: "Курьер уже в пути.",
    OrderStatus.completed: "Заказ доставлен. Можно оставить отзыв.",
    OrderStatus.cancelled: "Заказ отменён.",
}


class OrderTrackingService:
    def __init__(self, db: Session):
        self.db = db

    def build_status_response(self, order: Order) -> dict:
        latest = (
            self.db.query(Notification)
            .filter(Notification.user_id == order.user_id, Notification.order_id == order.id)
            .order_by(Notification.created_at.desc())
            .first()
        )
        return {
            "order_id": order.id,
            "status": order.status.value,
            "message": self._status_message(order),
            "latest_notification": latest.message if latest else None,
        }

    def _status_message(self, order: Order) -> str:
        base_message = TRACKING_MESSAGES.get(order.status, "Статус заказа обновлён.")
        prompt = (
            "Ты агент сопровождения заказа в пиццерии.\n"
            "Сформулируй короткое дружелюбное сообщение на русском о статусе заказа.\n"
            "Не придумывай фактов, используй только переданные данные.\n"
            "1-2 предложения.\n\n"
            f"Заказ: #{order.id}\n"
            f"Статус: {order.status.value}\n"
            f"Базовое описание: {base_message}\n"
            f"Адрес: {order.delivery_address}\n"
            f"Имя клиента: {order.customer_name or order.user.login if order.user else 'клиент'}"
        )
        try:
            result = ollama_service.send_message(
                messages=[
                    {"role": "system", "content": "Ты AI-агент сопровождения заказа. Пиши коротко, понятно и без выдумок."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            content = (result.get("content") or "").strip()
            if content:
                return content
        except Exception:
            pass
        return base_message
