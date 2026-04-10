from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Piazza Pizza API"
    debug: bool = True

    database_url: str = "sqlite:///./pizza.db"

    cors_origins: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    static_dir: str = "app/static"
    images_dir: str = "app/static/images"

    SECRET_KEY: str = "super-secret-pizza-key-change-in-production-abc123xyz"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


    class Config:
        env_file = ".env"
        extra = "ignore" 


settings = Settings()
