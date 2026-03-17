from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .category import CategoryResponse

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Название продукта")
    description: Optional[str] = Field(None, description="Описание продукта")
    price: float = Field(..., gt=0, description="Цена продукта")
    category_id: int = Field(..., description="ID категории")
    image_url: Optional[str] = Field(None, description="URL изображения")
    slug: str = Field(..., min_length=4, max_length=100, description="URL продукта")
    calories: Optional[int] = Field(0, description="Калории (ккал на 100г)")
    protein: Optional[float] = Field(0, description="Белки (г на 100г)")
    fat: Optional[float] = Field(0, description="Жиры (г на 100г)")
    carbohydrates: Optional[float] = Field(0, description="Углеводы (г на 100г)")
    weight: Optional[int] = Field(0, description="Вес порции (г)")
    ingredients: Optional[List[str]] = Field(default_factory=list, description="Состав ингредиентов")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbohydrates: Optional[float] = None
    weight: Optional[int] = None
    ingredients: Optional[List[str]] = None
    is_available: Optional[bool] = None
    discount: Optional[float] = Field(None, ge=0, le=100)

class ProductResponse(BaseModel):
    id: int = Field(..., description="Уникальный ID продукта")
    name: str
    description: Optional[str]
    price: float
    category_id: int
    image_url: Optional[str]
    created_at: datetime
    category: CategoryResponse = Field(..., description="Категория продукта")
    calories: int = 0
    protein: float = 0
    fat: float = 0
    carbohydrates: float = 0
    weight: int = 0
    ingredients: List[str] = []
    is_available: bool = True
    discount: float = 0

    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int = Field(..., description="Общее количество продуктов")