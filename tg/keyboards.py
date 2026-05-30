from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from .config import settings


def start_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="🍕 Меню", callback_data="nav_menu"),
            InlineKeyboardButton(text="🛒 Корзина", callback_data="nav_cart"),
        ],
        [
            InlineKeyboardButton(text="💳 Оформить", callback_data="nav_checkout"),
            InlineKeyboardButton(text="📦 Заказы", callback_data="nav_orders"),
        ],
        [
            InlineKeyboardButton(text="⭐ Отзыв", callback_data="nav_review"),
            InlineKeyboardButton(text="ℹ️ Помощь", callback_data="nav_help"),
        ],
        [
            InlineKeyboardButton(text="🛟 Техподдержка", callback_data="nav_support"),
        ],
    ]

    if settings.tg_mini_app_url:
        rows.append(
            [
                InlineKeyboardButton(
                    text="📱 Открыть Mini App",
                    web_app=WebAppInfo(url=settings.tg_mini_app_url),
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=rows)


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
