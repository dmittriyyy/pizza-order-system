# Piazza Pizza

Система онлайн-заказа пиццы для дипломного проекта.  
Сейчас проект состоит из общего backend API на FastAPI, веб-клиента на Vue 3, Android-приложения и Telegram-бота, которые работают с одной базой данных и общей бизнес-логикой.

## Что есть сейчас

- каталог товаров и категорий
- регистрация и вход по логину/паролю
- профиль текущего пользователя
- корзина и оформление заказа
- история заказов
- ролевой доступ для `admin`, `cook`, `courier`, `client`
- админ-панель для сотрудников и товаров
- кухонный интерфейс для повара
- интерфейс доставки для курьера
- чат с AI-ассистентом через backend
- Telegram-бот с просмотром меню, корзиной и переходом в Mini App
- Telegram auth для входа в Mini App через `/api/auth/telegram`

## Архитектура

### Backend
- `backend/app` - FastAPI API, бизнес-логика, SQLAlchemy модели, маршруты и сервисы
- база данных по умолчанию: `SQLite`
- документация Swagger: `/api/docs`

### Frontend
- `frontend` - веб-приложение на Vue 3 + Vite + Pinia + Vue Router
- роли и доступ к страницам проверяются на клиенте и на backend

### Telegram Bot
- `tg` - бот на `aiogram`
- использует общую БД проекта
- может показывать меню, работать с корзиной и отправлять пользователя в Mini App

### Android
- `android-diplom` - Android-клиент проекта

## Стек

- Backend: `FastAPI`, `SQLAlchemy`, `Pydantic`, `Uvicorn`
- Database: `SQLite`
- Frontend: `Vue 3`, `Vite`, `Pinia`, `Vue Router`, `Tailwind CSS`, `Axios`
- Telegram Bot: `aiogram`
- Android: `Kotlin`, `Jetpack Compose`

## Структура проекта

```text
pizza-order-system/
├── backend/           # FastAPI backend
├── frontend/          # Vue 3 frontend
├── tg/                # Telegram bot
├── android-diplom/    # Android app
├── .gitignore
└── readme.md
```

## Основные API маршруты

### Аутентификация
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/telegram`

### Каталог и корзина
- `GET /api/products`
- `GET /api/categories`
- `GET /api/cart`
- `POST /api/cart/add`
- `PUT /api/cart/update/{item_id}`
- `DELETE /api/cart/remove/{item_id}`

### Заказы
- `POST /api/orders`
- `GET /api/orders`
- `GET /api/orders/{order_id}`
- `GET /api/orders/admin/all`
- `GET /api/orders/cook/pending`
- `GET /api/orders/courier/ready`

### Чат
- `POST /api/chat/send`
- `GET /api/chat/history`
- `DELETE /api/chat/clear`


## Локальный запуск

### 1. Backend

Из корня проекта:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

Backend будет доступен на `http://127.0.0.1:8000`  
Swagger UI: `http://127.0.0.1:8000/api/docs`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend по умолчанию доступен на `http://localhost:5173`


### 3. Telegram Bot

Из корня проекта:

```bash
source .venv/bin/activate
pip install -r tg/requirements.txt
python -m tg.bot
```

Для работы бота должны быть запущены backend и все его зависимости.

### 4. Android

Открыть папку `android-diplom` в Android Studio и запустить приложение стандартной сборкой Gradle.

## Тестовые аккаунты

### Администратор
- логин: `admin_boss`
- пароль: `pass_1`

### Повар
- логин: `cook_maria`
- пароль: `pass_2`

### Курьер
- логин: `courier_vic`
- пароль: `pass_3`

### Клиент
- логин: `user_igor`
- пароль: `pass_4`

## Telegram-бот

Что уже реализовано:

- `/start`
- `/menu`
- `/cart`
- `/clear`
- `/help`
- текстовый диалог с рекомендациями через существующий `ChatService`
- общая корзина с основной системой
- кнопка открытия Mini App

На текущем этапе заказ оформляется через сайт или Mini App, а не прямо в чате.

## Документация по подпроектам

- фронтенд: [frontend/README.md](/Users/dimyllik/Институт/Диплом/pizza-order-system/frontend/README.md:1)
- Telegram-бот: [tg/README.md](/Users/dimyllik/Институт/Диплом/pizza-order-system/tg/README.md:1)
