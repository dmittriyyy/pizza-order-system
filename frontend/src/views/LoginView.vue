<template>
  <div class="min-h-screen flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">
      <!-- Логотип -->
      <div class="text-center mb-8">
        <div class="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-3xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary-500/30">
          <span class="text-4xl">🍕</span>
        </div>
        <h1 class="text-3xl font-bold text-white">Pizza Premium</h1>
        <p class="text-dark-400 mt-2">Войдите в свой аккаунт</p>
      </div>

      <!-- Форма -->
      <div class="premium-card p-8">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">
              Логин
            </label>
            <input
              v-model="loginForm.login"
              type="text"
              placeholder="Введите логин"
              class="input-primary"
              required
            />
          </div>

          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">
              Пароль
            </label>
            <input
              v-model="loginForm.password"
              type="password"
              placeholder="Введите пароль"
              class="input-primary"
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

        <div class="mt-6 text-center">
          <p class="text-dark-400 text-sm">
            Нет аккаунта? 
            <router-link to="/register" class="text-primary-400 hover:text-primary-300 font-medium">
              Зарегистрироваться
            </router-link>
          </p>
        </div>

        <!-- Демо credentials -->
        <div class="mt-6 pt-6 border-t border-dark-700">
          <p class="text-dark-500 text-xs text-center mb-3">Тестовые аккаунты:</p>
          <div class="space-y-2 text-xs text-dark-400">
            <p><span class="text-primary-400">admin_boss</span> / pass_1 (Админ)</p>
            <p><span class="text-primary-400">user_igor</span> / pass_4 (Клиент)</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginForm = ref({
  login: '',
  password: '',
})

const isLoading = ref(false)
const error = ref('')

const handleLogin = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    await authStore.login(loginForm.value.login, loginForm.value.password)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при входе'
  } finally {
    isLoading.value = false
  }
}
</script>
