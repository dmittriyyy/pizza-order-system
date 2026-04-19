from pydantic import BaseModel, EmailStr
from typing import Optional
from ..models.users import UserRole


class UserBase(BaseModel):
    login: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.client


class UserLogin(BaseModel):
    login: str
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    telegram: Optional[str] = None
    telegram_id: Optional[str] = None
    default_address: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: UserRole
    phone: Optional[str] = None
    telegram: Optional[str] = None
    telegram_id: Optional[str] = None
    default_address: Optional[str] = None

    class Config:
        from_attributes = True
