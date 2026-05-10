<template>
  <div id="app" class="min-h-screen bg-dark-950">
    <Navbar v-if="!isTelegramMiniApp" />
    <main :class="isTelegramMiniApp ? 'pt-0 pb-28' : 'pt-20'">
      <RouterView />
    </main>
    <CartDrawer />
    <MiniAppDock v-if="isTelegramMiniApp" />
    <AIWidget v-if="!isTelegramMiniApp" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterView } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import CartDrawer from '@/components/CartDrawer.vue'
import MiniAppDock from '@/components/MiniAppDock.vue'
import AIWidget from '@/components/AIWidget.vue'
import { isTelegramMiniApp as detectTelegramMiniApp } from '@/services/telegram'

const isTelegramMiniApp = computed(() => detectTelegramMiniApp())
</script>

<style scoped>
#app {
  font-family: 'Inter', system-ui, sans-serif;
}
</style>
