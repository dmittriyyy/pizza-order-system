from .products import router as products_router
from .categories import router as categories_router
from .cart import router as cart_router
from .order import router as orders_router
from .auth import router as auth_router
from .products_admin import router as products_admin_router

__all__ = [
    "products_router",
    "categories_router",
    "cart_router",
    "orders_router",
    "auth_router",
    "products_admin_router"
]