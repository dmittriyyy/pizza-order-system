from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.user import UserUpdate, UserResponse
from ..models.users import User
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("/me", response_model=UserResponse)
def get_current_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_data = user_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user
