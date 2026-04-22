from __future__ import annotations

import os
from typing import Iterable, Optional

import requests
from sqlalchemy.orm import Session

from ..models.notification import Notification
from ..models.order import Order
from ..models.users import User, UserRole


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.telegram_token = os.getenv("TG_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")

    def create_in_app(
        self,
        user_id: int,
        title: str,
        message: str,
        kind: str = "info",
        order_id: Optional[int] = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            kind=kind,
            channel="in_app",
            order_id=order_id,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def list_for_user(self, user_id: int, unread_only: bool = False, limit: int = 50) -> list[Notification]:
        query = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        if unread_only:
            query = query.filter(Notification.is_read.is_(False))
        return query.limit(limit).all()

    def mark_all_read(self, user_id: int) -> int:
        updated = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read.is_(False))
            .update({"is_read": True}, synchronize_session=False)
        )
        self.db.commit()
        return updated

    def notify_order_status(self, order: Order, message: str) -> None:
        self.create_in_app(
            user_id=order.user_id,
            title="Статус заказа обновлён",
            message=message,
            kind="order_status",
            order_id=order.id,
        )
        self._send_telegram_to_user(order.user, message)

    def notify_admins(self, title: str, message: str, order_id: Optional[int] = None) -> None:
        admins = self.db.query(User).filter(User.role == UserRole.admin).all()
        for admin in admins:
            self.create_in_app(
                user_id=admin.id,
                title=title,
                message=message,
                kind="admin_alert",
                order_id=order_id,
            )
            self._send_telegram_to_user(admin, f"{title}\n{message}")

    def _send_telegram_to_user(self, user: Optional[User], message: str) -> None:
        if not user or not user.telegram_id or not self.telegram_token:
            return

        try:
            requests.post(
                f"https://api.telegram.org/bot{self.telegram_token}/sendMessage",
                json={
                    "chat_id": user.telegram_id,
                    "text": message,
                },
                timeout=10,
            )
        except Exception:
            # Уведомления в Telegram не должны ломать основной сценарий заказа
            pass
