from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..services.cart_service import CartService
from ..schemas.cart import CartResponse
from ..models.users import User
from ..dependencies import get_current_user

router = APIRouter(
    prefix="/api/cart",
    tags=["cart"]
)


class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int = 1


class UpdateCartRequest(BaseModel):
    quantity: int


@router.get("", response_model=CartResponse, status_code=status.HTTP_200_OK)
def get_cart( db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = CartService(db)
    return service.get_user_cart(current_user.id)


@router.post("/add", response_model=CartResponse, status_code=status.HTTP_200_OK)
def add_to_cart( request: AddToCartRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = CartService(db)
    return service.add_to_cart(
        user_id=current_user.id,
        product_id=request.product_id,
        quantity=request.quantity
    )


@router.put("/update/{product_id}", response_model=CartResponse, status_code=status.HTTP_200_OK)
def update_cart( product_id: int, request: UpdateCartRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = CartService(db)
    return service.update_cart_item(
        user_id=current_user.id,
        product_id=product_id,
        quantity=request.quantity
    )


@router.delete("/remove/{product_id}", response_model=CartResponse, status_code=status.HTTP_200_OK)
def remove_from_cart( product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = CartService(db)
    return service.remove_from_cart(
        user_id=current_user.id,
        product_id=product_id
    )


@router.delete("/clear", status_code=status.HTTP_200_OK)
def clear_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = CartService(db)
    return service.clear_cart(user_id=current_user.id)