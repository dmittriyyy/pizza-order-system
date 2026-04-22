<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-7xl mx-auto">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-4xl font-bold text-white mb-2">⚙️ Админ панель</h1>
          <p class="text-dark-400">Полная статистика и управление</p>
        </div>
        <div class="flex items-center space-x-3">
          <router-link to="/admin/products" class="btn-secondary px-6 py-3">
            ✏️ Изменить меню
          </router-link>
          <router-link to="/admin/employees" class="btn-secondary px-6 py-3">
            👥 Сотрудники
          </router-link>
        </div>
      </div>

      <!-- Финансовая статистика -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="premium-card p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-dark-400 text-sm font-medium">Прибыль за сегодня</h3>
            <span class="text-2xl">💰</span>
          </div>
          <div class="text-3xl font-bold text-green-400">{{ stats.todayRevenue }} ₽</div>
          <div class="text-dark-500 text-sm mt-1">{{ stats.todayOrders }} заказов</div>
        </div>

        <div class="premium-card p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-dark-400 text-sm font-medium">Прибыль за месяц</h3>
            <span class="text-2xl">📅</span>
          </div>
          <div class="text-3xl font-bold text-blue-400">{{ stats.monthRevenue }} ₽</div>
          <div class="text-dark-500 text-sm mt-1">{{ stats.monthOrders }} заказов</div>
        </div>

        <div class="premium-card p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-dark-400 text-sm font-medium">Средний чек</h3>
            <span class="text-2xl">📊</span>
          </div>
          <div class="text-3xl font-bold text-primary-400">{{ stats.averageCheck }} ₽</div>
          <div class="text-dark-500 text-sm mt-1">за все время</div>
        </div>
      </div>

      <!-- Статистика по заказам -->
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        <div class="premium-card p-4 text-center">
          <div class="text-2xl font-bold text-blue-400">{{ stats.newOrders }}</div>
          <div class="text-dark-400 text-xs mt-1">Новые</div>
        </div>
        <div class="premium-card p-4 text-center">
          <div class="text-2xl font-bold text-yellow-400">{{ stats.cookingOrders }}</div>
          <div class="text-dark-400 text-xs mt-1">Готовятся</div>
        </div>
        <div class="premium-card p-4 text-center">
          <div class="text-2xl font-bold text-green-400">{{ stats.readyOrders }}</div>
          <div class="text-dark-400 text-xs mt-1">Готовы</div>
        </div>
        <div class="premium-card p-4 text-center">
          <div class="text-2xl font-bold text-purple-400">{{ stats.deliveringOrders }}</div>
          <div class="text-dark-400 text-xs mt-1">В доставке</div>
        </div>
        <div class="premium-card p-4 text-center">
          <div class="text-2xl font-bold text-dark-400">{{ stats.completedOrders }}</div>
          <div class="text-dark-500 text-xs mt-1">Выполнены</div>
        </div>
      </div>

      <!-- Актуальные заказы -->
      <div class="premium-card p-6 mb-8">
        <h2 class="text-2xl font-bold text-white mb-6">🔔 Актуальные заказы</h2>

        <div v-if="activeOrders.length === 0" class="text-center py-8">
          <p class="text-dark-400">Нет активных заказов</p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="order in activeOrders"
            :key="order.id"
            class="glass p-4 rounded-2xl"
          >
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center space-x-3">
                <span class="text-white font-bold">Заказ #{{ order.id }}</span>
                <span :class="[
                  'px-3 py-1 rounded-full text-xs font-medium',
                  getStatusClass(order.status)
                ]">
                  {{ translateStatus(order.status) }}
                </span>
              </div>
              <div class="flex items-center space-x-4">
                <span class="text-primary-400 font-bold">{{ Math.round(order.total_price) }} ₽</span>
                <span class="text-dark-400 text-sm">{{ formatTime(order.created_at) }}</span>
              </div>
            </div>

            <div class="text-sm text-dark-400 mb-2">
              <span>📍</span> {{ order.delivery_address }}
            </div>

            <div class="text-xs text-dark-500">
              {{ order.items?.length || 0 }} позиций • {{ order.customer_name || 'Клиент' }} • {{ order.customer_phone || 'нет телефона' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Выполненные заказы (последние 10) -->
      <div class="premium-card p-6">
        <h2 class="text-2xl font-bold text-white mb-6">✅ Выполненные заказы</h2>

        <div v-if="completedOrders.length === 0" class="text-center py-8">
          <p class="text-dark-400">Нет выполненных заказов</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-dark-700">
                <th class="text-left py-3 px-4 text-dark-300 font-medium">№</th>
                <th class="text-left py-3 px-4 text-dark-300 font-medium">Сумма</th>
                <th class="text-left py-3 px-4 text-dark-300 font-medium">Адрес</th>
                <th class="text-left py-3 px-4 text-dark-300 font-medium">Время</th>
                <th class="text-left py-3 px-4 text-dark-300 font-medium">Статус</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="order in completedOrders"
                :key="order.id"
                class="border-b border-dark-800 hover:bg-dark-800/50"
              >
                <td class="py-3 px-4 text-white font-bold">#{{ order.id }}</td>
                <td class="py-3 px-4 text-primary-400 font-bold">{{ Math.round(order.total_price) }} ₽</td>
                <td class="py-3 px-4 text-dark-400 text-sm max-w-xs truncate">{{ order.delivery_address }}</td>
                <td class="py-3 px-4 text-dark-400 text-sm">{{ formatDateTime(order.created_at) }}</td>
                <td class="py-3 px-4">
                  <span :class="[
                    'px-3 py-1 rounded-full text-xs font-medium',
                    getStatusClass(order.status)
                  ]">
                    {{ translateStatus(order.status) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="premium-card p-6 mt-8">
        <h2 class="text-2xl font-bold text-white mb-6">⚠️ Проблемные отзывы</h2>

        <div v-if="problematicFeedback.length === 0" class="text-center py-8">
          <p class="text-dark-400">Пока нет отзывов, требующих внимания администратора</p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="item in problematicFeedback"
            :key="item.id"
            class="glass p-4 rounded-2xl border border-red-500/20"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-3">
                <span class="text-white font-bold">Заказ #{{ item.order_id }}</span>
                <span class="px-3 py-1 rounded-full text-xs font-medium bg-red-500/20 text-red-400">
                  Требует внимания
                </span>
              </div>
              <span class="text-dark-400 text-sm">{{ item.user_login || 'Пользователь' }}</span>
            </div>
            <div class="text-primary-400 text-sm mb-2">{{ renderStars(item.rating) }}</div>
            <p class="text-dark-300 text-sm mb-2">
              {{ item.comment || 'Клиент оставил низкую оценку без комментария.' }}
            </p>
            <p class="text-dark-500 text-xs">{{ formatDateTime(item.created_at) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

const stats = ref({
  todayRevenue: 0,
  todayOrders: 0,
  monthRevenue: 0,
  monthOrders: 0,
  averageCheck: 0,
  newOrders: 0,
  cookingOrders: 0,
  readyOrders: 0,
  deliveringOrders: 0,
  completedOrders: 0,
})

const activeOrders = ref([])
const completedOrders = ref([])
const problematicFeedback = ref([])

const getStatusClass = (status) => {
  const classes = {
    created: 'bg-blue-500/20 text-blue-400',
    paid: 'bg-blue-500/20 text-blue-400',
    cooking: 'bg-yellow-500/20 text-yellow-400',
    ready: 'bg-green-500/20 text-green-400',
    delivering: 'bg-purple-500/20 text-purple-400',
    completed: 'bg-green-500/20 text-green-400',
    cancelled: 'bg-red-500/20 text-red-400',
  }
  return classes[status] || 'bg-gray-500/20 text-gray-400'
}

const translateStatus = (status) => {
  const translations = {
    created: 'Новый',
    paid: 'Оплачен',
    cooking: 'Готовится',
    ready: 'Готов',
    delivering: 'Доставляется',
    completed: 'Завершён',
    cancelled: 'Отменён',
  }
  return translations[status] || status
}

const formatTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('ru-RU', {
    day: 'numeric',
    month: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const renderStars = (rating) => '★'.repeat(rating) + '☆'.repeat(5 - rating)

const fetchStats = async () => {
  try {
    const response = await api.get('/api/orders/admin/all', {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    const allOrders = response.data

    // Считаем статистику
    const now = new Date()
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1)

    let todayRevenue = 0
    let todayOrders = 0
    let monthRevenue = 0
    let monthOrders = 0
    let totalRevenue = 0
    let totalOrders = 0

    const statusCounts = {
      created: 0,
      paid: 0,
      cooking: 0,
      ready: 0,
      delivering: 0,
      completed: 0,
      cancelled: 0,
    }

    allOrders.forEach(order => {
      const orderDate = new Date(order.created_at)
      const price = order.total_price || 0

      // Сегодня
      if (orderDate >= todayStart) {
        todayRevenue += price
        todayOrders++
      }

      // Этот месяц
      if (orderDate >= monthStart) {
        monthRevenue += price
        monthOrders++
      }

      // Всего
      if (order.status === 'completed') {
        totalRevenue += price
        totalOrders++
      }

      // По статусам
      statusCounts[order.status] = (statusCounts[order.status] || 0) + 1
    })

    stats.value = {
      todayRevenue: Math.round(todayRevenue),
      todayOrders,
      monthRevenue: Math.round(monthRevenue),
      monthOrders,
      averageCheck: totalOrders > 0 ? Math.round(totalRevenue / totalOrders) : 0,
      newOrders: statusCounts.created + statusCounts.paid,
      cookingOrders: statusCounts.cooking,
      readyOrders: statusCounts.ready,
      deliveringOrders: statusCounts.delivering,
      completedOrders: statusCounts.completed,
    }

    // Разделяем заказы на активные и выполненные
    activeOrders.value = allOrders.filter(o => 
      !['completed', 'cancelled'].includes(o.status)
    ).sort((a, b) => new Date(b.created_at) - new Date(a.created_at))

    completedOrders.value = allOrders.filter(o => 
      ['completed', 'cancelled'].includes(o.status)
    ).sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 10)

  } catch (error) {
    console.error('Ошибка при загрузке статистики:', error)
  }
}

const fetchProblematicFeedback = async () => {
  try {
    const response = await api.get('/api/feedback/admin/problematic', {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    problematicFeedback.value = response.data || []
  } catch (error) {
    console.error('Ошибка при загрузке проблемных отзывов:', error)
  }
}

onMounted(() => {
  if (!authStore.isAuthenticated || !authStore.isAdmin) {
    router.push('/')
    return
  }
  fetchStats()
  fetchProblematicFeedback()
  // Автообновление каждые 30 секунд
  setInterval(() => {
    fetchStats()
    fetchProblematicFeedback()
  }, 30000)
})
</script>
