from sqlalchemy.orm import Session, joinedload
from ..models.cart import Cart
from ..models.cartItem import CartItem


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_cart(self, user_id: int) -> Cart:
        cart = self.db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            self.db.add(cart)
            self.db.commit()
            self.db.refresh(cart)
        return cart

    def get_cart_by_user_id(self, user_id: int) -> Cart | None:
        cart = self.db.query(Cart).options(
            joinedload(Cart.items).joinedload(CartItem.product)
        ).filter(Cart.user_id == user_id).first()
        return cart

    def add_item(self, cart: Cart, product_id: int, quantity: int) -> CartItem:
        existing_item = self.db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        ).first()
        if existing_item:
            existing_item.quantity += quantity
        else:
            item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
            self.db.add(item)

        self.db.commit()
        return cart

    def update_item(self, cart: Cart, product_id: int, quantity: int) -> CartItem:
        item = self.db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        ).first()
        if not item:
            return None
        if quantity <= 0:
            self.db.delete(item)
        else:
            item.quantity = quantity
        self.db.commit()
        return cart

    def remove_item(self, cart: Cart, product_id: int) -> bool:
        item = self.db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        ).first()
        if not item:
            return False
        self.db.delete(item)
        self.db.commit()
        return True

    def clear_cart(self, cart: Cart) -> None:
        self.db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        self.db.commit()
