from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key= True, index= True)
    name = Column(String, nullable= False)
    description = Column(String)
    slug = Column(String, unique=True,nullable = False, index = True)
    price = Column(float, nullable= False, index = True)
    image_url = Column(String)
    created_at = Column(DateTime, default = datetime.utcnow)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable= False)
    category = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"<Product(id = {self.id}, name = '{self.name}', price = {self.price}, description = '{self.description}')>"