from fastapi import APIRouter, Depends
from ..models.users import User
from ..schemas.user import UserResponse
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user
