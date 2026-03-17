import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .routes import products_router, cart_router, categories_router, orders_router, auth_router, products_admin_router
from .database import init_db

app = FastAPI(
    title=settings.app_name,
    description="Платформа онлайн-заказа пиццы",
    version="1.0.0", 
    debug=settings.debug,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins, # откуда можно принимать
    allow_credentials=True, # разрешаем отправлять куки
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(categories_router)
app.include_router(orders_router)
app.include_router(products_admin_router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/") 
def root():
    return {
        "message": "Welcome to the Pizza Platform API!",
        "docs": "/api/docs",}

@app.get('/health')
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level='info'
    )
