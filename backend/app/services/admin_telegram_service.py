from __future__ import annotations

from sqlalchemy.orm import Session

from ..config import settings
from ..models.users import User


class AdminTelegramService:
    def __init__(self, db: Session):
        self.db = db

    def sync_from_settings(self) -> None:
        admin = self.db.query(User).filter(User.login == settings.admin_login).first()
        if not admin:
            return

        updated = False

        username = settings.admin_telegram_username
        if username:
            normalized_username = username if username.startswith("@") else f"@{username}"
            if admin.telegram != normalized_username:
                admin.telegram = normalized_username
                updated = True

        telegram_id = settings.admin_telegram_id
        if telegram_id and admin.telegram_id != telegram_id:
            conflict_user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
            if not conflict_user or conflict_user.id == admin.id:
                admin.telegram_id = telegram_id
                updated = True

        if updated:
            self.db.commit()
            self.db.refresh(admin)
