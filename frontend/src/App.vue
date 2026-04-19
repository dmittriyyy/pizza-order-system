<template>
  <div id="app" class="min-h-screen bg-dark-950">
    <Navbar v-if="!isTelegramMiniApp" />
    <main :class="isTelegramMiniApp ? 'pt-0' : 'pt-20'">
      <RouterView />
    </main>
    <CartDrawer />
    <AIWidget v-if="!isTelegramMiniApp" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterView } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import CartDrawer from '@/components/CartDrawer.vue'
import AIWidget from '@/components/AIWidget.vue'
import { isTelegramMiniApp as detectTelegramMiniApp } from '@/services/telegram'

const isTelegramMiniApp = computed(() => detectTelegramMiniApp())
</script>

<style scoped>
#app {
  font-family: 'Inter', system-ui, sans-serif;
}
</style>
