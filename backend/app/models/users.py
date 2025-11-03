import re
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from ..database import Base


class UserRole(PyEnum):
    client = "client"
    admin = "admin"
    cook = "cook"
    courier = "courier"


class UserStatus(PyEnum):
    active = "active"
    not_active = "not_active"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    login = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    email = Column(String,nullable=True,unique=True) 
    role = Column(Enum(UserRole), nullable=False, index=True)
    status = Column(Enum(UserStatus), default=UserStatus.active, nullable=True)

    registered_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, login='{self.login}', role='{self.role.value}', status='{self.status.value}')>"
