import axios from 'axios'

// Всегда используем относительный путь, чтобы работал Vite Proxy.
// Это работает и на ПК (localhost:5173 -> localhost:8000),
// и на телефоне (192.168.x.x:5173 -> 192.168.x.x:8000).
const apiClient = axios.create({
  baseURL: '', 
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
