<template>
  <div class="auth-shell min-h-screen px-4 py-6 md:py-12">
    <div class="auth-panel w-full max-w-md mx-auto">
      <div class="text-center mb-6 md:mb-8">
        <div class="auth-logo mx-auto mb-4">
          <span class="text-4xl">🍕</span>
        </div>
        <h1 class="text-3xl md:text-4xl font-bold text-white">Войти</h1>
        <p class="text-dark-300 mt-2 text-sm md:text-base">
          {{ isTelegramMiniApp ? 'Откройте Mini App и авторизуйтесь для заказа и общей корзины.' : 'Войдите в аккаунт Piazza Pizza.' }}
        </p>
      </div>

      <div class="premium-card p-5 md:p-8 space-y-5">
        <div v-if="isTelegramMiniApp" class="glass rounded-[24px] p-4 md:p-5">
          <p class="text-white font-semibold text-base mb-2">Вход через Telegram</p>
          <p class="text-dark-300 text-sm leading-relaxed mb-4">
            Это основной вход для пользователей Mini App. После авторизации корзина и заказы будут связаны с вашим Telegram.
          </p>
          <button
            type="button"
            :disabled="isTelegramLoading || !canUseTelegram"
            class="btn-primary w-full py-4 text-base disabled:opacity-50 disabled:cursor-not-allowed"
            @click="handleTelegramLogin"
          >
            <span v-if="isTelegramLoading">Подключение...</span>
            <span v-else>Войти через Telegram</span>
          </button>
          <p v-if="!canUseTelegram" class="text-xs text-red-400 mt-3">
            Telegram initData не найден. Откройте страницу именно из бота как Mini App.
          </p>
        </div>

        <div class="flex items-center gap-3">
          <div class="h-px flex-1 bg-white/10"></div>
          <span class="text-xs uppercase tracking-[0.22em] text-dark-500">или</span>
          <div class="h-px flex-1 bg-white/10"></div>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">Логин</label>
            <input
              v-model.trim="loginForm.login"
              type="text"
              placeholder="Введите логин"
              class="input-primary"
              autocomplete="username"
              required
            />
          </div>

          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">Пароль</label>
            <input
              v-model="loginForm.password"
              type="password"
              placeholder="Введите пароль"
              class="input-primary"
              autocomplete="current-password"
              required
            />
          </div>

          <div v-if="error" class="bg-red-500/10 border border-red-500/30 rounded-2xl p-4">
            <p class="text-red-400 text-sm">{{ error }}</p>
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="btn-primary w-full py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading">Вход...</span>
            <span v-else>Войти</span>
          </button>
        </form>

        <div class="glass rounded-[24px] p-4 text-center">
          <p class="text-dark-300 text-sm">
            Нет аккаунта?
            <router-link to="/register" class="text-primary-400 hover:text-primary-300 font-semibold">
              Зарегистрироваться
            </router-link>
          </p>
        </div>

        <div v-if="!isTelegramMiniApp" class="pt-2 border-t border-white/10">
          <p class="text-dark-500 text-xs text-center mb-3">Тестовые аккаунты</p>
          <div class="space-y-2 text-xs text-dark-400">
            <p><span class="text-primary-400">admin_boss</span> / pass_1</p>
            <p><span class="text-primary-400">user_igor</span> / pass_4</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { canUseTelegramAuth, getTelegramWebApp, isTelegramMiniApp as detectTelegramMiniApp } from '@/services/telegram'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loginForm = ref({
  login: '',
  password: '',
})

const isLoading = ref(false)
const isTelegramLoading = ref(false)
const error = ref('')

const isTelegramMiniApp = computed(() => detectTelegramMiniApp())
const canUseTelegram = computed(() => canUseTelegramAuth())

const resolveRedirect = () => {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  return redirect || authStore.redirectByRole()
}

const handleLogin = async () => {
  isLoading.value = true
  error.value = ''

  try {
    await authStore.login(loginForm.value.login, loginForm.value.password)
    router.push(resolveRedirect())
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при входе'
  } finally {
    isLoading.value = false
  }
}

const handleTelegramLogin = async () => {
  const webApp = getTelegramWebApp()
  if (!webApp?.initData) {
    error.value = 'Откройте приложение именно внутри Telegram Mini App.'
    return
  }

  isTelegramLoading.value = true
  error.value = ''

  try {
    await authStore.telegramLogin(webApp.initData)
    router.push(resolveRedirect())
  } catch (err) {
    error.value = err.response?.data?.detail || 'Не удалось войти через Telegram'
  } finally {
    isTelegramLoading.value = false
  }
}
</script>
