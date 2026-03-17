import { defineStore } from 'pinia'
import { authService } from '@/services'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token') || null,
    isLoading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    getUser: (state) => state.user,
    getToken: (state) => state.token,
  },

  actions: {
    async login(login, password) {
      this.isLoading = true
      this.error = null
      try {
        const data = await authService.login(login, password)
        this.token = data.access_token
        
        // Получаем информацию о пользователе из токена или сохраняем логин
        const user = {
          login: login,
          role: 'client' // по умолчанию, можно обновить после получения с бэкенда
        }
        this.setUser(user)
        
        return data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при входе'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async register(userData) {
      this.isLoading = true
      this.error = null
      try {
        const data = await authService.register(userData)
        return data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при регистрации'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    logout() {
      authService.logout()
      this.token = null
      this.user = null
      this.error = null
    },

    setUser(user) {
      this.user = user
      authService.setCurrentUser(user)
    },

    loadUserFromStorage() {
      const user = authService.getCurrentUser()
      if (user) {
        this.user = user
      }
    },

    // Проверка токена с редиректом если невалиден
    checkAuth(redirect = true) {
      if (!this.token) {
        if (redirect) {
          window.location.href = '/login'
        }
        return false
      }
      return true
    },
  },
})
