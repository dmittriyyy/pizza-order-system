<template>
  <!-- Overlay -->
  <div 
    v-if="cartStore.isOpen" 
    class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 transition-opacity"
    @click="cartStore.closeCart()"
  ></div>

  <!-- Drawer -->
  <div 
    :class="[
      'fixed top-0 right-0 h-full w-full max-w-md glass-dark border-l border-dark-700 z-50 transform transition-transform duration-300',
      cartStore.isOpen ? 'translate-x-0' : 'translate-x-full'
    ]"
  >
    <div class="flex flex-col h-full">
      <!-- Заголовок -->
      <div class="flex items-center justify-between p-6 border-b border-dark-700">
        <h2 class="text-2xl font-bold text-white flex items-center space-x-3">
          <svg class="w-6 h-6 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
          </svg>
          <span>Корзина</span>
        </h2>
        <button 
          @click="cartStore.closeCart()"
          class="p-2 hover:bg-white/10 rounded-xl transition-colors"
        >
          <svg class="w-6 h-6 text-dark-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Содержимое -->
      <div class="flex-1 overflow-y-auto p-6">
        <div v-if="cartStore.isEmpty" class="text-center py-12">
          <div class="w-24 h-24 mx-auto mb-4 bg-dark-800 rounded-full flex items-center justify-center">
            <svg class="w-12 h-12 text-dark-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
            </svg>
          </div>
          <p class="text-dark-400 text-lg">Корзина пуста</p>
          <p class="text-dark-500 text-sm mt-2">Добавьте что-нибудь вкусное!</p>
        </div>

        <div v-else class="space-y-4">
          <div 
            v-for="item in cartStore.items" 
            :key="item.product_id"
            class="premium-card p-4 flex items-center space-x-4"
          >
            <img 
              :src="item.image_url || 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=100&h=100&fit=crop'"
              :alt="item.name"
              class="w-20 h-20 rounded-xl object-cover"
            />
            <div class="flex-1">
              <h4 class="text-white font-semibold">{{ item.name }}</h4>
              <p class="text-primary-400 font-bold mt-1">{{ Math.round(item.subtotal) }} ₽</p>
              
              <!-- Контролы количества -->
              <div class="flex items-center space-x-3 mt-2">
                <button 
                  @click="updateQuantity(item.product_id, item.quantity - 1)"
                  class="w-8 h-8 glass-button rounded-lg flex items-center justify-center text-dark-300 hover:text-white transition-colors"
                >
                  -
                </button>
                <span class="text-white font-medium w-8 text-center">{{ item.quantity }}</span>
                <button 
                  @click="updateQuantity(item.product_id, item.quantity + 1)"
                  class="w-8 h-8 glass-button rounded-lg flex items-center justify-center text-dark-300 hover:text-white transition-colors"
                >
                  +
                </button>
                <button 
                  @click="removeFromCart(item.product_id)"
                  class="ml-auto text-red-400 hover:text-red-300 transition-colors text-sm"
                >
                  Удалить
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Футер с итогом -->
      <div v-if="!cartStore.isEmpty" class="border-t border-dark-700 p-6 space-y-4">
        <div class="flex items-center justify-between text-lg">
          <span class="text-dark-400">Итого:</span>
          <span class="text-2xl font-bold text-gradient">{{ Math.round(cartStore.total) }} ₽</span>
        </div>
        
        <button 
          @click="openCheckout"
          :disabled="isCheckingOut"
          class="btn-primary w-full py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isCheckingOut ? 'Оформление...' : 'Оформить заказ' }}
        </button>
      </div>
    </div>
  </div>
  
  <!-- Модальное окно оформления заказа -->
  <CheckoutModal
    :is-open="isCheckoutOpen"
    :total="Math.round(cartStore.total)"
    @close="isCheckoutOpen = false"
    @success="onCheckoutSuccess"
  />
</template>

<script setup>
import { ref, watch } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import CheckoutModal from '@/components/CheckoutModal.vue'

const cartStore = useCartStore()
const authStore = useAuthStore()
const router = useRouter()
const isCheckingOut = ref(false)
const isCheckoutOpen = ref(false)

// Отладка
watch(() => cartStore.isOpen, (newVal) => {
  console.log('CartDrawer: isOpen =', newVal)
}, { immediate: true })

const updateQuantity = async (productId, quantity) => {
  if (quantity < 1) {
    await cartStore.removeFromCart(productId)
  } else {
    await cartStore.updateQuantity(productId, quantity)
  }
}

const removeFromCart = async (productId) => {
  await cartStore.removeFromCart(productId)
}

const openCheckout = () => {
  if (!authStore.isAuthenticated) {
    cartStore.closeCart()
    router.push('/login')
    return
  }
  isCheckoutOpen.value = true
}

const onCheckoutSuccess = () => {
  cartStore.closeCart()
}
</script>
