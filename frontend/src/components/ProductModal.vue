<template>
  <!-- 
    Исправлено: 
    - fixed inset-0 (на весь экран поверх всего)
    - flex items-center justify-center (строго по центру)
    - z-[60] (выше дока и навбара)
  -->
  <div v-if="isOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
    <!-- Overlay -->
    <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="close"></div>

    <!-- Контент модалки (Mobile: Bottom Sheet, Desktop: Center Modal) -->
    <div class="relative glass w-full md:max-w-4xl md:rounded-[30px] rounded-t-[30px] overflow-hidden animate-fade-in max-h-[90vh] flex flex-col z-10">
      
      <!-- Заголовок -->
      <div class="sticky top-0 bg-white/10 md:bg-dark-900/95 backdrop-blur border-b border-white/10 md:border-dark-700 p-4 md:p-6 flex items-center justify-between z-10">
        <h2 class="text-xl md:text-2xl font-bold text-white">🍕 {{ product.name }}</h2>
        <button @click="close" class="w-10 h-10 glass-button rounded-full flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <div class="flex-1 overflow-y-auto">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-0">
          <!-- Изображение -->
          <div class="relative h-64 md:h-full min-h-[300px]">
            <img 
              :src="product.image_url || defaultImage" 
              :alt="product.name"
              class="w-full h-full object-cover"
            />
            <div class="absolute inset-0 bg-gradient-to-t from-dark-900/80 via-transparent to-transparent md:bg-gradient-to-r"></div>
            
            <!-- Бейдж -->
            <span class="absolute top-4 left-4 glass px-4 py-2 rounded-full text-sm font-medium">
              {{ categoryName }}
            </span>
          </div>

          <!-- Контент -->
          <div class="p-4 md:p-8 flex flex-col">
            <p class="text-dark-400 mb-4 md:mb-6 text-sm md:text-base">{{ product.description }}</p>

            <!-- Питание -->
            <div class="glass p-3 md:p-4 rounded-[20px] md:rounded-2xl mb-4 md:mb-6">
              <h3 class="text-xs md:text-sm font-semibold text-dark-300 mb-3">Пищевая ценность (на 100г)</h3>
              <div class="grid grid-cols-4 gap-2 md:gap-3">
                <div class="text-center">
                  <div class="text-xl md:text-2xl font-bold text-gradient">{{ product.calories }}</div>
                  <div class="text-xs text-dark-400">ккал</div>
                </div>
                <div class="text-center">
                  <div class="text-xl md:text-2xl font-bold text-blue-400">{{ product.protein }}г</div>
                  <div class="text-xs text-dark-400">белки</div>
                </div>
                <div class="text-center">
                  <div class="text-xl md:text-2xl font-bold text-yellow-400">{{ product.fat }}г</div>
                  <div class="text-xs text-dark-400">жиры</div>
                </div>
                <div class="text-center">
                  <div class="text-xl md:text-2xl font-bold text-green-400">{{ product.carbohydrates }}г</div>
                  <div class="text-xs text-dark-400">углеводы</div>
                </div>
              </div>
            </div>

            <!-- Цена и кнопка -->
            <div class="mt-auto flex items-center justify-between">
              <div>
                <span class="text-2xl md:text-3xl font-bold text-gradient">{{ Math.round(product.price) }} ₽</span>
              </div>
              
              <button 
                @click="handleAddToCart"
                :disabled="isAdding"
                class="btn-primary px-6 py-3 md:px-8 md:py-4 text-sm md:text-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="isAdding">...</span>
                <span v-else>В корзину</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useProductsStore } from '@/stores/products'

const props = defineProps({
  product: { type: Object, default: null },
  isOpen: { type: Boolean, default: false },
})

const emit = defineEmits(['close'])

const cartStore = useCartStore()
const productsStore = useProductsStore()
const isAdding = ref(false)
const defaultImage = 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500&h=300&fit=crop'

const categoryName = computed(() => {
  if (!props.product?.category_id) return ''
  const category = productsStore.getCategoryById(props.product.category_id)
  return category?.name || ''
})

const close = () => emit('close')

const handleAddToCart = async () => {
  if (!props.product) return
  isAdding.value = true
  try {
    await cartStore.addToCart(props.product.id, 1)
    close()
  } catch (error) {
    console.error('Ошибка:', error)
  } finally {
    isAdding.value = false
  }
}
</script>
