from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy.orm import joinedload

from .bootstrap import BACKEND_DIR 

from app.database import SessionLocal
from app.models import Cart, CartItem, Product
from app.repositories.cart_repository import CartRepository
from app.services.chat_service import ChatService
from app.services.telegram_auth_service import TelegramAuthService


@dataclass
class MenuItem:
    id: int
    name: str
    price: float
    category: str


class TelegramPizzaService:
    def _session_id(self, telegram_user_id: int) -> str:
        return f"tg_{telegram_user_id}"

    def _legacy_session_cart_user_id(self, telegram_user_id: int) -> int:
        return hash(self._session_id(telegram_user_id)) % 1_000_000

    def _get_or_create_user_id(self, telegram_user_id: int, username: str | None, first_name: str | None, last_name: str | None) -> int:
        db = SessionLocal()
        try:
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
