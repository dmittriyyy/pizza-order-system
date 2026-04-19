from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from .config import settings
from .keyboards import start_keyboard
from .services import TelegramPizzaService


logging.basicConfig(level=logging.INFO)

dp = Dispatcher()
service = TelegramPizzaService()


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    text = (
        "Я бот Piazza Pizza.\n"
        "Могу подсказать по меню, порекомендовать блюда и собрать корзину прямо в чате.\n\n"
        "Команды:\n"
        "/menu - краткое меню\n"
        "/cart - показать корзину\n"
        "/clear - очистить корзину"
    )
    await message.answer(text, reply_markup=start_keyboard())


@dp.message(Command("menu"))
async def menu_handler(message: Message) -> None:
    await message.answer(
        service.render_menu_preview(limit=settings.tg_menu_preview_limit),
        reply_markup=start_keyboard(),
    )


@dp.message(Command("cart"))
async def cart_handler(message: Message) -> None:
    await message.answer(
        service.get_cart_text(
            message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
    )


@dp.message(Command("clear"))
async def clear_handler(message: Message) -> None:
    await message.answer(
        service.clear_cart(
            message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
    )


@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(
        "Пиши обычным текстом.\n"
        "Например:\n"
        "«посоветуй что-нибудь мясное»\n"
        "«добавь две пепперони»\n"
        "«что есть из десертов?»"
    )


@dp.message()
async def chat_handler(message: Message) -> None:
    if not message.text or not message.from_user:
        await message.answer("Поддерживаются только текстовые сообщения.")
        return

    response = service.chat(
        message.from_user.id,
        message.text,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await message.answer(response, reply_markup=start_keyboard())


async def main() -> None:
    bot = Bot(
        token=settings.tg_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
