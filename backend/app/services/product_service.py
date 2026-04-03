from sqlalchemy.orm import Session
from typing import List, Optional
from ..repositories.product_repository import ProductRepository
from ..repositories.category_repository import CategoryRepository
from ..schemas.product import ProductResponse, ProductCreate, ProductUpdate, ProductListResponse
from fastapi import HTTPException, status

class ProductService:
    def __init__(self, db: Session):
        self.repository = ProductRepository(db)
        self.category_repository = CategoryRepository(db)

    def get_all_products(self) -> ProductListResponse:
        products = self.repository.get_all()
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(products=products_response, total=len(products_response))

    def get_product_by_id(self, product_id: int) -> ProductResponse:
        product = self.repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Товар с id {product_id} не найден"
            )
        return ProductResponse.model_validate(product)

    def get_product_by_category(self, category_id: int) -> ProductListResponse:
        category = self.category_repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категория с id {category_id} не найдена"
            )
        products = self.repository.get_by_category_id(category_id)
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(products=products_response, total=len(products_response))

    def create_product(self, product_data: ProductCreate) -> ProductResponse:
        category = self.category_repository.get_by_id(product_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категория с id {product_data.category_id} не найдена"
            )
        new_product = self.repository.create(product_data)
        return ProductResponse.model_validate(new_product)

    def update_product(self, product_id: int, product_data: ProductUpdate) -> ProductResponse:
        product = self.repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Товар с id {product_id} не найден"
            )
        
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        self.repository.db.commit()
        self.repository.db.refresh(product)
        return ProductResponse.model_validate(product)

    def delete_product(self, product_id: int) -> None:
        product = self.repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Товар с id {product_id} не найден"
            )
        self.repository.db.delete(product)
        self.repository.db.commit()
