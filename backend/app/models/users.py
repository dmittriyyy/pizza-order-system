from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class User(BaseModel):
    id: int = Field(description="ID пользователя")
    first_name: str = Field(description="Имя")
    last_name: str = Field(description="Фамилия")
    login: str = Field(description="Логин")
    password_hash: str = Field(description="Хэш пароля")
    role: Literal["client", "admin", "cook", "courier"] = Field(description="Роль")
    registered_at: datetime = Field(description="Дата регистрации")
    status: Literal["active", "blocked"] = Field(default="active", description="Статус")
