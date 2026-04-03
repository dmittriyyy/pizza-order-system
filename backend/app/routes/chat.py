from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
import uuid
from ..database import get_db
from ..models.users import User
from ..dependencies import get_current_user, get_current_user_optional
from ..services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    message: str
    response: str
    timestamp: str


class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]


@router.post("/send", response_model=ChatMessageResponse)
def send_message(
    request: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    session_id = request.session_id or f"anon_{uuid.uuid4()}"

    chat_service = ChatService(db)
    history = chat_service.get_user_history(user_id, session_id, limit=20)

    context = [{"message": h.message, "response": h.response} for h in history]

    response_text = chat_service.generate_response(
        message=request.message,
        context=context,
        user_id=user_id,
        session_id=session_id
    )

    chat_service.add_message(
        user_id=user_id,
        session_id=session_id,
        message=request.message,
        response=response_text
    )

    return {
        "message": request.message,
        "response": response_text,
        "timestamp": "now"
    }


@router.get("/history", response_model=ChatHistoryResponse)
def get_chat_history(
    session_id: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    session_id = session_id or f"anon_{uuid.uuid4()}"

    chat_service = ChatService(db)
    history = chat_service.get_user_history(user_id, session_id, limit)

    return {
        "messages": [
            {
                "message": h.message,
                "response": h.response,
                "timestamp": h.created_at.isoformat()
            }
            for h in history
        ]
    }


@router.delete("/clear")
def clear_chat_history(
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    session_id = session_id or f"anon_{uuid.uuid4()}"

    chat_service = ChatService(db)
    count = chat_service.clear_history(user_id, session_id)

    return {"message": f"Удалено {count} сообщений"}
