<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-6xl mx-auto">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-4xl font-bold text-white mb-2">🚚 Доставка заказов</h1>
          <p class="text-dark-400">Заберите заказы и доставьте клиентам</p>
        </div>
        <div class="flex items-center space-x-3">
          <span class="glass px-4 py-2 rounded-xl text-sm">
            <span class="text-primary-400 font-bold">{{ activeOrders.length }}</span>
            <span class="text-dark-400 ml-2">в доставке</span>
          </span>
          <span class="glass px-4 py-2 rounded-xl text-sm">
            <span class="text-green-400 font-bold">{{ readyOrders.length }}</span>
            <span class="text-dark-400 ml-2">готовы</span>
          </span>
        </div>
      </div>

      <!-- Загрузка -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="inline-block w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
        <p class="text-dark-400 mt-4">Загрузка заказов...</p>
      </div>

      <!-- Нет заказов -->
      <div v-else-if="readyOrders.length === 0 && activeOrders.length === 0" class="text-center py-12">
        <div class="w-24 h-24 mx-auto mb-4 bg-dark-800 rounded-full flex items-center justify-center">
          <span class="text-4xl">🛵</span>
        </div>
        <p class="text-white text-lg mb-2">Нет доступных заказов</p>
        <p class="text-dark-400">Все заказы доставлены!</p>
      </div>

      <!-- Готовые заказы (можно забрать) -->
      <div v-if="readyOrders.length > 0" class="mb-12">
        <h2 class="text-2xl font-bold text-white mb-6">📦 Готовы к доставке</h2>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div
            v-for="order in readyOrders"
            :key="order.id"
            class="premium-card p-6"
          >
            <!-- Заголовок -->
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center space-x-3">
                <span class="text-2xl font-bold text-white">Заказ #{{ order.id }}</span>
                <span class="px-3 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400">
                  Готов
                </span>
              </div>
              <span class="text-dark-400 text-sm">{{ formatTime(order.created_at) }}</span>
            </div>

            <!-- Адрес -->
            <div class="glass rounded-xl p-4 mb-4">
              <div class="flex items-start space-x-3">
                <span class="text-xl">📍</span>
                <div>
                  <h4 class="text-sm font-semibold text-dark-300 mb-1">Адрес доставки:</h4>
                  <p class="text-white">{{ order.delivery_address }}</p>
                </div>
              </div>
            </div>

            <!-- Контактные данные -->
            <div class="glass rounded-xl p-4 mb-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <span class="text-xl">👤</span>
                  <div>
                    <p class="text-white font-medium">{{ order.customer_name || 'Клиент' }}</p>
                    <p v-if="order.customer_phone" class="text-dark-400 text-sm">{{ order.customer_phone }}</p>
                  </div>
                </div>
                <a
                  v-if="order.customer_phone"
                  :href="'tel:' + order.customer_phone"
                  class="btn-primary px-4 py-2 text-sm"
                >
                  📞 Позвонить
                </a>
              </div>
            </div>

            <!-- Состав заказа -->
            <div class="glass rounded-xl p-4 mb-4">
              <h4 class="text-sm font-semibold text-dark-300 mb-3">Заказ:</h4>
              <div class="space-y-2">
                <div
                  v-for="item in order.items"
                  :key="item.product_id"
                  class="flex items-center justify-between text-sm"
                >
                  <span class="text-white">{{ item.product?.name || 'Товар' }}</span>
                  <span class="text-dark-500">× {{ item.quantity }}</span>
                </div>
              </div>
            </div>

            <!-- Кнопка -->
            <button
              @click="takeOrder(order.id)"
              :disabled="isProcessing"
              class="btn-primary w-full py-3"
            >
              {{ isProcessing ? '...' : '🚀 Забрать заказ' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Активные заказы (в доставке) -->
      <div v-if="activeOrders.length > 0" class="mb-12">
        <h2 class="text-2xl font-bold text-white mb-6"> В доставке</h2>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div
            v-for="order in activeOrders"
            :key="order.id"
            class="premium-card p-6 border-purple-500/30"
          >
            <!-- Заголовок с таймером -->
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center space-x-3">
                <span class="text-2xl font-bold text-white">Заказ #{{ order.id }}</span>
                <span class="px-3 py-1 rounded-full text-xs font-medium bg-purple-500/20 text-purple-400">
                  В доставке
                </span>
              </div>
              <div class="text-right">
                <div :class="[
                  'text-lg font-bold',
                  getTimeLeft(order) < 600000 ? 'text-red-400 animate-pulse' : 'text-green-400'
                ]">
                  {{ formatTimeLeft(order) }}
                </div>
                <div class="text-dark-500 text-xs">до конца часа</div>
              </div>
            </div>

            <!-- Адрес с кнопкой маршрута -->
            <div class="glass rounded-xl p-4 mb-4">
              <div class="flex items-start justify-between">
                <div class="flex items-start space-x-3 flex-1">
                  <span class="text-xl">📍</span>
                  <div>
                    <h4 class="text-sm font-semibold text-dark-300 mb-1">Адрес:</h4>
                    <p class="text-white">{{ order.delivery_address }}</p>
                    <p v-if="order.delivery_comment" class="text-dark-400 text-sm mt-1">
                      💬 {{ order.delivery_comment }}
                    </p>
                  </div>
                </div>
                <a
                  :href="getRouteUrl(order)"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn-secondary px-4 py-2 text-sm whitespace-nowrap ml-3"
                >
                  🗺️ Маршрут
                </a>
              </div>
            </div>

            <!-- Контактные данные -->
            <div class="glass rounded-xl p-4 mb-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <span class="text-xl">👤</span>
                  <div>
                    <p class="text-white font-medium">{{ order.customer_name || 'Клиент' }}</p>
                    <p v-if="order.customer_phone" class="text-dark-400 text-sm">{{ order.customer_phone }}</p>
                  </div>
                </div>
                <a
                  v-if="order.customer_phone"
                  :href="'tel:' + order.customer_phone"
                  class="btn-primary px-4 py-2 text-sm"
                >
                  📞 Позвонить
                </a>
              </div>
            </div>

            <!-- Время заказа -->
            <div class="text-dark-400 text-sm mb-4">
              <span>⏰ Забран в:</span>
              <span class="text-white ml-2">{{ formatPickupTime(order.picked_up_at) }}</span>
            </div>

            <!-- Кнопка -->
            <button
              @click="completeDelivery(order.id)"
              :disabled="isProcessing"
              class="btn-primary w-full py-3 bg-green-600 hover:bg-green-700"
            >
              {{ isProcessing ? '...' : '✅ Доставлен' }}
            </button>
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

const orders = ref([])
const isLoading = ref(true)
const isProcessing = ref(false)

// Пиццерия (точка старта)
const PIZZERIA_COORDS = '54.5293,36.2754' // Калуга, Кирова 1

const readyOrders = computed(() =>
  orders.value.filter(o => o.status === 'ready')
)

const activeOrders = computed(() =>
  orders.value.filter(o => o.status === 'delivering')
)

const deliveredOrders = computed(() =>
  orders.value.filter(o => o.status === 'completed')
)

const parseServerDate = (dateString) => {
  if (!dateString) return null
  const normalized = /z|[+-]\d{2}:\d{2}$/i.test(dateString)
    ? dateString
    : `${dateString}Z`
  const date = new Date(normalized)
  return Number.isNaN(date.getTime()) ? null : date
}

const formatTime = (dateString) => {
  const date = parseServerDate(dateString)
  if (!date) return '--:--'
  return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

const formatPickupTime = (dateString) => {
  if (!dateString) return 'Не забран'
  const date = parseServerDate(dateString)
  if (!date) return 'Не забран'
  return date.toLocaleTimeString('ru-RU', { 
    hour: '2-digit', 
    minute: '2-digit',
    day: 'numeric',
    month: 'numeric'
  })
}

const getTimeLeft = (order) => {
  if (!order.picked_up_at) return 3600000 // 1 час по умолчанию
  const pickupDate = parseServerDate(order.picked_up_at)
  if (!pickupDate) return 3600000
  const pickupTime = pickupDate.getTime()
  const now = Date.now()
  const elapsed = now - pickupTime
  return Math.max(0, 3600000 - elapsed) // 1 час в миллисекундах
}

const formatTimeLeft = (order) => {
  const ms = getTimeLeft(order)
  const minutes = Math.floor(ms / 60000)
  const seconds = Math.floor((ms % 60000) / 1000)
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
}

const getRouteUrl = (order) => {
  // Яндекс Карты - построение маршрута
  const to = order.delivery_lat && order.delivery_lng 
    ? `${order.delivery_lat},${order.delivery_lng}`
    : encodeURIComponent(order.delivery_address)
  
  return `https://yandex.ru/maps/?rtext=~${to}&rtt=auto`
}

const fetchOrders = async () => {
  isLoading.value = true
  try {
    // Готовые заказы
    const readyResponse = await api.get('/api/orders/courier/ready', {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    
    // Заказы в доставке — берем ВСЕ заказы через админский эндпоинт
    // (обычный /api/orders возвращает только заказы текущего пользователя)
    const allResponse = await api.get('/api/orders/admin/all', {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    const deliveringOrders = allResponse.data.filter(o => o.status === 'delivering')
    
    console.log('Заказы в доставке:', deliveringOrders)
    
    orders.value = [...readyResponse.data, ...deliveringOrders]
  } catch (error) {
    console.error('Ошибка при загрузке заказов:', error)
  } finally {
    isLoading.value = false
  }
}

const updateOrderStatus = async (orderId, endpoint) => {
  isProcessing.value = true
  try {
    const response = await api.patch(`/api/orders/${orderId}/status/${endpoint}`, {}, {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    await fetchOrders()
  } catch (error) {
    console.error('Ошибка:', error)
    alert(error.response?.data?.detail || 'Ошибка при обновлении статуса')
  } finally {
    isProcessing.value = false
  }
}

const takeOrder = (orderId) => {
  updateOrderStatus(orderId, 'delivering')
}

const completeDelivery = (orderId) => {
  if (confirm('Подтвердите, что заказ доставлен клиенту')) {
    updateOrderStatus(orderId, 'completed')
  }
}

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  fetchOrders()
  // Автообновление каждые 10 секунд
  setInterval(fetchOrders, 10000)
})
</script>
