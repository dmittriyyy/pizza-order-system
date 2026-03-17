from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from ..schemas.order import OrderCreate, OrderResponse
from ..repositories.order_repository import OrderRepository
from ..repositories.cart_repository import CartRepository
from ..models.order import OrderStatus, Order
from ..models.orderItem import OrderItem
from ..models.users import User
from ..dependencies import get_current_user, get_current_admin_user

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart_repo = CartRepository(db)
    cart = cart_repo.get_cart_by_user_id(current_user.id)

    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя создать заказ с пустой корзиной"
        )

    repo = OrderRepository(db)
    try:
        new_order = repo.create_order_from_cart(
            user_id=current_user.id,
            address=order_data.delivery_address,
            payment_method=order_data.payment_method.value if hasattr(order_data.payment_method, 'value') else order_data.payment_method,
            cart_items=cart.items
        )
        cart_repo.clear_cart(cart)
        return new_order
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при создании заказа")


@router.get("", response_model=List[OrderResponse])
def get_user_orders( skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product)
    ).filter(
        Order.user_id == current_user.id
    ).order_by(
        Order.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    for order in orders:
        for item in order.items:
            item.subtotal = item.price_at_time_of_order * item.quantity
    
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order( order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    if order.user_id != current_user.id:
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
        if user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещён"
            )
    
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status( order_id: int, new_status: OrderStatus, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    order.status = new_status
    db.commit()
    db.refresh(order)
    return order