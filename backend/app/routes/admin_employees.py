from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database import get_db
from ..models.users import User, UserRole, UserStatus
from ..schemas.user import UserResponse, UserUpdate
from ..dependencies import get_current_admin_user

router = APIRouter(prefix="/api/admin", tags=["Admin Management"])


class ExistingEmployeeAssignRequest(BaseModel):
    query: str
    role: UserRole


@router.get("/employees", response_model=List[UserResponse])
def get_all_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    employees = db.query(User).filter(User.role != UserRole.client).all()
    return employees


@router.patch("/employees/{user_id}", response_model=UserResponse)
def update_employee(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    employee = db.query(User).filter(User.id == user_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)
    
    db.commit()
    db.refresh(employee)
    return employee


@router.delete("/employees/{user_id}")
def delete_employee(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    employee = db.query(User).filter(User.id == user_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    if employee.id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя удалить самого себя")
    
    db.delete(employee)
    db.commit()
    return {"message": "Сотрудник удалён"}


@router.post("/employees", response_model=UserResponse)
def create_employee(
    employee_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    existing = db.query(User).filter(
        (User.login == employee_data.login) | (User.email == employee_data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь с таким логином или email уже существует")
    
    from ..services.auth_service import get_password_hash
    
    new_employee = User(
        login=employee_data.login,
        email=employee_data.email,
        first_name=employee_data.first_name,
        last_name=employee_data.last_name,
        password_hash=get_password_hash("temp_password_123"),
        role=employee_data.role or UserRole.client,
        phone=employee_data.phone,
        telegram=employee_data.telegram,
    )
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee


@router.post("/employees/assign-existing", response_model=UserResponse)
def assign_existing_employee(
    payload: ExistingEmployeeAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    lookup = payload.query.strip()
    if not lookup:
        raise HTTPException(status_code=400, detail="Укажите логин, email или Telegram пользователя")

    normalized = lookup.lstrip("@").lower()
    telegram_value = f"@{normalized}"

    employee = db.query(User).filter(
        (func.lower(User.login) == normalized) |
        (func.lower(func.coalesce(User.email, "")) == normalized) |
        (func.lower(func.coalesce(User.telegram, "")) == telegram_value) |
        (func.coalesce(User.telegram_id, "") == lookup)
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    employee.role = payload.role
    if employee.status != UserStatus.active:
        employee.status = UserStatus.active

    db.commit()
    db.refresh(employee)
    return employee
