from pydantic import BaseModel, Field

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=4, max_length=100, description="Category name")
    slug: str = Field(..., min_length=4, max_length=100, description="URL category name")
    
class CategoryCreate(CategoryBase):
    pass 

class CategoryResponse(CategoryBase):
    id: int = Field(...,description="Uniqie category identiffier")

    class Config:
        from_attributes = True