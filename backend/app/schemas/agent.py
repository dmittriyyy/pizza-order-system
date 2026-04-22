from typing import List, Optional

from pydantic import BaseModel


class AgentSuggestion(BaseModel):
    product_id: int
    name: str
    reason: str


class ConsultantResponse(BaseModel):
    response: str


class TrackingResponse(BaseModel):
    order_id: int
    status: str
    message: str
    latest_notification: Optional[str] = None


class RecommendationResponse(BaseModel):
    message: str
    suggestions: List[AgentSuggestion]
