<template>
  <div class="auth-shell min-h-screen px-4 py-6 md:py-12">
    <div class="auth-panel w-full max-w-md mx-auto">
      <div class="text-center mb-6 md:mb-8">
        <div class="auth-logo mx-auto mb-4">
          <span class="text-4xl">🍕</span>
        </div>
        <h1 class="text-3xl md:text-4xl font-bold text-white">Регистрация</h1>
        <p class="text-dark-300 mt-2 text-sm md:text-base">
          Создайте аккаунт для заказов, истории и общей корзины между сайтом и ботом.
        </p>
      </div>

      <div class="premium-card p-5 md:p-8">
        <div v-if="isTelegramMiniApp" class="glass rounded-[24px] p-4 md:p-5 mb-5">
          <p class="text-white font-semibold text-base mb-2">Новый пользователь в Telegram</p>
          <p class="text-dark-300 text-sm leading-relaxed">
            Если хотите отдельный аккаунт с логином и паролем, зарегистрируйтесь ниже. Если нужен быстрый вход без пароля, вернитесь на экран входа и используйте Telegram-вход.
          </p>
        </div>

        <form @submit.prevent="handleRegister" class="space-y-4">
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="block text-dark-300 text-sm font-medium mb-2">Имя</label>
              <input
                v-model.trim="registerForm.first_name"
                type="text"
                placeholder="Иван"
                class="input-primary"
                autocomplete="given-name"
              />
            </div>

            <div>
              <label class="block text-dark-300 text-sm font-medium mb-2">Фамилия</label>
              <input
                v-model.trim="registerForm.last_name"
                type="text"
                placeholder="Петров"
                class="input-primary"
                autocomplete="family-name"
              />
            </div>
          </div>

          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">Email</label>
            <input
              v-model.trim="registerForm.email"
              type="email"
              placeholder="example@mail.com"
              class="input-primary"
              autocomplete="email"
            />
          </div>

          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">Логин</label>
            <input
              v-model.trim="registerForm.login"
              type="text"
              placeholder="Придумайте логин"
              class="input-primary"
              autocomplete="username"
              required
            />
          </div>

          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">Пароль</label>
            <input
              v-model="registerForm.password"
              type="password"
              placeholder="Минимум 6 символов"
              class="input-primary"
              autocomplete="new-password"
              minlength="6"
              required
            />
          </div>

          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">Повторите пароль</label>
            <input
              v-model="confirmPassword"
              type="password"
              placeholder="Повторите пароль"
              class="input-primary"
              autocomplete="new-password"
              minlength="6"
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
            <span v-if="isLoading">Создание аккаунта...</span>
            <span v-else>Зарегистрироваться</span>
          </button>
        </form>

        <div class="glass rounded-[24px] p-4 text-center mt-5">
          <p class="text-dark-300 text-sm">
            Уже есть аккаунт?
            <router-link to="/login" class="text-primary-400 hover:text-primary-300 font-semibold">
              Войти
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { isTelegramMiniApp as detectTelegramMiniApp } from '@/services/telegram'

const router = useRouter()
const authStore = useAuthStore()

const registerForm = ref({
  login: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
})

const confirmPassword = ref('')
const isLoading = ref(false)
const error = ref('')

const isTelegramMiniApp = computed(() => detectTelegramMiniApp())

const handleRegister = async () => {
  error.value = ''

  if (registerForm.value.password.length < 6) {
    error.value = 'Пароль должен быть не короче 6 символов.'
    return
  }

  if (registerForm.value.password !== confirmPassword.value) {
    error.value = 'Пароли не совпадают.'
    return
  }

  isLoading.value = true

  try {
    await authStore.register({
      ...registerForm.value,
      email: registerForm.value.email || null,
      first_name: registerForm.value.first_name || null,
      last_name: registerForm.value.last_name || null,
    })

    await authStore.login(registerForm.value.login, registerForm.value.password)
    router.push(authStore.redirectByRole())
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка при регистрации'
  } finally {
    isLoading.value = false
  }
}
</script>
