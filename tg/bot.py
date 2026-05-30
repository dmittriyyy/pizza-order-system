from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.enums import ParseMode

from .config import settings
from .keyboards import checkout_keyboard, review_rating_keyboard, start_keyboard
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
    address: str | None = None
    order_id: int | None = None
    rating: int | None = None


auth_states: dict[int, AuthState] = {}
chat_modes: dict[int, str] = {}


def _is_checkout_intent(text: str) -> bool:
    normalized = text.lower()
    triggers = (
        "оплат",
        "оформ",
        "закаж",
        "сделаем заказ",
        "сделай заказ",
        "хочу оформить",
        "хочу заказать",
        "перейти к оплате",
        "оплачу",
    )
    return any(trigger in normalized for trigger in triggers)


async def begin_checkout_flow(message: Message) -> None:
    checkout = service.get_checkout_context(
        message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    if not checkout:
        await message.answer(
            "Сначала соберём корзину. Напиши, что добавить: например, «добавь две пепперони»."
        )
        return

    if checkout.default_address:
        auth_states[message.from_user.id] = AuthState(
            mode="checkout",
            step="awaiting_payment",
            address=checkout.default_address,
        )
        await message.answer(
            "Переходим к оформлению.\n"
            f"Адрес: {checkout.default_address}\n"
            f"Сумма: {checkout.total:.0f} ₽\n\n"
            "Если адрес верный, нажми кнопку оплаты ниже. Если нужен другой адрес, просто отправь его следующим сообщением.",
            reply_markup=checkout_keyboard(checkout.total),
        )
        return

    auth_states[message.from_user.id] = AuthState(mode="checkout", step="awaiting_address")
    await message.answer(
        "Переходим к оформлению заказа.\n"
        "Напиши адрес доставки одним сообщением: улица, дом, квартира."
    )


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    linked_suffix = (
        "Аккаунт уже привязан. Можно собирать корзину, оформлять заказ и смотреть статусы."
        if service.is_linked(message.from_user.id)
        else "Сначала привяжи аккаунт через /link или создай новый через /register."
    )
    text = (
        "WOKI на связи.\n"
        "Могу подсказать по меню, добавить товары в корзину и помочь оформить заказ прямо в чате.\n\n"
        f"{linked_suffix}\n\n"
        "Основное:\n"
        "/menu — посмотреть меню\n"
        "/cart — открыть корзину\n"
        "/checkout — оформить заказ\n"
        "/orders — последние заказы\n"
        "/support_mode — агент техподдержки\n"
        "/consultant_mode — консультант по меню\n"
        "/review — оставить отзыв\n"
        "/help — все возможности"
    )
    await message.answer(text, reply_markup=start_keyboard())


@dp.message(Command("support_mode"))
async def support_mode_handler(message: Message) -> None:
    chat_modes[message.from_user.id] = "support"
    await message.answer(
        "Включен агент техподдержки. Если он не сможет точно ответить, он предупредит об этом и перенаправит вопрос администратору."
    )


@dp.message(Command("consultant_mode"))
async def consultant_mode_handler(message: Message) -> None:
    chat_modes[message.from_user.id] = "consultant"
    await message.answer("Включен консультант по меню и заказу.")


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
    )


