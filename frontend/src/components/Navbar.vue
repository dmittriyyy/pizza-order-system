<template>
  <nav class="
    fixed z-[50] 
    md:top-0 md:bottom-auto md:left-0 md:right-0 md:rounded-none md:bg-dark-900/90 md:border-b md:border-dark-700 md:backdrop-blur-md
    bottom-4 left-4 right-4 rounded-[30px] 
    bg-[#CC1A1A2E] backdrop-blur-xl border border-[#33EA670A] shadow-2xl
    transition-all duration-300
    safe-area-bottom
  ">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16 md:h-20">

        <!-- Логотип -->
        <router-link to="/" class="flex items-center space-x-3 group shrink-0">
          <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center transform group-hover:scale-110 transition-transform duration-300">
            <span class="text-white text-xl">🍕</span>
          </div>
          <span class="text-xl font-bold text-gradient hidden sm:block">Piazza Pizza</span>
        </router-link>

        <!-- Основные ссылки (Всегда видны) -->
        <div class="flex items-center space-x-6 md:space-x-8">
          <router-link to="/" class="text-dark-300 hover:text-primary-400 transition-colors duration-300 font-medium">Меню</router-link>
          <router-link to="/about" class="text-dark-300 hover:text-primary-400 transition-colors duration-300 font-medium">О нас</router-link>

          <!-- Ролевые ссылки (Только для авторизованных с нужной ролью) -->
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

        <!-- Правая часть -->
        <div class="flex items-center space-x-4">
          <!-- Корзина -->
          <button 
            @click="cartStore.toggleCart()"
            class="relative glass-button p-3 group hidden md:flex"
          >
            <svg class="w-6 h-6 text-dark-300 group-hover:text-primary-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
            </svg>
            <span v-if="cartStore.itemsCount > 0" class="absolute -top-1 -right-1 w-5 h-5 bg-primary-500 text-white text-xs font-bold rounded-full flex items-center justify-center animate-pulse-slow">
              {{ cartStore.itemsCount }}
            </span>
          </button>

          <!-- Профиль/Вход -->
          <template v-if="authStore.isAuthenticated">
            <router-link to="/profile" class="glass-button p-3 hidden md:flex">
               👤
            </router-link>
            <button @click="authStore.logout" class="glass-button px-4 py-2 text-sm text-dark-300 hover:text-primary-400 transition-colors hidden md:block">
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
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'

const authStore = useAuthStore()
const cartStore = useCartStore()

// Загружаем профиль при старте
authStore.loadUserFromStorage()
</script>