from sqlalchemy.orm import Session
from typing import List, Optional
from repositories.product_repository import ProductRepository
from schemas.product import ProductResponse, ProductCreate, ProductUpdate, ProductListResponse
from repositories.category_repository import CategoryRepository
from fastapi import HTTPException, status

class ProductService:
    def __init__(self, db: Session):
        self.repository = ProductRepository(db)
        self.category_repository = CategoryRepository(db)
    
    def get_all_products(self) -> ProductListResponse:
        products = self.repository.get_all()
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(products = products_response, total = len(products_response))
    
    def get_product_by_id(self, product_id: int) -> ProductResponse:
        product = self.repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )
        return ProductResponse.model_validate(product)
    
