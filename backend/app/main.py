import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import init_db

# Импорт роутеров (строго по файловой структуре проекта)
from .routes.auth import router as auth_router
from .routes.auth_me import router as auth_me_router
from .routes.profile import router as profile_router
from .routes.products import router as products_router
from .routes.categories import router as categories_router
from .routes.cart import router as cart_router
from .routes.order import router as orders_router
from .routes.chat import router as chat_router
from .routes.admin_employees import router as admin_employees_router
from .routes.products_admin import router as products_admin_router

app = FastAPI(
    title=settings.app_name,
    description="Платформа онлайн-заказа пиццы",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    debug=settings.debug
)

# 1. CORS: Разрешаем ВСЕ (для отладки и эмулятора)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Статика (картинки)
if os.path.exists(settings.static_dir):
    app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

# 3. Подключаем роутеры (префиксы уже заданы в самих файлах роутеров!)
app.include_router(auth_router)
app.include_router(auth_me_router)
app.include_router(profile_router)
app.include_router(products_router)
app.include_router(categories_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(chat_router)
app.include_router(admin_employees_router)
app.include_router(products_admin_router)

# 4. Инициализация БД при старте
@app.on_event("startup")
def on_startup():
    print("🚀 Запуск сервера... Инициализация БД.")
    init_db()

@app.get("/")
def root():
    return {"message": "Pizza API is running!", "docs": "/api/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 5. Запуск (если файл запущен напрямую)
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level='info'
    )