<template>
  <nav class="fixed top-0 left-0 right-0 z-50 glass-dark border-b border-dark-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-20">
        <!-- Логотип -->
        <router-link to="/" class="flex items-center space-x-3 group">
          <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center transform group-hover:scale-110 transition-transform duration-300">
            <span class="text-white text-xl">🍕</span>
          </div>
          <span class="text-xl font-bold text-gradient">Velo Pizza</span>
        </router-link>

        <!-- Навигация -->
        <div class="hidden md:flex items-center space-x-8">
          <router-link to="/" class="text-dark-300 hover:text-primary-400 transition-colors duration-300 font-medium">
            Меню
          </router-link>
          <router-link to="/about" class="text-dark-300 hover:text-primary-400 transition-colors duration-300 font-medium">
            О нас
          </router-link>
        </div>

        <!-- Правая часть -->
        <div class="flex items-center space-x-4">
          <!-- Кнопка корзины -->
          <button 
            @click="cartStore.toggleCart()"
            class="relative glass-button p-3 group"
          >
            <svg class="w-6 h-6 text-dark-300 group-hover:text-primary-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
            </svg>
            <span 
              v-if="cartStore.itemsCount > 0"
              class="absolute -top-1 -right-1 w-5 h-5 bg-primary-500 text-white text-xs font-bold rounded-full flex items-center justify-center animate-pulse-slow"
            >
              {{ cartStore.itemsCount }}
            </span>
          </button>

          <!-- Кнопка входа/профиля -->
          <template v-if="authStore.isAuthenticated">
            <router-link to="/profile" class="glass-button p-3">
              <svg class="w-6 h-6 text-dark-300 hover:text-primary-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
              </svg>
            </router-link>
            <button @click="handleLogout" class="glass-button px-4 py-2 text-sm text-dark-300 hover:text-primary-400 transition-colors">
              Выход
            </button>
          </template>
          <template v-else>
            <router-link to="/login" class="btn-primary">
              Войти
            </router-link>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'

const cartStore = useCartStore()
const authStore = useAuthStore()

const handleLogout = () => {
  authStore.logout()
  window.location.href = '/'
}
</script>
