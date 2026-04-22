from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from ..schemas.order import OrderCreate, OrderResponse
from ..repositories.order_repository import OrderRepository
from ..repositories.cart_repository import CartRepository
from ..models.order import OrderStatus, Order
from ..models.orderItem import OrderItem
from ..models.users import User, UserRole
from ..services.order_service import OrderService
from ..dependencies import (
    get_current_user, 
    get_current_admin_user,
    require_cook, 
    require_courier,
    require_admin
)

router = APIRouter(prefix="/api/orders", tags=["Orders"])

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_repo = CartRepository(db)
    cart = cart_repo.get_cart_by_user_id(current_user.id)

    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя создать заказ с пустой корзиной"
        )

    items = [
        {
            'product_id': item.product_id,
            'quantity': item.quantity,
            'price': item.product.price,
            'comment': item.comment,
            'special_requests': None
        }
        for item in cart.items
    ]

    repo = OrderRepository(db)
    service = OrderService(db)
    try:
        new_order = repo.create_order(
            user_id=current_user.id,
            total_price=cart.total if hasattr(cart, 'total') else sum(i.product.price * i.quantity for i in cart.items),
            delivery_address=order_data.delivery_address,
            delivery_comment=order_data.delivery_comment,
            delivery_time=order_data.delivery_time,
            delivery_lat=order_data.delivery_lat,
            delivery_lng=order_data.delivery_lng,
            customer_phone=order_data.customer_phone or current_user.login,
            customer_name=order_data.customer_name or f"{current_user.first_name or ''} {current_user.last_name or ''}".strip(),
            order_comment=order_data.order_comment,
            payment_method=order_data.payment_method.value if hasattr(order_data.payment_method, 'value') else order_data.payment_method,
            items=items
        )
        if order_data.simulate_payment:
            new_order = service.process_fake_payment(new_order)
        cart_repo.clear_cart(cart)
        return new_order
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при создании заказа")


@router.get("", response_model=List[OrderResponse])
def get_user_orders(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = OrderService(db)
    orders = service.get_user_orders(current_user.id, skip, limit)
    
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = OrderService(db)
    order = service.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    user_role = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
    if order.user_id != current_user.id and user_role != UserRole.admin.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён"
        )
    
    return order


@router.get("/cook/pending", response_model=List[OrderResponse], dependencies=[Depends(require_cook)])
def get_cook_orders(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_cook)
):
    service = OrderService(db)
    orders = service.get_cook_orders(skip, limit)
    
    return orders


@router.patch("/{order_id}/status/start-cooking", response_model=OrderResponse, dependencies=[Depends(require_cook)])
def start_cooking_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_cook)
):
    service = OrderService(db)
    order = service.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    return service.update_order_status(order_id, OrderStatus.cooking, current_user)


@router.patch("/{order_id}/status/ready", response_model=OrderResponse, dependencies=[Depends(require_cook)])
def complete_cooking_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_cook)
):
    service = OrderService(db)
    order = service.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    return service.update_order_status(order_id, OrderStatus.ready, current_user)



@router.get("/courier/ready", response_model=List[OrderResponse], dependencies=[Depends(require_courier)])
def get_ready_orders(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_courier)
):
    service = OrderService(db)
    orders = service.get_courier_orders(skip, limit)
    
    return orders


@router.patch("/{order_id}/status/delivering", response_model=OrderResponse, dependencies=[Depends(require_courier)])
def start_delivery_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_courier)
):
    service = OrderService(db)
    order = service.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    updated_order = service.update_order_status(order_id, OrderStatus.delivering, current_user)

    from datetime import datetime, timezone
    updated_order.picked_up_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(updated_order)

    return updated_order


@router.patch("/{order_id}/status/completed", response_model=OrderResponse, dependencies=[Depends(require_courier)])
def complete_delivery_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_courier)
):
    service = OrderService(db)
    order = service.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    return service.update_order_status(order_id, OrderStatus.completed, current_user)


@router.get("/admin/all", response_model=List[OrderResponse], dependencies=[Depends(require_admin)])
def get_all_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    service = OrderService(db)
    orders = service.get_all_orders(skip, limit)
    
    return orders


@router.patch("/{order_id}/status", response_model=OrderResponse, dependencies=[Depends(require_admin)])
def admin_update_order_status(
    order_id: int,
    new_status: OrderStatus = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    service = OrderService(db)
    return service.update_order_status(order_id, new_status, current_user)
