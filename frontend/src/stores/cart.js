import { defineStore } from 'pinia'
import { cartService } from '@/services'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [],
    total: 0,
    itemsCount: 0,
    isLoading: false,
    error: null,
    isOpen: false,
  }),

  getters: {
    getItems: (state) => state.items,
    getTotal: (state) => state.total,
    getItemsCount: (state) => state.itemsCount,
    isEmpty: (state) => state.items.length === 0,
  },

  actions: {
    async fetchCart() {
      // Если нет токена, просто показываем пустую корзину
      if (!localStorage.getItem('access_token')) {
        this.items = []
        this.total = 0
        this.itemsCount = 0
        return
      }
      
      this.isLoading = true
      this.error = null
      try {
        const data = await cartService.get()
        this.items = data.items || []
        this.total = data.total || 0
        this.itemsCount = data.items_count || 0
      } catch (error) {
        // Игнорируем 401 - просто показываем пустую корзину
        this.items = []
        this.total = 0
        this.itemsCount = 0
      } finally {
        this.isLoading = false
      }
    },

    async addToCart(productId, quantity = 1) {
      this.isLoading = true
      this.error = null
      try {
        const data = await cartService.add(productId, quantity)
        this.items = data.items || []
        this.total = data.total || 0
        this.itemsCount = data.items_count || 0
        return data
      } catch (error) {
        const errorMsg = error.response?.data?.detail || 'Ошибка при добавлении в корзину'
        this.error = errorMsg
        
        // Если 401 - предлагаем войти
        if (error.response?.status === 401) {
          alert('Для добавления в корзину необходимо войти. Пожалуйста, войдите в аккаунт.')
        } else {
          alert(errorMsg)
        }
        
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async updateQuantity(productId, quantity) {
      this.isLoading = true
      this.error = null
      try {
        const data = await cartService.update(productId, quantity)
        this.items = data.items || []
        this.total = data.total || 0
        this.itemsCount = data.items_count || 0
        return data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при обновлении корзины'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async removeFromCart(productId) {
      this.isLoading = true
      this.error = null
      try {
        const data = await cartService.remove(productId)
        this.items = data.items || []
        this.total = data.total || 0
        this.itemsCount = data.items_count || 0
        return data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при удалении из корзины'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async clearCart() {
      this.isLoading = true
      this.error = null
      try {
        await cartService.clear()
        this.items = []
        this.total = 0
        this.itemsCount = 0
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при очистке корзины'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    openCart() {
      this.isOpen = true
      this.fetchCart()
    },

    closeCart() {
      this.isOpen = false
    },

    toggleCart() {
      this.isOpen = !this.isOpen
      if (this.isOpen) {
        this.fetchCart()
      }
    },
  },
})
