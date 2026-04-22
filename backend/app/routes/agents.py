from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models.order import Order
from ..models.users import User
from ..schemas.agent import ConsultantResponse, RecommendationResponse, TrackingResponse
from ..services.chat_service import ChatService
from ..services.order_tracking_service import OrderTrackingService
from ..services.recommendation_service import RecommendationService


router = APIRouter(prefix="/api/agents", tags=["Agents"])


@router.post("/consultant", response_model=ConsultantResponse)
def consultant_agent(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = (payload or {}).get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Сообщение пустое")

    chat_service = ChatService(db)
    history = chat_service.get_user_history(user_id=current_user.id, limit=10)
    context = [{"message": item.message, "response": item.response} for item in history]
    response = chat_service.generate_response(
        message=message,
        context=context,
        user_id=current_user.id,
        session_id=f"agent_{current_user.id}",
    )
    chat_service.add_message(
        user_id=current_user.id,
        session_id=f"agent_{current_user.id}",
        message=message,
        response=response,
    )
    return {"response": response}


@router.get("/tracking/{order_id}", response_model=TrackingResponse)
def tracking_agent(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    service = OrderTrackingService(db)
    return service.build_status_response(order)


@router.get("/recommendations", response_model=RecommendationResponse)
def recommendation_agent(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RecommendationService(db)
    message, suggestions = service.build_for_user(current_user.id)
    return {"message": message, "suggestions": suggestions}
