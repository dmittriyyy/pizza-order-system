from sqlalchemy.orm import Session
from ..repositories.cart_repository import CartRepository
from ..repositories.product_repository import ProductRepository
from ..schemas.cart import CartResponse, CartItemCreate, CartItemUpdate, CartItem
from fastapi import HTTPException, status


class CartService:
    def __init__(self, db: Session):
        self.db = db
        self.cart_repository = CartRepository(db)
        self.product_repository = ProductRepository(db)

    def get_user_cart(self, user_id: int) -> CartResponse:
        cart = self.cart_repository.get_cart_by_user_id(user_id)
        
        if not cart or not cart.items:
            return CartResponse(items=[], total=0.0, items_count=0)
        
        cart_items = []
        total_price = 0.0
        total_items = 0
        
        for item in cart.items:
            subtotal = item.product.price * item.quantity
            cart_item = CartItem(
                product_id=item.product.id,
                name=item.product.name,
                price=item.product.price,
                quantity=item.quantity,
                subtotal=subtotal,
                image_url=item.product.image_url
            )
            cart_items.append(cart_item)
            total_price += subtotal
            total_items += item.quantity
        
        return CartResponse(
            items=cart_items,
            total=round(total_price, 2),
            items_count=total_items
        )

    def add_to_cart(self, user_id: int, product_id: int, quantity: int) -> CartResponse:
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Товар с id {product_id} не найден"
            )
        
        cart = self.cart_repository.get_or_create_cart(user_id)
        self.cart_repository.add_item(cart, product_id, quantity)
        
        return self.get_user_cart(user_id)

    def update_cart_item(self, user_id: int, product_id: int, quantity: int) -> CartResponse:
        cart = self.cart_repository.get_cart_by_user_id(user_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Корзина не найдена"
            )
        
        self.cart_repository.update_item(cart, product_id, quantity)
        return self.get_user_cart(user_id)

    def remove_from_cart(self, user_id: int, product_id: int) -> CartResponse:
        cart = self.cart_repository.get_cart_by_user_id(user_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Корзина не найдена"
            )
        
        self.cart_repository.remove_item(cart, product_id)
        return self.get_user_cart(user_id)

    def clear_cart(self, user_id: int) -> dict:
        cart = self.cart_repository.get_cart_by_user_id(user_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Корзина не найдена"
            )
        
        self.cart_repository.clear_cart(cart)
        return {"message": "Корзина очищена"}