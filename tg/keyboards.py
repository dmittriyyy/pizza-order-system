from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from .config import settings


def start_keyboard() -> InlineKeyboardMarkup | None:
    if not settings.tg_mini_app_url:
        return None

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть Mini App",
                    web_app=WebAppInfo(url=settings.tg_mini_app_url),
                )
            ]
        ]
    )
