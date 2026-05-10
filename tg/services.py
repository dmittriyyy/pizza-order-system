from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy.orm import joinedload

from .bootstrap import BACKEND_DIR 

from app.database import SessionLocal
from app.models import Cart, CartItem, Feedback, Order, Product, User
from app.models.order import OrderStatus
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.services.feedback_service import FeedbackService
from app.services.ollama_service import ollama_service
from app.services.order_service import OrderService
from app.services.order_tracking_service import OrderTrackingService
from app.services.recommendation_service import RecommendationService
from app.services.telegram_auth_service import TelegramAuthService
from app.schemas.feedback import FeedbackCreate
from app.schemas.user import UserCreate


@dataclass
class MenuItem:
    id: int
    name: str
    price: float
    category: str


@dataclass
class CheckoutContext:
    user_id: int
    total: float
    customer_name: str
    customer_phone: str
    default_address: str | None


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
            lines.append("Оформить заказ можно командой /checkout или через Mini App.")
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

    def has_cart_items(self, telegram_user_id: int, username: str | None = None, first_name: str | None = None, last_name: str | None = None) -> bool:
        db = SessionLocal()
        try:
            user_id = self._get_or_create_user_id(telegram_user_id, username, first_name, last_name)
            cart = (
                db.query(Cart)
                .options(joinedload(Cart.items))
                .filter(Cart.user_id == user_id)
                .first()
            )
            return bool(cart and cart.items)
        finally:
            db.close()

    def get_checkout_context(self, telegram_user_id: int, username: str | None = None, first_name: str | None = None, last_name: str | None = None) -> CheckoutContext | None:
        db = SessionLocal()
        try:
            user_id = self._get_or_create_user_id(telegram_user_id, username, first_name, last_name)
            user = db.query(User).filter(User.id == user_id).first()
            cart = (
                db.query(Cart)
                .options(joinedload(Cart.items).joinedload(CartItem.product))
                .filter(Cart.user_id == user_id)
                .first()
            )
            if not user or not cart or not cart.items:
                return None

            total = sum(item.product.price * item.quantity for item in cart.items)
            customer_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.login
            customer_phone = user.phone or ""
            return CheckoutContext(
                user_id=user_id,
                total=total,
                customer_name=customer_name,
                customer_phone=customer_phone,
                default_address=user.default_address,
            )
        finally:
            db.close()

    def create_order_from_cart(
        self,
        telegram_user_id: int,
        delivery_address: str,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> str:
        db = SessionLocal()
        try:
            user_id = self._get_or_create_user_id(telegram_user_id, username, first_name, last_name)
            user = db.query(User).filter(User.id == user_id).first()
            cart = (
                db.query(Cart)
                .options(joinedload(Cart.items).joinedload(CartItem.product))
                .filter(Cart.user_id == user_id)
                .first()
            )
            if not user or not cart or not cart.items:
                return "Корзина пуста. Сначала добавь товары."

            items = [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": item.product.price,
                    "comment": item.comment,
                    "special_requests": None,
                }
                for item in cart.items
            ]

            repo = OrderRepository(db)
            order_service = OrderService(db)
            new_order = repo.create_order(
                user_id=user.id,
                total_price=sum(item["price"] * item["quantity"] for item in items),
                delivery_address=delivery_address,
                delivery_comment=None,
                delivery_time=None,
                delivery_lat=None,
                delivery_lng=None,
                customer_phone=user.phone or user.login,
                customer_name=f"{user.first_name or ''} {user.last_name or ''}".strip() or user.login,
                order_comment="Оформлено через Telegram-бота",
                payment_method="credit_card",
                items=items,
            )
            new_order = order_service.process_fake_payment(new_order)
            cart_repo = CartRepository(db)
            cart_repo.clear_cart(cart)
            return (
                f"Заказ #{new_order.id} оплачен и передан в обработку.\n"
                f"Адрес: {delivery_address}\n"
                f"Статус: {new_order.status.value}"
            )
        except Exception:
            db.rollback()
            return "Не удалось оформить заказ. Попробуй ещё раз через пару секунд."
        finally:
            db.close()

    def get_latest_completed_order_for_review(
        self,
        telegram_user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> Order | None:
        db = SessionLocal()
        try:
            user_id = self._get_or_create_user_id(telegram_user_id, username, first_name, last_name)
            reviewed_order_ids = {
                order_id
                for (order_id,) in db.query(Feedback.order_id).filter(Feedback.user_id == user_id).all()
            }
            return (
                db.query(Order)
                .filter(
                    Order.user_id == user_id,
                    Order.status == OrderStatus.completed,
                    ~Order.id.in_(reviewed_order_ids) if reviewed_order_ids else True,
                )
                .order_by(Order.created_at.desc())
                .first()
            )
        finally:
            db.close()

    def create_feedback_for_order(
        self,
        telegram_user_id: int,
        order_id: int,
        rating: int,
        comment: str | None,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> str:
        db = SessionLocal()
        try:
            user_id = self._get_or_create_user_id(telegram_user_id, username, first_name, last_name)
            service = FeedbackService(db)
            feedback = service.create_feedback(
                user_id,
                FeedbackCreate(
                    order_id=order_id,
                    rating=rating,
                    comment=None if not comment or comment == "-" else comment,
                ),
            )
            visibility = "Отзыв опубликован на сайте." if feedback.is_public else "Отзыв сохранён."
            if feedback.needs_admin_attention:
                visibility += " Администратор увидит его в отдельной сводке."
            return f"Спасибо за отзыв к заказу #{order_id}. {visibility}"
        except ValueError as error:
            return str(error)
        finally:
            db.close()

    def get_admin_feedback_digest(self, telegram_user_id: int, limit: int = 12) -> str:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == str(telegram_user_id)).first()
            if not user or getattr(user.role, "value", user.role) != "admin":
                return "Эта команда доступна только администратору."

            feedback_items = (
                db.query(Feedback)
                .options(joinedload(Feedback.user))
                .order_by(Feedback.created_at.desc())
                .limit(limit)
                .all()
            )
            if not feedback_items:
                return "Пока нет отзывов для сводки."

            prepared = []
            positive = neutral = negative = 0
            for item in feedback_items:
                if item.sentiment == "positive":
                    positive += 1
                elif item.sentiment == "negative":
                    negative += 1
                else:
                    neutral += 1
                author = item.user.login if item.user else "Пользователь"
                prepared.append(
                    f"Заказ #{item.order_id}; автор={author}; оценка={item.rating}; sentiment={item.sentiment}; комментарий={item.comment or 'без комментария'}"
                )

            digest_lines = [
                f"Последние отзывы: {len(feedback_items)}",
                f"Позитивных: {positive}",
                f"Нейтральных: {neutral}",
                f"Негативных: {negative}",
                "",
                "Краткая AI-сводка:",
            ]

            prompt = (
                "Ты помощник администратора пиццерии. "
                "По последним отзывам сделай короткую сводку на русском: что клиентам нравится, "
                "что не нравится, какие 2-3 действия стоит предпринять. Пиши без markdown, компактно.\n\n"
                + "\n".join(prepared)
            )
            try:
                result = ollama_service.send_message(
                    messages=[
                        {"role": "system", "content": "Ты аналитик отзывов для администратора доставки еды. Отвечай по-русски кратко и предметно."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )
                digest_lines.append((result.get("content") or "").strip() or "Не удалось построить AI-сводку.")
            except Exception:
                digest_lines.append("AI-сводка временно недоступна.")

            digest_lines.append("")
            digest_lines.append("Последние отзывы:")
            for item in feedback_items[:5]:
                author = item.user.login if item.user else "Пользователь"
                digest_lines.append(
                    f"• Заказ #{item.order_id}, {author}, {item.rating}/5: {item.comment or 'без комментария'}"
                )
            return "\n".join(digest_lines)
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
                f"{tracking['message']}\n\n"
                f"Если заказ уже завершён, можешь оставить отзыв командой /review."
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
