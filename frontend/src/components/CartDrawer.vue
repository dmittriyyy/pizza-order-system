<template>
  <!-- Mobile: Bottom Sheet, Desktop: Center Modal -->
  <div v-if="cartStore.isOpen" class="fixed inset-0 z-50 flex items-end md:items-center justify-center">
    <!-- Overlay -->
    <div 
      class="absolute inset-0 bg-black/60 backdrop-blur-sm"
      @click="cartStore.closeCart()"
    ></div>

    <!-- Drawer Content -->
    <div class="relative bg-white/10 md:bg-dark-800 backdrop-blur-xl md:backdrop-blur-none border border-white/20 md:border-dark-700 w-full md:max-w-2xl rounded-t-[30px] md:rounded-[30px] overflow-hidden animate-fade-in max-h-[95vh] md:max-h-[90vh] flex flex-col safe-bottom">
      
      <!-- Header -->
      <div class="sticky top-0 bg-white/10 md:bg-dark-900/95 backdrop-blur border-b border-white/10 md:border-dark-700 p-4 md:p-6 flex items-center justify-between z-10">
        <h2 class="text-xl md:text-2xl font-bold text-white">🛒 Корзина</h2>
        <button @click="cartStore.closeCart()" class="w-10 h-10 glass-button rounded-full flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Body -->
      <div class="flex-1 overflow-y-auto p-4 md:p-6">
        <div v-if="cartStore.isEmpty" class="text-center py-12">
          <div class="w-20 h-20 mx-auto mb-4 bg-white/5 md:bg-dark-800 rounded-full flex items-center justify-center">
            <svg class="w-10 h-10 text-dark-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
            class="glass p-4 rounded-[20px] md:rounded-2xl flex items-center space-x-4"
          >
            <img 
              :src="item.image_url || 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=100&h=100&fit=crop'"
              :alt="item.name"
              class="w-16 h-16 md:w-20 md:h-20 rounded-xl object-cover"
            />
            <div class="flex-1">
              <h4 class="text-white font-semibold text-sm md:text-base">{{ item.name }}</h4>
              <p class="text-primary-400 font-bold mt-1">{{ Math.round(item.subtotal) }} ₽</p>
              
              <!-- Quantity Controls -->
              <div class="flex items-center space-x-3 mt-2">
                <button 
                  @click="updateQuantity(item.product_id, item.quantity - 1)"
                  class="w-8 h-8 glass-button rounded-lg flex items-center justify-center text-dark-300 hover:text-white transition-colors text-sm"
                >
                  -
                </button>
                <span class="text-white font-medium w-8 text-center">{{ item.quantity }}</span>
                <button 
                  @click="updateQuantity(item.product_id, item.quantity + 1)"
                  class="w-8 h-8 glass-button rounded-lg flex items-center justify-center text-dark-300 hover:text-white transition-colors text-sm"
                >
                  +
                </button>
                <button 
                  @click="removeFromCart(item.product_id)"
                  class="ml-auto text-red-400 hover:text-red-300 transition-colors text-xs"
                >
                  Удалить
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div v-if="!cartStore.isEmpty" class="border-t border-white/10 md:border-dark-700 p-4 md:p-6 space-y-4 bg-white/5 md:bg-dark-900/50 backdrop-blur">
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

  <!-- Checkout Modal -->
  <CheckoutModal
    :is-open="isCheckoutOpen"
    :total="Math.round(cartStore.total)"
    @close="isCheckoutOpen = false"
    @success="onCheckoutSuccess"
  />
</template>

<script setup>
import { ref } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import CheckoutModal from '@/components/CheckoutModal.vue'

const cartStore = useCartStore()
const authStore = useAuthStore()
const router = useRouter()
const isCheckingOut = ref(false)
const isCheckoutOpen = ref(false)

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

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (min-width: 768px) {
  .animate-fade-in {
    animation: fadeInDesktop 0.3s ease-out;
  }
  @keyframes fadeInDesktop {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
  }
}

.safe-bottom {
  padding-bottom: env(safe-area-inset-bottom);
}
</style>
