from pathlib import Path

from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = BASE_DIR / "pizza.db"
DEFAULT_STATIC_DIR = BASE_DIR / "app" / "static"
DEFAULT_IMAGES_DIR = DEFAULT_STATIC_DIR / "images"


class Settings(BaseSettings):
    app_name: str = "Piazza Pizza API"
    debug: bool = True

    database_url: str = f"sqlite:///{DEFAULT_DB_PATH}"

    cors_origins: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    static_dir: str = str(DEFAULT_STATIC_DIR)
    images_dir: str = str(DEFAULT_IMAGES_DIR)

    SECRET_KEY: str = "super-secret-pizza-key-change-in-production-abc123xyz"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    telegram_bot_token: str | None = None
    telegram_auth_max_age_seconds: int = 86400


    class Config:
        env_file = ".env"
        extra = "ignore" 


settings = Settings()
