import { defineStore } from 'pinia'
import { productService, categoryService } from '@/services'

export const useProductsStore = defineStore('products', {
  state: () => ({
    products: [],
    categories: [],
    selectedCategory: null,
    isLoading: false,
    error: null,
  }),

  getters: {
    getProducts: (state) => state.products,
    getCategories: (state) => state.categories,
    getSelectedCategory: (state) => state.selectedCategory,
    
    filteredProducts(state) {
      if (!state.selectedCategory) {
        return state.products
      }
      return state.products.filter(p => p.category_id === state.selectedCategory)
    },
    
    getProductById: (state) => (id) => {
      return state.products.find(p => p.id === id)
    },
    
    getCategoryById: (state) => (id) => {
      return state.categories.find(c => c.id === id)
    },
  },

  actions: {
    async fetchProducts() {
      this.isLoading = true
      this.error = null
      try {
        const data = await productService.getAll()
        // Сервис уже вернул массив, просто сохраняем его
        this.products = Array.isArray(data) ? data : []
        console.log('✅ Товары загружены:', this.products.length)
      } catch (error) {
        console.error('❌ Ошибка загрузки продуктов:', error)
        this.error = error.response?.data?.detail || 'Ошибка при загрузке продуктов'
      } finally {
        this.isLoading = false
      }
    },

    async fetchCategories() {
      this.isLoading = true
      this.error = null
      try {
        const data = await categoryService.getAll()
        this.categories = data || []
        console.log('✅ Категории загружены:', this.categories.length)
      } catch (error) {
        console.error('❌ Ошибка загрузки категорий:', error)
        this.error = error.response?.data?.detail || 'Ошибка при загрузке категорий'
      } finally {
        this.isLoading = false
      }
    },

    async fetchProductsByCategory(categoryId) {
      this.isLoading = true
      this.error = null
      try {
        const data = await productService.getByCategory(categoryId)
        this.products = Array.isArray(data) ? data : []
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при загрузке продуктов'
      } finally {
        this.isLoading = false
      }
    },

    selectCategory(categoryId) {
      this.selectedCategory = categoryId
    },

    clearCategory() {
      this.selectedCategory = null
    },

    async initialize() {
      await Promise.all([
        this.fetchCategories(),
        this.fetchProducts(),
      ])
    },
  },
})
