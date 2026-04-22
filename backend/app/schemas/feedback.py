from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    order_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    order_id: int
    rating: int
    comment: Optional[str] = None
    sentiment: str
    is_public: bool
    needs_admin_attention: bool
    user_login: Optional[str] = None
    author_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
