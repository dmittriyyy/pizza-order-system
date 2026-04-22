from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.feedback import Feedback
from ..models.order import OrderStatus
from ..schemas.feedback import FeedbackCreate
from .notification_service import NotificationService
from .ollama_service import ollama_service


class FeedbackService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)

    def create_feedback(self, user_id: int, payload: FeedbackCreate) -> Feedback:
        order = (
            self.db.query(Feedback)
            .filter(Feedback.order_id == payload.order_id)
            .first()
        )
        if order:
            return order

        from ..models.order import Order

        user_order = (
            self.db.query(Order)
            .filter(Order.id == payload.order_id, Order.user_id == user_id)
            .first()
        )
        if not user_order or user_order.status != OrderStatus.completed:
            raise ValueError("Отзыв можно оставить только по завершённому заказу")

        sentiment = self._analyze_with_llm(payload.rating, payload.comment or "")
        feedback = Feedback(
            user_id=user_id,
            order_id=payload.order_id,
            rating=payload.rating,
            comment=payload.comment,
            sentiment=sentiment,
            is_public=sentiment == "positive",
            needs_admin_attention=sentiment == "negative",
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)

        if feedback.needs_admin_attention:
            self.notification_service.notify_admins(
                title="Негативный отзыв по заказу",
                message=f"Заказ #{payload.order_id}: {payload.comment or 'Клиент поставил низкую оценку без комментария.'}",
                order_id=payload.order_id,
            )

        return feedback

    def list_public_feedback(self, limit: int = 20) -> list[Feedback]:
        return (
            self.db.query(Feedback)
            .filter(Feedback.is_public.is_(True))
            .order_by(Feedback.created_at.desc())
            .limit(limit)
            .all()
        )

    def list_user_feedback(self, user_id: int) -> list[Feedback]:
        return (
            self.db.query(Feedback)
            .filter(Feedback.user_id == user_id)
            .order_by(Feedback.created_at.desc())
            .all()
        )

    def list_negative_feedback(self, limit: int = 50) -> list[Feedback]:
        return (
            self.db.query(Feedback)
            .filter(Feedback.needs_admin_attention.is_(True))
            .order_by(Feedback.created_at.desc())
            .limit(limit)
            .all()
        )

    def _analyze_with_llm(self, rating: int, comment: str) -> str:
        prompt = (
            "Ты анализируешь отзыв клиента пиццерии.\n"
            "Нужно определить тональность: positive, neutral или negative.\n"
            "Учитывай и оценку, и текст комментария.\n"
            "Ответь строго одним словом из списка: positive, neutral, negative.\n\n"
            f"Оценка: {rating}\n"
            f"Комментарий: {comment or 'Комментарий не указан'}"
        )
        try:
            result = ollama_service.send_message(
                messages=[
                    {"role": "system", "content": "Ты сервис анализа отзывов. Отвечай строго одним словом: positive, neutral или negative."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )
            sentiment = (result.get("content") or "").strip().lower()
            if sentiment in {"positive", "neutral", "negative"}:
                return sentiment
        except Exception:
            pass

        if rating <= 2:
            return "negative"
        if rating >= 4:
            return "positive"
        return "neutral"
