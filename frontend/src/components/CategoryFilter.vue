<template>
  <div class="flex flex-wrap gap-3 justify-center mb-8">
    <!-- Кнопка "Все" -->
    <button
      @click="selectCategory(null)"
      :class="[
        'px-6 py-3 rounded-2xl font-medium transition-all duration-300',
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
        'px-6 py-3 rounded-2xl font-medium transition-all duration-300',
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
