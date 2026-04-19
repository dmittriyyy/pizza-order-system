from pydantic_settings import BaseSettings, SettingsConfigDict


class TgSettings(BaseSettings):
    tg_bot_token: str
    tg_mini_app_url: str | None = None
    tg_bot_name: str = "Piazza Pizza Bot"
    tg_menu_preview_limit: int = 8

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = TgSettings()
