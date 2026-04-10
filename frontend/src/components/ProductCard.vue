<template>
  <!-- Mobile: Extreme rounding (rounded-[30px] via CSS class), Desktop: Standard -->
  <div class="premium-card overflow-hidden group h-full flex flex-col cursor-pointer" @click="openModal">
    <!-- Изображение -->
    <div class="relative h-48 overflow-hidden">
      <img
        :src="product.image_url || defaultImage"
        :alt="product.name"
        class="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-500"
      />
      <div class="absolute inset-0 bg-gradient-to-t from-dark-900/80 to-transparent"></div>

      <!-- Бейдж категории -->
      <span class="absolute top-3 left-3 glass px-3 py-1 rounded-full text-xs font-medium text-white">
        {{ categoryName }}
      </span>
    </div>

    <!-- Контент -->
    <div class="p-4 md:p-5 flex-1 flex flex-col">
      <h3 class="text-lg md:text-xl font-bold text-white mb-2 group-hover:text-primary-400 transition-colors">
        {{ product.name }}
      </h3>
      <p class="text-dark-400 text-xs md:text-sm mb-4 flex-1 line-clamp-2">
        {{ product.description }}
      </p>

      <!-- Цена и кнопка -->
      <div class="flex items-center justify-between mt-auto" @click.stop>
        <div class="flex items-baseline space-x-1">
          <span class="text-xl md:text-2xl font-bold text-gradient">{{ Math.round(product.price) }}</span>
          <span class="text-dark-400 text-xs md:text-sm">₽</span>
        </div>

        <button
          @click="handleAddToCart"
          :disabled="isAdding"
          class="btn-primary px-4 py-2 md:px-5 md:py-2.5 text-xs md:text-sm flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="isAdding">
            <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </span>
          <span v-else>В корзину</span>
        </button>
      </div>
    </div>
  </div>
  
  <!-- Модалка -->
  <ProductModal 
    :product="product" 
    :is-open="isModalOpen" 
    @close="isModalOpen = false" 
  />
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useProductsStore } from '@/stores/products'
import ProductModal from '@/components/ProductModal.vue'

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
})

const cartStore = useCartStore()
const productsStore = useProductsStore()
const isAdding = ref(false)
const isModalOpen = ref(false)

const defaultImage = 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500&h=300&fit=crop'

const categoryName = computed(() => {
  const category = productsStore.getCategoryById(props.product.category_id)
  return category?.name || 'Категория'
})

const openModal = () => {
  isModalOpen.value = true
}

const handleAddToCart = async () => {
  isAdding.value = true
  try {
    await cartStore.addToCart(props.product.id, 1)
  } catch (error) {
    console.error('Ошибка при добавлении в корзину:', error)
  } finally {
    isAdding.value = false
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
