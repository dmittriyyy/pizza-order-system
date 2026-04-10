<template>
  <!-- Mobile: Horizontal Scroll, Desktop: Center Wrap -->
  <div class="flex md:flex-wrap md:justify-center gap-3 mb-6 md:mb-8 overflow-x-auto md:overflow-visible pb-2 md:pb-0 scrollbar-hide">
    <!-- Кнопка "Все" -->
    <button
      @click="selectCategory(null)"
      :class="[
        'px-4 md:px-6 py-2 md:py-3 rounded-[20px] md:rounded-2xl font-medium text-sm md:text-base whitespace-nowrap transition-all duration-300',
        selectedCategory === null
          ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-500/25'
          : 'glass text-dark-300 hover:text-white hover:bg-white/20'
      ]"
    >
      Все
    </button>

    <!-- Кнопки категорий -->
    <button
      v-for="category in categories"
      :key="category.id"
      @click="selectCategory(category.id)"
      :class="[
        'px-4 md:px-6 py-2 md:py-3 rounded-[20px] md:rounded-2xl font-medium text-sm md:text-base whitespace-nowrap transition-all duration-300',
        selectedCategory === category.id
          ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-500/25'
          : 'glass text-dark-300 hover:text-white hover:bg-white/20'
      ]"
    >
      {{ category.name }}
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useProductsStore } from '@/stores/products'

const productsStore = useProductsStore()

const categories = computed(() => productsStore.categories)
const selectedCategory = computed(() => productsStore.selectedCategory)

const selectCategory = (categoryId) => {
  productsStore.selectCategory(categoryId)
}
</script>
