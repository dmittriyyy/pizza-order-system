# Pizza Premium — Frontend

Современное веб-приложение для заказа пиццы на Vue 3 с использованием Composition API, Vite, Pinia и Tailwind CSS.

## 🚀 Технологии

- **Vue 3** — Composition API (`<script setup>`)
- **Vite** — Быстрый сборщик
- **Pinia** — State management
- **Vue Router** — Маршрутизация с guards
- **Tailwind CSS** — Стилизация
- **Axios** — HTTP клиент с интерсепторами
- **Glassmorphism** — Премиальный дизайн с эффектом стекла

## 📁 Структура проекта

```
frontend/
├── src/
│   ├── assets/
│   │   └── main.css          # Глобальные стили и Tailwind директивы
│   ├── components/
│   │   ├── Navbar.vue        # Навигация с glassmorphism
│   │   ├── ProductCard.vue   # Карточка товара
│   │   ├── CategoryFilter.vue # Фильтр по категориям
│   │   ├── CartDrawer.vue    # Выезжающая корзина
│   │   └── AIWidget.vue      # AI чат-помощник
│   ├── router/
│   │   └── index.js          # Маршруты с guards
│   ├── services/
│   │   ├── api.js            # Axios экземпляр с интерсепторами
│   │   └── index.js          # API сервисы (auth, products, cart, orders)
│   ├── stores/
│   │   ├── auth.js           # Auth store (JWT)
│   │   ├── cart.js           # Cart store
│   │   └── products.js       # Products store
│   ├── views/
│   │   ├── HomeView.vue      # Главная страница
│   │   ├── LoginView.vue     # Вход
│   │   ├── RegisterView.vue  # Регистрация
│   │   ├── ProfileView.vue   # Профиль пользователя
│   │   └── AboutView.vue     # О нас
│   ├── App.vue               # Корневой компонент
│   └── main.js               # Точка входа
├── tailwind.config.js
├── vite.config.js
└── package.json
```

## 🎨 Дизайн-система

### Цвета
- **Primary**: Оранжевый градиент (`#ea670a` → `#d14d07`)
- **Dark**: Тёмная палитра для фона
- **Glass**: Полупрозрачные элементы с backdrop-blur

### Компоненты
- **premium-card** — Карточка с градиентом и тенью
- **glass-button** — Кнопка с эффектом стекла
- **btn-primary** — Основная кнопка с градиентом
- **input-primary** — Стильный input

## 🔑 Ключевые возможности

### 1. Auth Store с JWT
```javascript
// stores/auth.js
- Автоматическое сохранение токена в localStorage
- Axios interceptor добавляет Authorization header
- Redirect на /login при 401 ошибке
```

### 2. AI Widget (чат-помощник)
```javascript
// components/AIWidget.vue
- Плавающая кнопка в нижнем углу
- Имитация ответа за 1.5 секунды
- Контекстные ответы о меню
- Анимация набора текста
```

### 3. Cart Drawer
```javascript
// components/CartDrawer.vue
- Выезжающая панель справа
- Управление количеством товаров
- Оформление заказа в 1 клик
```

### 4. Роутинг с guards
```javascript
// router/index.js
- requiresAuth — защита маршрутов
- guestOnly — только для неавторизованных
- Автоматическая установка title страницы
```

## 🛠️ Установка и запуск

### 1. Установка зависимостей
```bash
npm install
```

### 2. Настройка переменных окружения
```bash
# .env
VITE_API_URL=http://localhost:8000
```

### 3. Запуск dev-сервера
```bash
npm run dev
```

Приложение доступно по адресу: **http://localhost:5173**

## 📡 API Endpoints

| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| POST | `/api/auth/login` | Вход | ❌ |
| POST | `/api/auth/register` | Регистрация | ❌ |
| GET | `/api/products` | Все продукты | ❌ |
| GET | `/api/categories` | Все категории | ❌ |
| GET | `/api/cart` | Корзина | ✅ |
| POST | `/api/cart/add` | Добавить в корзину | ✅ |
| PUT | `/api/cart/update/{id}` | Обновить количество | ✅ |
| DELETE | `/api/cart/remove/{id}` | Удалить из корзины | ✅ |
| POST | `/api/orders` | Создать заказ | ✅ |
| GET | `/api/orders` | История заказов | ✅ |

## 🧪 Тестовые аккаунты

| Логин | Пароль | Роль |
|-------|--------|------|
| `admin_boss` | `pass_1` | Администратор |
| `user_igor` | `pass_4` | Клиент |

## 📦 Сборка

```bash
npm run build
npm run preview
```

## 🎯 Особенности реализации

### Axios Interceptor
```javascript
// services/api.js
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

### AI Response Logic
```javascript
// AIWidget.vue
const generateAIResponse = (message) => {
  if (message.includes('пицц')) {
    return 'Привет! Я уже изучаю наше меню... 🍕'
  }
  // ... другие ответы
}
```

### Pinia Store с actions
```javascript
// stores/cart.js
export const useCartStore = defineStore('cart', {
  actions: {
    async addToCart(productId, quantity) {
      const data = await cartService.add(productId, quantity)
      this.items = data.items
    }
  }
})
```

## 📝 Лицензия

MIT
