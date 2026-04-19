from datetime import timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..schemas.token import TokenWithUser
from ..services.auth_service import create_access_token
from ..services.telegram_auth_service import TelegramAuthService


router = APIRouter(prefix="/api/auth", tags=["Auth"])


class TelegramAuthRequest(BaseModel):
    init_data: str


@router.post("/telegram", response_model=TokenWithUser)
def telegram_auth(
    request: TelegramAuthRequest,
    db: Session = Depends(get_db),
):
    service = TelegramAuthService(db)
    telegram_user = service.verify_init_data(request.init_data)
    user = service.get_or_create_user(
        telegram_id=telegram_user["id"],
        username=telegram_user.get("username"),
        first_name=telegram_user.get("first_name"),
        last_name=telegram_user.get("last_name"),
    )

    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user}
