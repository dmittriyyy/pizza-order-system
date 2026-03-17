import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Создаем экземпляр axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// Интерсептор для добавления токена авторизации
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Интерсептор для обработки ошибок
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Проверяем, есть ли вообще токен
      const token = localStorage.getItem('access_token')
      if (token) {
        // Токен был, но истек или недействителен - очищаем и редиректим
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        // Не делаем редирект сразу, даём компоненту обработать ошибку
        console.warn('Токен истёк, выполните вход заново')
      }
      // Если токена не было - просто возвращаем ошибку, не редиректим
    }
    return Promise.reject(error)
  }
)

export default apiClient
