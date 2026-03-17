from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    slug = Column(String, unique=True, nullable=False)
    price = Column(Float, nullable=False, index=True)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    calories = Column(Integer, default=0)
    protein = Column(Float, default=0)     
    fat = Column(Float, default=0)         
    carbohydrates = Column(Float, default=0) 
    weight = Column(Integer, default=0)   
    
    ingredients = Column(JSON, default=list)  
    
    is_available = Column(Integer, default=1) 
    discount = Column(Float, default=0)  

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"