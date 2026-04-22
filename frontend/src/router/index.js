import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import ProfileView from '@/views/ProfileView.vue'
import AboutView from '@/views/AboutView.vue'
import ReviewsView from '@/views/ReviewsView.vue'

// Role-based views
import CookOrdersView from '@/views/CookOrdersView.vue'
import CourierOrdersView from '@/views/CourierOrdersView.vue'
import AdminDashboardView from '@/views/AdminDashboardView.vue'
import AdminProductsView from '@/views/AdminProductsView.vue'
import AdminEmployeesView from '@/views/AdminEmployeesView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        title: 'Piazza Pizza — Главная',
      },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: {
        title: 'Вход — Piazza Pizza',
        guestOnly: true,
      },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: {
        title: 'Регистрация — Piazza Pizza',
        guestOnly: true,
      },
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: {
        title: 'Профиль — Piazza Pizza',
        requiresAuth: true,
      },
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView,
      meta: {
        title: 'О нас — Piazza Pizza',
      },
    },
    {
      path: '/reviews',
      name: 'reviews',
      component: ReviewsView,
      meta: {
        title: 'Отзывы — Piazza Pizza',
      },
    },
    
    // ==================== РОЛЕВЫЕ МАРШРУТЫ ====================
    
    // Админ
    {
      path: '/admin',
      name: 'admin-dashboard',
      component: AdminDashboardView,
      meta: {
        title: 'Админ панель — Piazza Pizza',
        requiresAuth: true,
        requiresRole: 'admin',
      },
    },
    {
      path: '/admin/products',
      name: 'admin-products',
      component: AdminProductsView,
      meta: {
        title: 'Управление товарами — Piazza Pizza',
        requiresAuth: true,
        requiresRole: 'admin',
      },
    },
    {
      path: '/admin/employees',
      name: 'admin-employees',
      component: AdminEmployeesView,
      meta: {
        title: 'Сотрудники — Piazza Pizza',
        requiresAuth: true,
        requiresRole: 'admin',
      },
    },

    // Повар
    {
      path: '/cook/orders',
      name: 'cook-orders',
      component: CookOrdersView,
      meta: {
        title: 'Заказы на кухне — Piazza Pizza',
        requiresAuth: true,
        requiresRole: 'cook',
      },
    },
    
    // Курьер
    {
      path: '/courier/orders',
      name: 'courier-orders',
      component: CourierOrdersView,
      meta: {
        title: 'Доставка заказов — Piazza Pizza',
        requiresAuth: true,
        requiresRole: 'courier',
      },
    },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  },
})

router.beforeEach(async (to, from, next) => {
  document.title = to.meta.title || 'Piazza Pizza'

  const authStore = useAuthStore()

  // Если есть токен, но пользователь не загружен — пробуем загрузить
  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchCurrentUser()
    } catch (e) {
      console.warn('⚠️ Не удалось загрузить профиль, сбрасываем токен')
      authStore.logout()
    }
  }

  // Проверка авторизации
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  // Если пользователь авторизован и пытается зайти на страницу для гостей
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    next({ name: 'home' })
    return
  }

  // Проверка роли для ролевых маршрутов
  if (to.meta.requiresRole && authStore.isAuthenticated) {
    const userRole = authStore.getUserRole

    // 🔥 АДМИН МОЖЕТ ЗАХОДИТЬ ВЕЗДЕ
    if (userRole === 'admin') {
      next()
      return
    }

    // Проверка соответствия роли
    const requiredRole = to.meta.requiresRole
    if (requiredRole === 'cook' && userRole !== 'cook') {
      next({ name: 'home' })
      return
    }
    if (requiredRole === 'courier' && userRole !== 'courier') {
      next({ name: 'home' })
      return
    }
    if (requiredRole === 'admin' && userRole !== 'admin') {
      next({ name: 'home' })
      return
    }
  }

  next()
})

export default router
