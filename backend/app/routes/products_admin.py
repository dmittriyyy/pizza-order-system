import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..config import settings
from ..schemas.product import ProductUpdate, ProductResponse
from ..models.products import Product
from ..models.users import User
from ..dependencies import get_current_admin_user

router = APIRouter(prefix="/api/products", tags=["Products Management"])

# для изображений
UPLOAD_DIR = os.path.join("static", "images", "products")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  

os.makedirs(UPLOAD_DIR, exist_ok=True)


def validate_file(file: UploadFile):
    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый формат. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    return ext


@router.post("/{product_id}/images")
def upload_product_image( product_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Продукт не найден"
        )
    
    ext = validate_file(file)
    
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as buffer:
        buffer.write(file.file.read())
    
    image_url = f"/static/images/products/{filename}"
    product.image_url = image_url
    db.commit()
    db.refresh(product)
    
    return {
        "message": "Изображение загружено",
        "image_url": image_url,
        "product": ProductResponse.model_validate(product)
    }


@router.delete("/images/{filename}")
def delete_product_image(filename: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Изображение не найдено"
        )
    
    image_url = f"/static/images/products/{filename}"
    product = db.query(Product).filter(Product.image_url == image_url).first()
    
    if product:
        product.image_url = None
        db.commit()
    
    os.remove(filepath)
    
    return {"message": "Изображение удалено"}


@router.patch("/{product_id}")
def update_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Продукт не найден"
        )
    
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value) # setattr(объект, имя_поля, значение)
    
    db.commit()
    db.refresh(product)
    
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}")
def delete_product( product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Продукт не найден"
        )
    
    db.delete(product)
    db.commit()
    
    return {"message": "Продукт удалён"}
