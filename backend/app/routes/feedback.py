from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user, require_admin
from ..models.users import User
from ..schemas.feedback import FeedbackCreate, FeedbackResponse
from ..services.feedback_service import FeedbackService


router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


def _author_name(user: User | None) -> str | None:
    if not user:
        return None
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    return full_name or user.login


@router.get("/public", response_model=list[FeedbackResponse])
def list_public_feedback(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    service = FeedbackService(db)
    feedback = service.list_public_feedback(limit=limit)
    return [
        {
            **FeedbackResponse.model_validate(item).model_dump(),
            "user_login": item.user.login if item.user else None,
            "author_name": _author_name(item.user),
        }
        for item in feedback
    ]


@router.get("/my", response_model=list[FeedbackResponse])
def list_my_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FeedbackService(db)
    feedback = service.list_user_feedback(current_user.id)
    return [
        {
            **FeedbackResponse.model_validate(item).model_dump(),
            "user_login": current_user.login,
            "author_name": _author_name(current_user),
        }
        for item in feedback
    ]


@router.get("/admin/problematic", response_model=list[FeedbackResponse], dependencies=[Depends(require_admin)])
def list_problematic_feedback(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = FeedbackService(db)
    feedback = service.list_negative_feedback(limit=limit)
    return [
        {
            **FeedbackResponse.model_validate(item).model_dump(),
            "user_login": item.user.login if item.user else None,
            "author_name": _author_name(item.user),
        }
        for item in feedback
    ]


@router.post("", response_model=FeedbackResponse)
def create_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FeedbackService(db)
    try:
        return service.create_feedback(current_user.id, payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
