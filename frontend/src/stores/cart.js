import { defineStore } from 'pinia'
import { cartService } from '@/services'
import { useAuthStore } from '@/stores/auth'
import { canUseTelegramAuth, getTelegramWebApp } from '@/services/telegram'

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
    _applyCartData(data) {
      this.items = data.items || []
      this.total = data.total || 0
      this.itemsCount = data.items_count || 0
    },

    async _tryRecoverAuth() {
      const authStore = useAuthStore()

      if (canUseTelegramAuth()) {
        const initData = getTelegramWebApp()?.initData
        if (initData) {
          try {
            await authStore.telegramLogin(initData)
            return true
          } catch (error) {
            console.error('❌ Не удалось восстановить сессию через Telegram:', error)
          }
        }
      }

      if (authStore.token) {
        try {
          await authStore.fetchCurrentUser()
          return true
        } catch (error) {
          console.error('❌ Не удалось восстановить токен через /me:', error)
        }
      }

      authStore.logout()
      return false
    },

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
        this._applyCartData(data)
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
        this._applyCartData(data)
        return data
      } catch (error) {
        if (error.response?.status === 401) {
          const recovered = await this._tryRecoverAuth()
          if (recovered) {
            const retryData = await cartService.add(productId, quantity)
            this._applyCartData(retryData)
            return retryData
          }

          this.error = 'Сессия неактивна. Войдите снова.'
          alert('Сессия неактивна. Откройте Войти или Профиль в нижнем меню.')
          throw error
        }

        const errorMsg = error.response?.data?.detail || 'Ошибка при добавлении в корзину'
        this.error = errorMsg
        alert(errorMsg)
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