@dp.message(Command("cart"))
async def cart_handler(message: Message) -> None:
    if not service.is_linked(message.from_user.id):
        await message.answer(service.require_link_message())
        return
    cart_text = service.get_cart_text(
        message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await message.answer(cart_text)
    checkout = service.get_checkout_context(
            message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
    if checkout:
        await message.answer(
            "Можно оформить заказ прямо здесь.",
            reply_markup=checkout_keyboard(checkout.total),
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
        "«что есть из десертов?»\n"
        "«давай оформим заказ»\n\n"
        "Команды:\n"
        "/menu — меню\n"
        "/cart — корзина\n"
        "/checkout — оформление заказа\n"
        "/orders — последние заказы\n"
        "/status — последний заказ\n"
        "/review — оставить отзыв\n"
        "/recommend — персональные рекомендации\n"
        "/support_mode — переключиться на техподдержку\n"
        "/consultant_mode — переключиться на консультанта\n"
        "/support_tickets — список обращений поддержки для админа\n"
        "/reply_ticket <id> <текст> — ответить клиенту по обращению\n"
        "/link — привязать существующий аккаунт\n"
        "/register — создать аккаунт\n"
        "/unlink — снять привязку"
    )


@dp.message(Command("support_tickets"))
async def support_tickets_handler(message: Message) -> None:
    await message.answer(service.list_open_support_tickets(message.from_user.id))


@dp.message(Command("reply_ticket"))
async def reply_ticket_handler(message: Message) -> None:
    raw_text = (message.text or "").strip()
    parts = raw_text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Формат: /reply_ticket <id> <текст ответа>")
        return

    try:
        ticket_id = int(parts[1])
    except ValueError:
        await message.answer("ID обращения должен быть числом.")
        return

    await message.answer(service.reply_support_ticket(message.from_user.id, ticket_id, parts[2]))


@dp.message(Command("checkout"))
async def checkout_handler(message: Message) -> None:
    if not service.is_linked(message.from_user.id):
        await message.answer(service.require_link_message())
        return
    await begin_checkout_flow(message)


@dp.message(Command("review"))
async def review_handler(message: Message) -> None:
    if not service.is_linked(message.from_user.id):
        await message.answer(service.require_link_message())
        return

    order = service.get_latest_completed_order_for_review(
        message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    if not order:
        await message.answer("Нет завершённого заказа без отзыва. Как только доставим заказ, сможешь оставить отзыв.")
        return

    auth_states[message.from_user.id] = AuthState(
        mode="review",
        step="awaiting_rating",
        order_id=order.id,
    )
    await message.answer(
        f"Оцените заказ #{order.id} по шкале от 1 до 5.",
        reply_markup=review_rating_keyboard(order.id),
    )


@dp.message(Command("orders"))
async def orders_handler(message: Message) -> None:
    if not service.is_linked(message.from_user.id):
        await message.answer(service.require_link_message())
        return

    await message.answer(
        service.get_recent_orders_text(
            message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        ),
        reply_markup=start_keyboard(),
    )


@dp.message(Command("reviews_digest"))
async def reviews_digest_handler(message: Message) -> None:
    if not message.from_user:
        return
    await message.answer(service.get_admin_feedback_digest(message.from_user.id))


@dp.callback_query()
async def callback_handler(callback: CallbackQuery) -> None:
    if not callback.from_user:
        return

    user_id = callback.from_user.id
    state = auth_states.get(user_id)
    data = callback.data or ""

    if data == "checkout_pay":
        if not state or state.mode != "checkout" or not state.address:
            await callback.answer("Сначала укажи адрес доставки.", show_alert=True)
            return

        result = service.create_order_from_cart(
            user_id,
            delivery_address=state.address,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            last_name=callback.from_user.last_name,
        )
        auth_states.pop(user_id, None)
        await callback.message.answer(result, reply_markup=start_keyboard())
        await callback.answer("Заказ обработан")
        return

    if data == "nav_menu":
        await callback.message.answer(
            service.render_menu_preview(limit=settings.tg_menu_preview_limit),
            reply_markup=start_keyboard(),
        )
        await callback.answer()
        return

    if data == "nav_cart":
        if not service.is_linked(user_id):
            await callback.message.answer(service.require_link_message())
            await callback.answer()
            return

        await callback.message.answer(
            service.get_cart_text(
                user_id,
                username=callback.from_user.username,
                first_name=callback.from_user.first_name,
                last_name=callback.from_user.last_name,
            ),
            reply_markup=start_keyboard(),
        )
        await callback.answer()
        return

    if data == "nav_checkout":
        if not service.is_linked(user_id):
            await callback.message.answer(service.require_link_message())
            await callback.answer()
            return

        checkout = service.get_checkout_context(
            user_id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            last_name=callback.from_user.last_name,
        )
        if not checkout:
            await callback.message.answer("Корзина пуста. Сначала добавь товары.")
            await callback.answer()
            return

        if checkout.default_address:
            auth_states[user_id] = AuthState(
                mode="checkout",
                step="awaiting_payment",
                address=checkout.default_address,
            )
            await callback.message.answer(
                f"Подтверди заказ.\nАдрес: {checkout.default_address}\nСумма: {checkout.total:.0f} ₽",
                reply_markup=checkout_keyboard(checkout.total),
            )
        else:
            auth_states[user_id] = AuthState(mode="checkout", step="awaiting_address")
            await callback.message.answer("Введи адрес доставки текстом. После этого я покажу кнопку оплаты.")
        await callback.answer()
        return

    if data == "nav_orders":
        if not service.is_linked(user_id):
            await callback.message.answer(service.require_link_message())
            await callback.answer()
            return

        await callback.message.answer(
            service.get_recent_orders_text(
                user_id,
                username=callback.from_user.username,
                first_name=callback.from_user.first_name,
                last_name=callback.from_user.last_name,
            ),
            reply_markup=start_keyboard(),
        )
        await callback.answer()
        return

    if data == "nav_review":
        if not service.is_linked(user_id):
            await callback.message.answer(service.require_link_message())
            await callback.answer()
            return

        order = service.get_latest_completed_order_for_review(
            user_id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            last_name=callback.from_user.last_name,
        )
        if not order:
            await callback.message.answer("Нет завершённого заказа без отзыва. Как только доставим заказ, сможешь оставить отзыв.")
            await callback.answer()
            return

        auth_states[user_id] = AuthState(
            mode="review",
            step="awaiting_rating",
            order_id=order.id,
        )
        await callback.message.answer(
            f"Оцените заказ #{order.id} по шкале от 1 до 5.",
            reply_markup=review_rating_keyboard(order.id),
        )
        await callback.answer()
        return

    if data == "nav_help":
        await callback.message.answer(
            "Основные действия:\n"
            "• Пиши обычным текстом, чтобы попросить совет или добавить товар\n"
            "• /cart — посмотреть корзину\n"
            "• /checkout — оформить заказ\n"
            "• /orders — последние заказы\n"
            "• /review — оставить отзыв",
            reply_markup=start_keyboard(),
        )
        await callback.answer()
        return

    if data == "nav_support":
        chat_modes[user_id] = "support"
        await callback.message.answer(
            "Включен агент техподдержки. Если он не сможет точно ответить, он предупредит об этом и перенаправит вопрос администратору.",
            reply_markup=start_keyboard(),
        )
        await callback.answer()
        return

    if data.startswith("review_rate:"):
        _, order_id_raw, rating_raw = data.split(":")
        if not state or state.mode != "review":
            await callback.answer("Сначала вызови /review", show_alert=True)
            return

        auth_states[user_id] = AuthState(
            mode="review",
            step="awaiting_review_comment",
            order_id=int(order_id_raw),
            rating=int(rating_raw),
        )
        await callback.message.answer(
            f"Поставили {rating_raw}/5 для заказа #{order_id_raw}.\n"
            "Теперь напиши комментарий одним сообщением. Если комментарий не нужен, отправь -"
        )
        await callback.answer("Оценка сохранена")
        return


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
        )
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
        )
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

        if state.mode == "checkout" and state.step == "awaiting_address":
            address = message.text.strip()
            checkout = service.get_checkout_context(
                message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
            )
            if not checkout:
                auth_states.pop(message.from_user.id, None)
                await message.answer("Корзина уже пуста. Сначала добавь товары.")
                return

            auth_states[message.from_user.id] = AuthState(
                mode="checkout",
                step="awaiting_payment",
                address=address,
            )
            await message.answer(
                f"Адрес принят: {address}\n"
                f"Сумма к оплате: {checkout.total:.0f} ₽\n\n"
                "Нажми кнопку ниже, чтобы подтвердить оплату и создать заказ.",
                reply_markup=checkout_keyboard(checkout.total),
            )
            return

        if state.mode == "review" and state.step == "awaiting_review_comment":
            result = service.create_feedback_for_order(
                message.from_user.id,
                order_id=state.order_id or 0,
                rating=state.rating or 5,
                comment=message.text.strip(),
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
            )
            auth_states.pop(message.from_user.id, None)
            await message.answer(result, reply_markup=start_keyboard())
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

    if _is_checkout_intent(message.text):
        await begin_checkout_flow(message)
        return

    agent_type = chat_modes.get(message.from_user.id, "consultant")
    response = service.chat(
        message.from_user.id,
        message.text,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        agent_type=agent_type,
    )
    await message.answer(response)


async def main() -> None:
    bot = Bot(
        token=settings.tg_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
