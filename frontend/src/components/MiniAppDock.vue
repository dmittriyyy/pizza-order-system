<template>
  <nav class="mini-dock-wrap">
    <div class="mini-dock">
      <button type="button" class="mini-dock-item" @click="goToMenu">
        <span class="mini-dock-icon">🍕</span>
        <span class="mini-dock-label">Меню</span>
      </button>

      <button type="button" class="mini-dock-item" :class="{ 'mini-dock-item--active': isRouteActive('/mini-ai') }" @click="goToAI">
        <span class="mini-dock-icon">🤖</span>
        <span class="mini-dock-label">Консультант</span>
      </button>

      <button type="button" class="mini-dock-item" :class="{ 'mini-dock-item--active': isRouteActive('/mini-support') }" @click="goToSupport">
        <span class="mini-dock-icon">🛟</span>
        <span class="mini-dock-label">Поддержка</span>
      </button>

      <button type="button" class="mini-dock-item mini-dock-item--cart" :class="{ 'mini-dock-item--active': cartStore.isOpen }" @click="openCart">
        <span class="mini-dock-icon">🛒</span>
        <span class="mini-dock-label">Корзина</span>
        <span v-if="cartStore.itemsCount > 0" class="mini-dock-badge">{{ cartStore.itemsCount }}</span>
      </button>

      <button type="button" class="mini-dock-item" :class="{ 'mini-dock-item--active': isRouteActive('/more') || isRouteActive('/profile') || isRouteActive('/login') || isRouteActive('/register') }" @click="goToMore">
        <span class="mini-dock-icon">{{ authStore.isAuthenticated ? '👤' : '☰' }}</span>
        <span class="mini-dock-label">Ещё</span>
      </button>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()
const isRouteActive = (path) => router.currentRoute.value.path === path

const goToMenu = async () => {
  if (router.currentRoute.value.path !== '/') {
    await router.push('/')
  }

  requestAnimationFrame(() => {
    document.getElementById('menu')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

const goToAI = async () => {
  await router.push('/mini-ai')
}

const goToSupport = async () => {
  await router.push('/mini-support')
}

const openCart = async () => {
  if (!authStore.isAuthenticated) {
    await router.push('/login')
    return
  }

  cartStore.openCart()
}

const goToMore = async () => {
  await router.push('/more')
}
</script>

<style scoped>
.mini-dock-wrap {
  position: fixed;
  left: 12px;
  right: 12px;
  bottom: 12px;
  z-index: 55;
  padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 4px);
}

.mini-dock {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
  padding: 10px;
  border-radius: 30px;
  background: linear-gradient(180deg, rgba(39, 39, 42, 0.94), rgba(17, 24, 39, 0.98));
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(18px);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.35);
}

.mini-dock-item {
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
  transition: transform 0.18s ease, background-color 0.18s ease, border-color 0.18s ease;
}

.mini-dock-item:active {
  transform: scale(0.97);
}

.mini-dock-item--cart {
  background: linear-gradient(135deg, rgba(234, 103, 10, 0.22), rgba(204, 26, 26, 0.12));
  border-color: rgba(234, 103, 10, 0.24);
}

.mini-dock-item--active {
  border-color: rgba(234, 103, 10, 0.28);
  background: linear-gradient(135deg, rgba(234, 103, 10, 0.16), rgba(204, 26, 26, 0.08));
}

.mini-dock-icon {
  font-size: 20px;
  line-height: 1;
}

.mini-dock-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.mini-dock-badge {
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
</style>
