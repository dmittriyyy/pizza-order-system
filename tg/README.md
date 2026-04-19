# Telegram Bot

Каркас Telegram-бота для `Piazza Pizza`.

Что уже есть:
- `/start`, `/menu`, `/cart`, `/clear`, `/help`
- свободный диалог через существующий `ChatService` и `Ollama`
- общая корзина для Telegram-бота и Mini App через пользователя в основной БД
- кнопка открытия `Mini App`

Пока это промежуточный этап:
- Mini App логинится через `/api/auth/telegram`
- заказ оформляется через `Mini App`, не из чата

## Запуск

Из корня проекта:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
pip install -r tg/requirements.txt
cp tg/.env.example .env
python -m tg.bot
```

Для работы также должны быть подняты:
- backend FastAPI
- Ollama с нужной моделью

## Обязательные `.env` переменные

В корневом `.env` должны быть:

```env
TG_BOT_TOKEN=токен_бота_для_telegram_сервиса
TELEGRAM_BOT_TOKEN=тот_же_токен_для_backend_валидации_initData
TG_MINI_APP_URL=https://адрес-твоего-mini-app
```
