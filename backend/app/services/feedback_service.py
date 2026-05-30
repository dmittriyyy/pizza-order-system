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
            is_public=True,
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

    def build_negative_feedback_summary(self, limit: int = 20) -> dict[str, str | int]:
        feedback_items = self.list_negative_feedback(limit=limit)
        if not feedback_items:
            return {
                "summary": "Негативных отзывов, требующих внимания, пока нет.",
                "negative_count": 0,
            }

        prepared = []
        for item in feedback_items:
            prepared.append(
                f"Заказ #{item.order_id}; оценка={item.rating}; комментарий={item.comment or 'без комментария'}"
            )

        prompt = (
            "Ты анализируешь только негативные отзывы клиентов пиццерии.\n"
            "Сделай короткую сводку для администратора на русском языке.\n"
            "Нужно ответить в 2-4 предложениях: что именно не так чаще всего, где повторяются проблемы, "
            "и что стоит проверить в первую очередь.\n"
            "Не используй markdown, заголовки и списки. Пиши компактно и по делу.\n\n"
            + "\n".join(prepared)
        )

        try:
            result = ollama_service.send_message(
                messages=[
                    {
                        "role": "system",
                        "content": "Ты аналитик клиентских отзывов для администратора доставки еды. Отвечай кратко и предметно по-русски.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            summary = (result.get("content") or "").strip()
            if summary:
                return {
                    "summary": summary,
                    "negative_count": len(feedback_items),
                }
        except Exception:
            pass

        with_comments = [item for item in feedback_items if item.comment]
        low_ratings = sum(1 for item in feedback_items if item.rating <= 2)
        fallback_summary = (
            f"Найдено {len(feedback_items)} негативных отзывов."
            f" Низкие оценки 1-2 поставили {low_ratings} раз."
            f" Комментарии оставили {len(with_comments)} клиентов."
            " Стоит в первую очередь проверить качество доставки, соответствие заказа и стабильность сервиса."
        )
        return {
            "summary": fallback_summary,
            "negative_count": len(feedback_items),
        }

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
