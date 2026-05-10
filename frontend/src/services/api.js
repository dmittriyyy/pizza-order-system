import axios from 'axios'

const apiBaseURL = import.meta.env.VITE_API_BASE_URL || ''

// Локально можно оставить пустую строку и использовать Vite Proxy.
// Для деплоя Mini App укажи VITE_API_BASE_URL=https://<your-backend>.
const apiClient = axios.create({
  baseURL: apiBaseURL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

// Токен
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default apiClient
