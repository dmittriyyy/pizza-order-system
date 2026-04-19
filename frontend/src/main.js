import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from '@/stores/auth'
import { initTelegramWebApp, isTelegramMiniApp } from '@/services/telegram'

const app = createApp(App)

const pinia = createPinia()

app.use(pinia)
app.use(router)

// Загружаем данные пользователя после создания приложения
const authStore = useAuthStore()
authStore.loadUserFromStorage()

const telegramWebApp = initTelegramWebApp()
if (telegramWebApp && isTelegramMiniApp() && !authStore.token) {
  try {
    await authStore.telegramLogin(telegramWebApp.initData)
  } catch (error) {
    console.error('❌ Ошибка Telegram auth:', error)
  }
}

app.mount('#app')
