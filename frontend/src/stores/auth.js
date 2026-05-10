import { defineStore } from 'pinia'
import { authService } from '@/services'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token') || null,
    isLoading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    getUser: (state) => state.user,
    getToken: (state) => state.token,
    getUserRole: (state) => state.user?.role || 'client',
    isAdmin: (state) => state.user?.role === 'admin',
    isCook: (state) => state.user?.role === 'cook' || state.user?.role === 'admin',
    isCourier: (state) => state.user?.role === 'courier' || state.user?.role === 'admin',
  },

  actions: {
    async login(login, password) {
      this.isLoading = true
      this.error = null
      try {
        const data = await authService.login(login, password)
        this.token = data.access_token

        // Получаем информацию о пользователе из бэкенда
        const user = await this.fetchCurrentUser()
        this.setUser(user)

        console.log('✅ Вход успешен. Токен:', data.access_token.substring(0, 20) + '...')
        console.log('✅ Пользователь:', user)

        return data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка при входе'
        console.error('❌ Ошибка входа:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async fetchCurrentUser() {
      try {
        const response = await api.get('/api/auth/me')
        if (response.data) {
          const user = response.data
          console.log('✅ Данные пользователя с сервера:', user)
          this.user = user
          authService.setCurrentUser(user)
          return user
        }
      } catch (e) {
        console.error('❌ Ошибка при получении профиля:', e)
      }
      this.logout()
      throw new Error('AUTH_INVALID')
    },

    async telegramLogin(initData) {
      this.isLoading = true
      this.error = null
      try {
        const data = await authService.telegramLogin(initData)
        this.token = data.access_token
        this.setUser(data.user)
        return data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка входа через Telegram'
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

    checkAuth(redirect = true) {
      if (!this.token) {
        if (redirect) {
          window.location.href = '/login'
        }
        return false
      }
      return true
    },

    redirectByRole() {
      if (!this.user) return '/'

      const role = this.user.role
      switch (role) {
        case 'admin':
          return '/admin'
        case 'cook':
          return '/cook/orders'
        case 'courier':
          return '/courier/orders'
        default:
          return '/'
      }
    },
  },
})
