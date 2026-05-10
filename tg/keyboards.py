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


def checkout_keyboard(total: float) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=f"Оплатить и заказать {total:.0f} ₽",
                callback_data="checkout_pay",
            )
        ]
    ]
    if settings.tg_mini_app_url:
        rows.append(
            [
                InlineKeyboardButton(
                    text="Открыть Mini App",
                    web_app=WebAppInfo(url=settings.tg_mini_app_url),
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def review_rating_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1", callback_data=f"review_rate:{order_id}:1"),
                InlineKeyboardButton(text="2", callback_data=f"review_rate:{order_id}:2"),
                InlineKeyboardButton(text="3", callback_data=f"review_rate:{order_id}:3"),
                InlineKeyboardButton(text="4", callback_data=f"review_rate:{order_id}:4"),
                InlineKeyboardButton(text="5", callback_data=f"review_rate:{order_id}:5"),
            ]
        ]
    )
