<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Overlay -->
    <div 
      class="absolute inset-0 bg-black/80 backdrop-blur-sm"
      @click="closeModal"
    ></div>

    <!-- Модалка -->
    <div 
      class="relative premium-card max-w-4xl w-full max-h-[90vh] overflow-y-auto animate-fade-in"
      @click.stop
    >
      <!-- Кнопка закрытия -->
      <button 
        @click="closeModal"
        class="absolute top-4 right-4 z-10 w-10 h-10 glass-button rounded-full flex items-center justify-center"
      >
        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>

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
          
          <!-- Скидка -->
          <div v-if="product.discount > 0" class="absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
            -{{ product.discount }}%
          </div>
        </div>

        <!-- Контент -->
        <div class="p-6 md:p-8 flex flex-col">
          <h2 class="text-3xl font-bold text-white mb-2">{{ product.name }}</h2>
          <p class="text-dark-400 mb-6">{{ product.description }}</p>

          <!-- Питание -->
          <div class="glass p-4 rounded-2xl mb-6">
            <h3 class="text-sm font-semibold text-dark-300 mb-3">Пищевая ценность (на 100г)</h3>
            <div class="grid grid-cols-4 gap-3">
              <div class="text-center">
                <div class="text-2xl font-bold text-gradient">{{ product.calories }}</div>
                <div class="text-xs text-dark-400">ккал</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-blue-400">{{ product.protein }}г</div>
                <div class="text-xs text-dark-400">белки</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-yellow-400">{{ product.fat }}г</div>
                <div class="text-xs text-dark-400">жиры</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-green-400">{{ product.carbohydrates }}г</div>
                <div class="text-xs text-dark-400">углеводы</div>
              </div>
            </div>
          </div>

          <!-- Состав -->
          <div class="mb-6">
            <h3 class="text-sm font-semibold text-dark-300 mb-2">Состав</h3>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="(ingredient, index) in product.ingredients" 
                :key="index"
                class="glass px-3 py-1.5 rounded-full text-sm text-dark-300"
              >
                {{ ingredient }}
              </span>
            </div>
          </div>

          <!-- Вес порции -->
          <div class="text-dark-400 text-sm mb-6">
            <span class="text-dark-500">Вес порции:</span> {{ product.weight }}г
          </div>

          <!-- Цена и кнопка -->
          <div class="mt-auto flex items-center justify-between">
            <div>
              <div v-if="product.discount > 0" class="flex items-center space-x-3">
                <span class="text-3xl font-bold text-gradient">{{ Math.round(product.price * (1 - product.discount / 100)) }} ₽</span>
                <span class="text-dark-500 line-through">{{ Math.round(product.price) }} ₽</span>
              </div>
              <div v-else class="text-3xl font-bold text-gradient">{{ Math.round(product.price) }} ₽</div>
            </div>
            
            <button 
              @click="handleAddToCart"
              :disabled="isAdding"
              class="btn-primary px-8 py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="isAdding">
                <svg class="animate-spin h-5 w-5 inline" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </span>
              <span v-else>В корзину</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useProductsStore } from '@/stores/products'

const props = defineProps({
  product: {
    type: Object,
    default: null,
  },
  isOpen: {
    type: Boolean,
    default: false,
  },
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

const closeModal = () => {
  emit('close')
}

const handleAddToCart = async () => {
  if (!props.product) return
  
  isAdding.value = true
  try {
    await cartStore.addToCart(props.product.id, 1)
    closeModal()
  } catch (error) {
    console.error('Ошибка при добавлении в корзину:', error)
  } finally {
    isAdding.value = false
  }
}

// Блокируем прокрутку фона когда модалка открыта
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
