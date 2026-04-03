from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..services.product_service import ProductService
from ..schemas.product import ProductListResponse, ProductResponse, ProductCreate, ProductUpdate
from ..models.users import User
from ..dependencies import get_current_admin_user

router = APIRouter(
    prefix="/api/products",
    tags=["products"]
)

@router.get("", response_model = ProductListResponse, status_code=status.HTTP_200_OK)
def get_products(db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_all_products()

@router.get("/{product_id}", response_model = ProductResponse, status_code=status.HTTP_200_OK)
def get_product(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_product_by_id(product_id)

@router.get("/category/{category_id}", response_model = ProductListResponse, status_code=status.HTTP_200_OK)
def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_product_by_category(category_id)

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_current_admin_user)])
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.create_product(product_data)

@router.patch("/{product_id}", response_model=ProductResponse,
              dependencies=[Depends(get_current_admin_user)])
def update_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.update_product(product_id, product_data)

@router.delete("/{product_id}", status_code=status.HTTP_200_OK,
               dependencies=[Depends(get_current_admin_user)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    service.delete_product(product_id)
    return {"message": "Товар удалён"}