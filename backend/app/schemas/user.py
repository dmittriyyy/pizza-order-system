from pydantic import BaseModel, EmailStr
from typing import Optional
from ..models.users import UserRole


class UserBase(BaseModel):
    login: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.client


class UserLogin(BaseModel):
    login: str
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole

    class Config:
        from_attributes = True
