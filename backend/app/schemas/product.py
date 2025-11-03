from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .category import CategoryResponse

class ProductBase(BaseModel):
    name:str = Field(...,min_length=1, max_length=200,description="Product name")
    description : Optional[str] = Field(None,description="Product description")
    price: float = Field(...,gt=0,description="Product price")
    category_id: int = Field(...,description="Category ID")
    image_url: Optional[str] = Field(None, description="Product image URL")
    slug: str = Field(..., min_length=4, max_length=100, description="URL product name")

class ProductCreate(ProductBase):
    pass

class ProductResponse(BaseModel):
    id: int = Field(...,description="Uniqie product ID")
    name: str
    description: Optional[str]
    price: float
    category_id: int 
    image_url: Optional[str]
    created_ad: datetime
    category: CategoryResponse = Field(...,description="Product category")

    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    products:list[ProductResponse]
    total: int = Field(...,description="Total number of response")