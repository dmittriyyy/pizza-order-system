<template>
  <div class="min-h-screen py-6 px-4">
    <div class="max-w-4xl mx-auto">
      <div class="mb-6">
        <h1 class="text-4xl font-bold text-white">Ещё</h1>
        <p class="text-dark-400 mt-2">Профиль, вход, заказы и дополнительная информация.</p>
      </div>

      <div v-if="!authStore.isAuthenticated" class="space-y-4">
        <button class="btn-primary w-full py-4 text-lg" @click="router.push('/login')">
          Войти
        </button>
        <button class="btn-secondary w-full py-4 text-lg" @click="router.push('/register')">
          Зарегистрироваться
        </button>
        <p class="text-dark-500 text-sm px-1">
          После входа здесь будут доступны профиль, история заказов и персональные настройки.
        </p>
      </div>

      <div v-else class="space-y-4">
        <button v-if="authStore.isAdmin" class="mini-more-card" @click="router.push('/admin')">
          <span class="mini-more-icon">⚙️</span>
          <span>
            <span class="mini-more-title">Админ панель</span>
            <span class="mini-more-subtitle">Заказы, сотрудники, меню и проблемные отзывы</span>
          </span>
        </button>

        <button v-if="authStore.isCook" class="mini-more-card" @click="router.push('/cook/orders')">
          <span class="mini-more-icon">👨‍🍳</span>
          <span>
            <span class="mini-more-title">Панель повара</span>
            <span class="mini-more-subtitle">Готовка и управление статусами кухни</span>
          </span>
        </button>

        <button v-if="authStore.isCourier" class="mini-more-card" @click="router.push('/courier/orders')">
          <span class="mini-more-icon">🚚</span>
          <span>
            <span class="mini-more-title">Панель курьера</span>
            <span class="mini-more-subtitle">Готовые заказы и доставка клиентам</span>
          </span>
        </button>

        <button class="mini-more-card" @click="router.push('/profile')">
          <span class="mini-more-icon">👤</span>
          <span>
            <span class="mini-more-title">Профиль</span>
            <span class="mini-more-subtitle">Личные данные, заказы и отзывы</span>
          </span>
        </button>

        <button class="mini-more-card" @click="router.push('/about')">
          <span class="mini-more-icon">ℹ️</span>
          <span>
            <span class="mini-more-title">О нас</span>
            <span class="mini-more-subtitle">Контакты, адрес и информация о Piazza Pizza</span>
          </span>
        </button>

        <button class="mini-more-card" @click="router.push('/reviews')">
          <span class="mini-more-icon">⭐</span>
          <span>
            <span class="mini-more-title">Отзывы</span>
            <span class="mini-more-subtitle">Публичные отзывы клиентов</span>
          </span>
        </button>

        <button class="mini-more-logout" @click="handleLogout">
          Выйти из аккаунта
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = async () => {
  authStore.logout()
  await router.push('/')
}
</script>

<style scoped>
.mini-more-card {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #fff;
  text-align: left;
}

.mini-more-icon {
  width: 52px;
  height: 52px;
  border-radius: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  background: linear-gradient(135deg, rgba(234, 103, 10, 0.2), rgba(204, 26, 26, 0.12));
}

.mini-more-title {
  display: block;
  font-size: 18px;
  font-weight: 700;
}

.mini-more-subtitle {
  display: block;
  margin-top: 4px;
  font-size: 13px;
  color: #9ca3af;
}

.mini-more-logout {
  width: 100%;
  padding: 16px 18px;
  border-radius: 24px;
  background: rgba(127, 29, 29, 0.18);
  border: 1px solid rgba(248, 113, 113, 0.18);
  color: #f87171;
  font-size: 16px;
  font-weight: 700;
}
</style>
