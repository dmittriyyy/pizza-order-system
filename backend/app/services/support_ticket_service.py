from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.support_ticket import SupportTicket
from ..models.users import User
from .notification_service import NotificationService


class SupportTicketService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)

    def create_ticket(
        self,
        user: User,
        user_message: str,
        agent_response: str,
        source: str = "app",
    ) -> SupportTicket:
        ticket = SupportTicket(
            user_id=user.id,
            source=source,
            status="open",
            user_message=user_message,
            agent_response=agent_response,
        )
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        title = f"Новый тикет поддержки #{ticket.id}"
        message = (
            f"Клиент: {user.login}\n"
            f"Источник: {source}\n"
            f"Вопрос: {user_message}\n"
            f"AI: {agent_response}\n\n"
            f"Ответить: /reply_ticket {ticket.id} <текст>"
        )
        self.notification_service.notify_admins(title=title, message=message)
        return ticket

    def list_open_tickets(self, limit: int = 10) -> list[SupportTicket]:
        return (
            self.db.query(SupportTicket)
            .order_by(SupportTicket.created_at.desc())
            .limit(limit)
            .all()
        )

    def reply_to_ticket(self, ticket_id: int, message: str) -> SupportTicket | None:
        ticket = self.db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            return None

        ticket.status = "answered"
        ticket.admin_response = message
        ticket.answered_at = func.now()
        self.db.commit()
        self.db.refresh(ticket)

        self.notification_service.notify_support_reply(ticket.user, ticket.id, message)
        return ticket
