import api from './api'

export const authService = {
  // Вход пользователя
  async login(login, password) {
    const response = await api.post('/api/auth/login', { login, password })
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('token_type', response.data.token_type)
    }
    return response.data
  },

  // Регистрация пользователя
  async register(userData) {
    const response = await api.post('/api/auth/register', userData)
    return response.data
  },

  // Выход (очищаем токен)
  logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('token_type')
    localStorage.removeItem('user')
  },

  // Получение текущего пользователя (из токена)
  getCurrentUser() {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  },

  // Сохранение пользователя
  setCurrentUser(user) {
    localStorage.setItem('user', JSON.stringify(user))
  },

  // Проверка авторизации
  isAuthenticated() {
    return !!localStorage.getItem('access_token')
  },
}

export const productService = {
  // Получение всех продуктов
  async getAll() {
    const response = await api.get('/api/products')
    // Бэкенд возвращает { products: [...], total: N }, нам нужен массив
    return response.data.products || response.data
  },

  // Получение продукта по ID
  async getById(id) {
    const response = await api.get(`/api/products/${id}`)
    return response.data
  },

  // Получение продуктов по категории
  async getByCategory(categoryId) {
    const response = await api.get(`/api/products/category/${categoryId}`)
    return response.data.products || response.data
  },
}

export const categoryService = {
  // Получение всех категорий
  async getAll() {
    const response = await api.get('/api/categories')
    // Бэкенд может возвращать { categories: [...] } или просто [...]
    return response.data.categories || response.data
  },
}

export const cartService = {
  // Получение корзины
  async get() {
    const response = await api.get('/api/cart')
    return response.data
  },

  // Добавление товара в корзину
  async add(productId, quantity = 1) {
    const response = await api.post('/api/cart/add', { product_id: productId, quantity })
    return response.data
  },

  // Обновление количества товара
  async update(productId, quantity) {
    const response = await api.put(`/api/cart/update/${productId}`, { quantity })
    return response.data
  },

  // Удаление товара из корзины
  async remove(productId) {
    const response = await api.delete(`/api/cart/remove/${productId}`)
    return response.data
  },

  // Очистка корзины
  async clear() {
    const response = await api.delete('/api/cart/clear')
    return response.data
  },
}

export const orderService = {
  // Создание заказа
  async create(orderData) {
    const response = await api.post('/api/orders', orderData)
    return response.data
  },

  // Получение списка заказов
  async getAll(params = {}) {
    const response = await api.get('/api/orders', { params })
    return response.data
  },

  // Получение заказа по ID
  async getById(id) {
    const response = await api.get(`/api/orders/${id}`)
    return response.data
  },
}
