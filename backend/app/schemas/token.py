from pydantic import BaseModel
from .user import UserResponse


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenWithUser(Token):
    user: UserResponse


class TokenData(BaseModel):
    user_id: int | None = None
