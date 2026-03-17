<template>
  <div class="min-h-screen flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">
      <!-- Логотип -->
      <div class="text-center mb-8">
        <div class="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-3xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary-500/30">
          <span class="text-4xl">🍕</span>
        </div>
        <h1 class="text-3xl font-bold text-white">Регистрация</h1>
        <p class="text-dark-400 mt-2">Создайте аккаунт</p>
      </div>

      <!-- Форма -->
      <div class="premium-card p-8">
        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">
              Логин *
            </label>
            <input
              v-model="registerForm.login"
              type="text"
              placeholder="Придумайте логин"
              class="input-primary"
              required
            />
          </div>

          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">
              Email
            </label>
            <input
              v-model="registerForm.email"
              type="email"
              placeholder="example@mail.com"
              class="input-primary"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-dark-300 text-sm font-medium mb-2">
                Имя
              </label>
              <input
                v-model="registerForm.first_name"
                type="text"
                placeholder="Имя"
                class="input-primary"
              />
            </div>
            <div>
              <label class="block text-dark-300 text-sm font-medium mb-2">
                Фамилия
              </label>
              <input
                v-model="registerForm.last_name"
                type="text"
                placeholder="Фамилия"
                class="input-primary"
              />
            </div>
          </div>

          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">
              Пароль *
            </label>
            <input
              v-model="registerForm.password"
              type="password"
              placeholder="Придумайте пароль"
              class="input-primary"
              required
              minlength="6"
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
            <span v-if="isLoading">Регистрация...</span>
            <span v-else>Зарегистрироваться</span>
          </button>
        </form>

        <div class="mt-6 text-center">
          <p class="text-dark-400 text-sm">
            Уже есть аккаунт? 
            <router-link to="/login" class="text-primary-400 hover:text-primary-300 font-medium">
              Войти
            </router-link>
          </p>
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

const registerForm = ref({
  login: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
})

const isLoading = ref(false)
const error = ref('')

const handleRegister = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    await authStore.register(registerForm.value)
    router.push('/login')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при регистрации'
  } finally {
    isLoading.value = false
  }
}
</script>
