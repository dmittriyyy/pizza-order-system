from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

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


@dataclass
class AuthState:
    mode: str
    step: str
    login: str | None = None
    password: str | None = None
    first_name: str | None = None


auth_states: dict[int, AuthState] = {}


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    linked_suffix = (
        "\nАккаунт уже привязан, можно работать с корзиной и статусами."
        if service.is_linked(message.from_user.id)
        else "\nСначала привяжи аккаунт командой /link."
    )
    text = (
        "Я бот Piazza Pizza.\n"
        "Могу подсказать по меню, порекомендовать блюда и собрать корзину прямо в чате.\n\n"
        "Команды:\n"
        "/register - зарегистрировать новый аккаунт\n"
        "/link - привязать аккаунт Piazza Pizza\n"
        "/unlink - снять текущую привязку\n"
        "/menu - краткое меню\n"
        "/cart - показать корзину\n"
        "/clear - очистить корзину\n"
        "/status - статус последнего заказа\n"
        "/recommend - персональные рекомендации"
        f"{linked_suffix}"
    )
    await message.answer(text, reply_markup=start_keyboard())


@dp.message(Command("link"))
async def link_handler(message: Message) -> None:
    if service.is_linked(message.from_user.id):
        user = service.get_linked_user(message.from_user.id)
        await message.answer(
            f"Этот Telegram уже привязан к аккаунту {user.login}.\n"
            "Если нужна другая привязка, сначала выполни /unlink."
        )
        return

    auth_states[message.from_user.id] = AuthState(mode="link", step="awaiting_login")
    await message.answer("Введи логин от своего аккаунта Piazza Pizza.")


@dp.message(Command("unlink"))
async def unlink_handler(message: Message) -> None:
    auth_states.pop(message.from_user.id, None)
    await message.answer(service.unlink_account(message.from_user.id))


@dp.message(Command("register"))
async def register_handler(message: Message) -> None:
    if service.is_linked(message.from_user.id):
        user = service.get_linked_user(message.from_user.id)
        await message.answer(
            f"Этот Telegram уже привязан к аккаунту {user.login}.\n"
            "Если нужен новый аккаунт, сначала выполни /unlink."
        )
        return

    auth_states[message.from_user.id] = AuthState(mode="register", step="awaiting_login")
    await message.answer("Придумай логин для нового аккаунта Piazza Pizza.")


@dp.message(Command("menu"))
async def menu_handler(message: Message) -> None:
    await message.answer(
        service.render_menu_preview(limit=settings.tg_menu_preview_limit),
        reply_markup=start_keyboard(),
    )


@dp.message(Command("cart"))
async def cart_handler(message: Message) -> None:
    if not service.is_linked(message.from_user.id):
        await message.answer(service.require_link_message())
        return
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
    if not service.is_linked(message.from_user.id):
        await message.answer(service.require_link_message())
        return
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
        "«что есть из десертов?»\n\n"
        "Дополнительно:\n"
        "/register - создать аккаунт\n"
        "/link - привязать аккаунт\n"
        "/unlink - снять привязку\n"
        "/status - где мой заказ\n"
        "/recommend - что заказать снова"
    )


@dp.message(Command("status"))
async def status_handler(message: Message) -> None:
    if not service.is_linked(message.from_user.id):
        await message.answer(service.require_link_message())
        return
    await message.answer(
        service.get_latest_order_status(
            message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        ),
        reply_markup=start_keyboard(),
    )


@dp.message(Command("recommend"))
async def recommend_handler(message: Message) -> None:
    if not service.is_linked(message.from_user.id):
        await message.answer(service.require_link_message())
        return
    await message.answer(
        service.get_recommendations_text(
            message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        ),
        reply_markup=start_keyboard(),
    )


@dp.message()
async def chat_handler(message: Message) -> None:
    if not message.text or not message.from_user:
        await message.answer("Поддерживаются только текстовые сообщения.")
        return

    state = auth_states.get(message.from_user.id)
    if state:
        if state.step == "awaiting_login":
            auth_states[message.from_user.id] = AuthState(
                mode=state.mode,
                step="awaiting_password",
                login=message.text.strip(),
            )
            if state.mode == "link":
                await message.answer("Теперь введи пароль. Я использую его только для привязки аккаунта.")
            else:
                await message.answer("Теперь придумай пароль для нового аккаунта.")
            return

        if state.step == "awaiting_password":
            if state.mode == "link":
                login = state.login or ""
                result = service.link_existing_account(
                    message.from_user.id,
                    login=login,
                    password=message.text.strip(),
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                )
                auth_states.pop(message.from_user.id, None)
                await message.answer(result, reply_markup=start_keyboard())
                return

            auth_states[message.from_user.id] = AuthState(
                mode="register",
                step="awaiting_first_name",
                login=state.login,
                password=message.text.strip(),
            )
            await message.answer("Введи имя для нового аккаунта. Если не хочешь, отправь -")
            return

        if state.step == "awaiting_first_name":
            auth_states[message.from_user.id] = AuthState(
                mode="register",
                step="awaiting_last_name",
                login=state.login,
                password=state.password,
                first_name=None if message.text.strip() == "-" else message.text.strip(),
            )
            await message.answer("Введи фамилию для нового аккаунта. Если не хочешь, отправь -")
            return

        if state.step == "awaiting_last_name":
            result = service.register_account(
                message.from_user.id,
                login=state.login or "",
                password=state.password or "",
                first_name=state.first_name,
                last_name=None if message.text.strip() == "-" else message.text.strip(),
                username=message.from_user.username,
            )
            auth_states.pop(message.from_user.id, None)
            await message.answer(result, reply_markup=start_keyboard())
            return

    if not service.is_linked(message.from_user.id):
        await message.answer(service.require_link_message())
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
