<template>
  <div id="app" class="min-h-screen bg-dark-950">
    <Navbar />
    <main class="pt-20">
      <RouterView />
    </main>
    <CartDrawer />
    <AIWidget />
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import CartDrawer from '@/components/CartDrawer.vue'
import AIWidget from '@/components/AIWidget.vue'
</script>

<style scoped>
#app {
  font-family: 'Inter', system-ui, sans-serif;
}
</style>
