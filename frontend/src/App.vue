<template>
  <div id="app" class="min-h-screen bg-dark-950">
    <Navbar v-if="!isTelegramMiniApp" />
    <main :class="shouldShowMiniDock ? 'pt-0 pb-28' : (isTelegramMiniApp ? 'pt-0 pb-6' : 'pt-20')">
      <RouterView />
    </main>
    <CartDrawer />
    <MiniAppDock v-if="shouldShowMiniDock" />
    <AIWidget v-if="!isTelegramMiniApp" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import CartDrawer from '@/components/CartDrawer.vue'
import MiniAppDock from '@/components/MiniAppDock.vue'
import AIWidget from '@/components/AIWidget.vue'
import { isTelegramMiniApp as detectTelegramMiniApp } from '@/services/telegram'
import { useCartStore } from '@/stores/cart'

const route = useRoute()
const cartStore = useCartStore()
const isTelegramMiniApp = computed(() => detectTelegramMiniApp())
const hiddenDockRoutes = new Set(['login', 'register'])
const shouldShowMiniDock = computed(() => {
  if (!isTelegramMiniApp.value) return false
  if (cartStore.isOpen) return false
  return !hiddenDockRoutes.has(route.name)
})
</script>

<style scoped>
#app {
  font-family: 'Inter', system-ui, sans-serif;
}
</style>
