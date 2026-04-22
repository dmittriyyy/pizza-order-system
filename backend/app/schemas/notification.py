from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    kind: str
    channel: str
    is_read: bool
    order_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
