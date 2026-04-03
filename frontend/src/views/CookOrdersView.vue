<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-6xl mx-auto">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-4xl font-bold text-white mb-2">👨‍🍳 Заказы на кухне</h1>
          <p class="text-dark-400">Управляйте приготовлением заказов</p>
        </div>
        <div class="flex items-center space-x-3">
          <span class="glass px-4 py-2 rounded-xl text-sm">
            <span class="text-yellow-400 font-bold">{{ orders.length }}</span>
            <span class="text-dark-400 ml-2">в работе</span>
          </span>
        </div>
      </div>

      <!-- Загрузка -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="inline-block w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
        <p class="text-dark-400 mt-4">Загрузка заказов...</p>
      </div>

      <!-- Нет заказов -->
      <div v-else-if="orders.length === 0" class="text-center py-12">
        <div class="w-24 h-24 mx-auto mb-4 bg-dark-800 rounded-full flex items-center justify-center">
          <span class="text-4xl">🍳</span>
        </div>
        <p class="text-white text-lg mb-2">Нет активных заказов</p>
        <p class="text-dark-400">Все заказы приготовлены!</p>
      </div>

      <!-- Список заказов -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div
          v-for="order in orders"
          :key="order.id"
          class="premium-card p-6"
        >
          <!-- Заголовок заказа -->
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-3">
              <span class="text-2xl font-bold text-white">Заказ #{{ order.id }}</span>
              <span :class="[
                'px-3 py-1 rounded-full text-xs font-medium',
                getStatusClass(order.status)
              ]">
                {{ translateStatus(order.status) }}
              </span>
            </div>
            <span class="text-dark-400 text-sm">{{ formatTime(order.created_at) }}</span>
          </div>

          <!-- Состав заказа -->
          <div class="glass rounded-xl p-4 mb-4">
            <h4 class="text-sm font-semibold text-dark-300 mb-3">Состав заказа:</h4>
            <div class="space-y-3">
              <div
                v-for="item in order.items"
                :key="item.product_id"
                class="border-b border-dark-700 pb-3 last:border-0 last:pb-0"
              >
                <div class="flex items-center justify-between mb-1">
                  <span class="text-white font-medium">{{ item.product?.name || 'Товар' }}</span>
                  <span class="text-dark-500 text-sm">× {{ item.quantity }}</span>
                </div>
                <!-- Комментарий к позиции -->
                <div v-if="item.comment || item.special_requests" class="mt-2">
                  <span class="inline-flex items-center space-x-1 text-xs text-yellow-400">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z"/>
                    </svg>
                    <span>{{ item.comment || item.special_requests }}</span>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Комментарий к заказу -->
          <div v-if="order.order_comment" class="glass rounded-xl p-4 mb-4 border-l-4 border-yellow-500">
            <div class="flex items-start space-x-2">
              <span class="text-xl">📝</span>
              <div>
                <h4 class="text-xs font-semibold text-yellow-400 mb-1">Комментарий к заказу:</h4>
                <p class="text-dark-300 text-sm">{{ order.order_comment }}</p>
              </div>
            </div>
          </div>

          <!-- Информация -->
          <div class="flex items-center justify-between mb-4">
            <span class="text-dark-400 text-sm">Сумма: <span class="text-white font-bold">{{ Math.round(order.total_price) }} ₽</span></span>
          </div>

          <!-- Действия -->
          <div class="flex items-center space-x-3">
            <!-- Кнопка начать приготовление -->
            <button
              v-if="order.status === 'created' || order.status === 'paid'"
              @click="startCooking(order.id)"
              :disabled="isProcessing"
              class="btn-primary flex-1 py-3"
            >
              {{ isProcessing ? '...' : '🔥 Начать приготовление' }}
            </button>

            <!-- Кнопка готов -->
            <button
              v-if="order.status === 'cooking'"
              @click="markReady(order.id)"
              :disabled="isProcessing"
              class="btn-primary flex-1 py-3 bg-green-600 hover:bg-green-700"
            >
              {{ isProcessing ? '...' : '✅ Готов к выдаче' }}
            </button>

            <!-- Уже готов -->
            <div v-if="order.status === 'ready'" class="flex-1 text-center glass py-3 rounded-2xl">
              <span class="text-green-400 font-medium">✓ Готов</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const orders = ref([])
const isLoading = ref(true)
const isProcessing = ref(false)

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

const fetchOrders = async () => {
  isLoading.value = true
  try {
    const response = await fetch('/api/orders/cook/pending', {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    if (response.ok) {
      orders.value = await response.json()
    } else {
      router.push('/')
    }
  } catch (error) {
    console.error('Ошибка при загрузке заказов:', error)
  } finally {
    isLoading.value = false
  }
}

const updateOrderStatus = async (orderId, endpoint) => {
  isProcessing.value = true
  try {
    const response = await fetch(`/api/orders/${orderId}/status/${endpoint}`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    if (response.ok) {
      await fetchOrders()
    } else {
      const data = await response.json()
      alert(data.detail || 'Ошибка при обновлении статуса')
    }
  } catch (error) {
    console.error('Ошибка:', error)
    alert('Ошибка при обновлении статуса')
  } finally {
    isProcessing.value = false
  }
}

const startCooking = (orderId) => {
  updateOrderStatus(orderId, 'start-cooking')
}

const markReady = (orderId) => {
  updateOrderStatus(orderId, 'ready')
}

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  fetchOrders()
  // Автообновление каждые 30 секунд
  setInterval(fetchOrders, 30000)
})
</script>
