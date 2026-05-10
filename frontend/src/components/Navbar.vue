<template>
  <nav>
    <div class="hidden md:block fixed top-0 left-0 right-0 z-[50] bg-dark-900/90 border-b border-dark-700 backdrop-blur-md">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-20">
          <router-link to="/" class="flex items-center space-x-3 group shrink-0">
            <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center transform group-hover:scale-110 transition-transform duration-300">
              <span class="text-white text-xl">🍕</span>
            </div>
            <span class="text-xl font-bold text-gradient">Piazza Pizza</span>
          </router-link>

          <div class="flex items-center space-x-8">
            <router-link to="/" class="text-dark-300 hover:text-primary-400 transition-colors duration-300 font-medium">Меню</router-link>
            <router-link to="/about" class="text-dark-300 hover:text-primary-400 transition-colors duration-300 font-medium">О нас</router-link>

            <router-link v-if="authStore.isCook" to="/cook/orders" class="text-yellow-400 hover:text-yellow-300 transition-colors duration-300 font-medium flex items-center gap-1">
              👨‍🍳 Кухня
            </router-link>
            <router-link v-if="authStore.isCourier" to="/courier/orders" class="text-purple-400 hover:text-purple-300 transition-colors duration-300 font-medium flex items-center gap-1">
              🚚 Доставка
            </router-link>
            <router-link v-if="authStore.isAdmin" to="/admin" class="text-blue-400 hover:text-blue-300 transition-colors duration-300 font-medium flex items-center gap-1">
              ⚙️ Админка
            </router-link>
          </div>

          <div class="flex items-center space-x-4">
            <button @click="cartStore.toggleCart()" class="relative glass-button p-3 group">
              <svg class="w-6 h-6 text-dark-300 group-hover:text-primary-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
              </svg>
              <span v-if="cartStore.itemsCount > 0" class="absolute -top-1 -right-1 w-5 h-5 bg-primary-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                {{ cartStore.itemsCount }}
              </span>
            </button>

            <template v-if="authStore.isAuthenticated">
              <router-link to="/profile" class="glass-button p-3">👤</router-link>
              <button @click="authStore.logout" class="glass-button px-4 py-2 text-sm text-dark-300 hover:text-primary-400 transition-colors">
                Выход
              </button>
            </template>
            <template v-else>
              <router-link to="/login" class="btn-primary px-6 py-3">
                Войти
              </router-link>
            </template>
          </div>
        </div>
      </div>
    </div>

    <div class="md:hidden fixed left-4 right-4 bottom-4 z-[50] safe-area-bottom">
      <div class="mobile-dock">
        <router-link to="/" class="mobile-dock-item" :class="{ 'mobile-dock-item--active': isActive('/') }">
          <span class="mobile-dock-icon">🍕</span>
          <span class="mobile-dock-label">Меню</span>
        </router-link>

        <router-link to="/about" class="mobile-dock-item" :class="{ 'mobile-dock-item--active': isActive('/about') }">
          <span class="mobile-dock-icon">ℹ️</span>
          <span class="mobile-dock-label">О нас</span>
        </router-link>

        <button type="button" class="mobile-dock-item" @click="cartStore.toggleCart()">
          <span class="mobile-dock-icon">🛒</span>
          <span class="mobile-dock-label">Корзина</span>
          <span v-if="cartStore.itemsCount > 0" class="mobile-dock-badge">{{ cartStore.itemsCount }}</span>
        </button>

        <router-link
          :to="authStore.isAuthenticated ? '/profile' : '/login'"
          class="mobile-dock-item"
          :class="{ 'mobile-dock-item--active': isActive('/profile') || isActive('/login') || isActive('/register') }"
        >
          <span class="mobile-dock-icon">{{ authStore.isAuthenticated ? '👤' : '🔐' }}</span>
          <span class="mobile-dock-label">{{ authStore.isAuthenticated ? 'Профиль' : 'Войти' }}</span>
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'

const route = useRoute()
const authStore = useAuthStore()
const cartStore = useCartStore()

const isActive = (path) => route.path === path

authStore.loadUserFromStorage()
</script>

<style scoped>
.mobile-dock {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  padding: 10px;
  border-radius: 30px;
  background: linear-gradient(180deg, rgba(39, 39, 42, 0.94), rgba(17, 24, 39, 0.98));
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(18px);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.35);
}

.mobile-dock-item {
  position: relative;
  min-height: 68px;
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.03);
  color: #f3f4f6;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.mobile-dock-item--active {
  border-color: rgba(234, 103, 10, 0.28);
  background: linear-gradient(135deg, rgba(234, 103, 10, 0.16), rgba(204, 26, 26, 0.08));
}

.mobile-dock-icon {
  font-size: 20px;
  line-height: 1;
}

.mobile-dock-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.mobile-dock-badge {
  position: absolute;
  top: 10px;
  right: 12px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 999px;
  background: #ea670a;
  color: #fff;
  font-size: 10px;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom);
}
</style>
