import hashlib
import hmac
import json
import secrets
from datetime import datetime, timezone
from urllib.parse import parse_qsl

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..config import settings
from ..models.users import User, UserRole, UserStatus
from .auth_service import get_password_hash


class TelegramAuthService:
    def __init__(self, db: Session):
        self.db = db

    def _secret_key(self) -> bytes:
        if not settings.telegram_bot_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Telegram auth is not configured",
            )
        return hmac.new(
            b"WebAppData",
            settings.telegram_bot_token.encode("utf-8"),
            hashlib.sha256,
        ).digest()

    def verify_init_data(self, init_data: str) -> dict:
        parsed = dict(parse_qsl(init_data, keep_blank_values=True))
        received_hash = parsed.pop("hash", None)
        if not received_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Telegram hash",
            )

        data_check_string = "\n".join(
            f"{key}={value}" for key, value in sorted(parsed.items(), key=lambda item: item[0])
        )
        calculated_hash = hmac.new(
            self._secret_key(),
            data_check_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(calculated_hash, received_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Telegram signature",
            )

        auth_date_raw = parsed.get("auth_date")
        if auth_date_raw:
            auth_date = datetime.fromtimestamp(int(auth_date_raw), tz=timezone.utc)
            age = (datetime.now(timezone.utc) - auth_date).total_seconds()
            if age > settings.telegram_auth_max_age_seconds:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Telegram auth data expired",
                )

        user_json = parsed.get("user")
        if not user_json:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Telegram user payload",
            )
        return json.loads(user_json)

    def get_or_create_user(
        self,
        telegram_id: int | str,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        telegram_id = str(telegram_id)
        user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            updated = False
            if username and user.telegram != f"@{username}":
                user.telegram = f"@{username}"
                updated = True
            if first_name and not user.first_name:
                user.first_name = first_name
                updated = True
            if last_name and not user.last_name:
                user.last_name = last_name
                updated = True
            if updated:
                self.db.commit()
                self.db.refresh(user)
            return user

        base_login = f"tg_{telegram_id}"
        login = base_login
        suffix = 1
        while self.db.query(User).filter(User.login == login).first():
            suffix += 1
            login = f"{base_login}_{suffix}"

        user = User(
            login=login,
            password_hash=get_password_hash(secrets.token_urlsafe(24)),
            first_name=first_name,
            last_name=last_name,
            telegram=f"@{username}" if username else None,
            telegram_id=telegram_id,
            role=UserRole.client,
            status=UserStatus.active,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
