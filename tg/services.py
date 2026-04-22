from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy.orm import joinedload

from .bootstrap import BACKEND_DIR 

from app.database import SessionLocal
from app.models import Cart, CartItem, Order, Product, User
from app.repositories.cart_repository import CartRepository
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.services.order_tracking_service import OrderTrackingService
from app.services.recommendation_service import RecommendationService
from app.services.telegram_auth_service import TelegramAuthService
from app.schemas.user import UserCreate


@dataclass
class MenuItem:
    id: int
    name: str
    price: float
    category: str


class TelegramPizzaService:
    def get_linked_user(self, telegram_user_id: int) -> User | None:
        db = SessionLocal()
        try:
            return db.query(User).filter(User.telegram_id == str(telegram_user_id)).first()
        finally:
            db.close()

    def is_linked(self, telegram_user_id: int) -> bool:
        return self.get_linked_user(telegram_user_id) is not None

    def link_existing_account(
        self,
        telegram_user_id: int,
        login: str,
        password: str,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> str:
        db = SessionLocal()
        try:
            telegram_id = str(telegram_user_id)
            auth_service = AuthService(db)
            user = auth_service.authenticate(login, password)

            existing_link = db.query(User).filter(User.telegram_id == telegram_id).first()
            if existing_link and existing_link.id != user.id:
                return (
                    "Этот Telegram уже привязан к другому аккаунту.\n"
                    "Если нужно перепривязать, сначала очистим старую связь вручную."
                )

            if user.telegram_id and user.telegram_id != telegram_id:
                return "Этот аккаунт уже привязан к другому Telegram."

            user.telegram_id = telegram_id
            user.telegram = f"@{username}" if username else user.telegram
            if first_name and not user.first_name:
                user.first_name = first_name
            if last_name and not user.last_name:
                user.last_name = last_name
            db.commit()
            db.refresh(user)

            return (
                f"Аккаунт привязан.\n"
                f"Теперь бот работает как пользователь {user.login}."
            )
        finally:
            db.close()

    def unlink_account(self, telegram_user_id: int) -> str:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == str(telegram_user_id)).first()
            if not user:
                return "Этот Telegram сейчас не привязан ни к одному аккаунту."

            user.telegram_id = None
            db.commit()
            return f"Привязка снята с аккаунта {user.login}. Теперь можно выполнить /link заново."
        finally:
            db.close()

    def register_account(
        self,
        telegram_user_id: int,
        login: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
        username: str | None = None,
    ) -> str:
        db = SessionLocal()
        try:
            if db.query(User).filter(User.telegram_id == str(telegram_user_id)).first():
                return "Этот Telegram уже привязан. Если хочешь другой аккаунт, сначала выполни /unlink."

            auth_service = AuthService(db)
            user = auth_service.register(
                UserCreate(
                    login=login,
                    email=None,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                )
            )
            user.telegram_id = str(telegram_user_id)
            user.telegram = f"@{username}" if username else None
            db.commit()
            db.refresh(user)
            return f"Регистрация завершена. Аккаунт {user.login} создан и привязан к Telegram."
        finally:
            db.close()

    def require_link_message(self) -> str:
        return (
            "Сначала привяжи аккаунт командой /link.\n"
            "Бот попросит логин и пароль от твоего аккаунта Piazza Pizza, "
            "после этого сохранит Telegram ID и будет понимать, кто делает заказ."
        )

    def _session_id(self, telegram_user_id: int) -> str:
        return f"tg_{telegram_user_id}"

    def _legacy_session_cart_user_id(self, telegram_user_id: int) -> int:
        return hash(self._session_id(telegram_user_id)) % 1_000_000

    def _get_or_create_user_id(self, telegram_user_id: int, username: str | None, first_name: str | None, last_name: str | None) -> int:
        db = SessionLocal()
        try:
            linked_user = db.query(User).filter(User.telegram_id == str(telegram_user_id)).first()
            if linked_user:
                return linked_user.id

            auth_service = TelegramAuthService(db)
            user = auth_service.get_or_create_user(
                telegram_id=telegram_user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            self._migrate_legacy_session_cart(db, telegram_user_id, user.id)
            return user.id
        finally:
            db.close()

    def _migrate_legacy_session_cart(self, db, telegram_user_id: int, user_id: int) -> None:
        legacy_user_id = self._legacy_session_cart_user_id(telegram_user_id)
        if legacy_user_id == user_id:
            return

        legacy_cart = (
            db.query(Cart)
            .options(joinedload(Cart.items))
            .filter(Cart.user_id == legacy_user_id)
            .first()
        )
        if not legacy_cart or not legacy_cart.items:
            return

        cart_repo = CartRepository(db)
        user_cart = cart_repo.get_or_create_cart(user_id)

        for item in legacy_cart.items:
            existing_item = (
                db.query(CartItem)
                .filter(
                    CartItem.cart_id == user_cart.id,
                    CartItem.product_id == item.product_id,
                    CartItem.comment == item.comment,
                )
                .first()
            )
            if existing_item:
                existing_item.quantity += item.quantity
            else:
                db.add(
                    CartItem(
                        cart_id=user_cart.id,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        comment=item.comment,
                    )
                )

        db.query(CartItem).filter(CartItem.cart_id == legacy_cart.id).delete()
        db.delete(legacy_cart)
        db.commit()

    def get_menu_preview(self, limit: int = 8) -> list[MenuItem]:
        db = SessionLocal()
        try:
            products = (
                db.query(Product)
                .filter(Product.is_available == 1)
                .order_by(Product.id.asc())
                .limit(limit)
                .all()
            )
            return [
                MenuItem(
                    id=product.id,
                    name=product.name,
                    price=product.price,
                    category=product.category.name if product.category else "Другое",
                )
                for product in products
            ]
        finally:
            db.close()

    def render_menu_preview(self, limit: int = 8) -> str:
        items = self.get_menu_preview(limit=limit)
        if not items:
            return "Меню пока пустое."

        lines = ["Вот несколько позиций из меню:"]
        for item in items:
            lines.append(f"• {item.name} ({item.category}) — {item.price:.0f} ₽")

        lines.append("")
        lines.append("Полное меню и заказ доступны в Mini App.")
        lines.append("В чате можешь писать свободно: например, «посоветуй острую пиццу» или «добавь пепперони»")
        return "\n".join(lines)

    def chat(self, telegram_user_id: int, text: str, username: str | None = None, first_name: str | None = None, last_name: str | None = None) -> str:
        db = SessionLocal()
        try:
            user_id = self._get_or_create_user_id(telegram_user_id, username, first_name, last_name)
            session_id = self._session_id(telegram_user_id)
            chat_service = ChatService(db)
            history = chat_service.get_user_history(user_id=user_id, session_id=session_id, limit=20)
            context = [{"message": item.message, "response": item.response} for item in history]

            response = chat_service.generate_response(
                message=text,
                context=context,
                user_id=user_id,
                session_id=session_id,
            )
            chat_service.add_message(
                user_id=user_id,
                session_id=session_id,
                message=text,
                response=response,
            )
            return response
        finally:
            db.close()

    def get_cart_text(self, telegram_user_id: int, username: str | None = None, first_name: str | None = None, last_name: str | None = None) -> str:
        db = SessionLocal()
        try:
            user_id = self._get_or_create_user_id(telegram_user_id, username, first_name, last_name)
            cart = (
                db.query(Cart)
                .options(joinedload(Cart.items).joinedload(CartItem.product))
                .filter(Cart.user_id == user_id)
                .first()
            )
            if not cart or not cart.items:
                return "Корзина пока пустая."

            total = 0.0
            lines = ["Текущая корзина:"]
            for item in cart.items:
                subtotal = item.product.price * item.quantity
                total += subtotal
                comment = f" [{item.comment}]" if item.comment else ""
                lines.append(
                    f"• {item.product.name} x{item.quantity} — {subtotal:.0f} ₽{comment}"
                )

            lines.append("")
            lines.append(f"Итого: {total:.0f} ₽")
            lines.append("Оформление заказа пока делай через Mini App.")
            return "\n".join(lines)
        finally:
            db.close()

    def clear_cart(self, telegram_user_id: int, username: str | None = None, first_name: str | None = None, last_name: str | None = None) -> str:
        db = SessionLocal()
        try:
            user_id = self._get_or_create_user_id(telegram_user_id, username, first_name, last_name)
            cart = (
                db.query(Cart)
                .options(joinedload(Cart.items))
                .filter(Cart.user_id == user_id)
                .first()
            )
            if not cart or not cart.items:
                return "Корзина уже пустая."

            for item in list(cart.items):
                db.delete(item)
            db.commit()
            return "Корзина очищена."
        finally:
            db.close()

    def get_latest_order_status(self, telegram_user_id: int, username: str | None = None, first_name: str | None = None, last_name: str | None = None) -> str:
        db = SessionLocal()
        try:
            user_id = self._get_or_create_user_id(telegram_user_id, username, first_name, last_name)
            order = (
                db.query(Order)
                .filter(Order.user_id == user_id)
                .order_by(Order.created_at.desc())
                .first()
            )
            if not order:
                return "У тебя пока нет оформленных заказов."

            tracking_service = OrderTrackingService(db)
            tracking = tracking_service.build_status_response(order)
            return (
                f"Заказ #{tracking['order_id']}\n"
                f"Статус: {tracking['status']}\n"
                f"{tracking['message']}"
            )
        finally:
            db.close()

    def get_recommendations_text(self, telegram_user_id: int, username: str | None = None, first_name: str | None = None, last_name: str | None = None) -> str:
        db = SessionLocal()
        try:
            user_id = self._get_or_create_user_id(telegram_user_id, username, first_name, last_name)
            recommendation_service = RecommendationService(db)
            message, suggestions = recommendation_service.build_for_user(user_id)
            if not suggestions:
                return message

            lines = [message, "", "Могу предложить:"]
            for suggestion in suggestions[:3]:
                lines.append(f"• {suggestion['name']} — {suggestion['reason']}")
            return "\n".join(lines)
        finally:
            db.close()
