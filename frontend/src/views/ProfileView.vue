<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-4xl font-bold text-white mb-8">Профиль</h1>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Информация о пользователе -->
        <div class="md:col-span-1">
          <div class="premium-card p-6">
            <div class="text-center">
              <div class="w-24 h-24 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
              </div>
              <h2 class="text-xl font-bold text-white">{{ authStore.user?.login || 'Пользователь' }}</h2>
              <p class="text-dark-400 text-sm mt-1">{{ authStore.user?.email || '' }}</p>
              <span class="inline-block mt-3 glass px-3 py-1 rounded-full text-xs text-dark-300">
                {{ authStore.user?.role || 'client' }}
              </span>
            </div>

            <button
              @click="handleLogout"
              class="w-full mt-6 btn-secondary py-3 text-sm"
            >
              Выйти
            </button>
          </div>
        </div>

        <!-- История заказов -->
        <div class="md:col-span-2">
          <div class="premium-card p-6">
            <h3 class="text-xl font-bold text-white mb-6">История заказов</h3>

            <div v-if="isLoading" class="text-center py-8">
              <div class="inline-block w-8 h-8 border-3 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
              <p class="text-dark-400 mt-3">Загрузка...</p>
            </div>

            <div v-else-if="orders.length === 0" class="text-center py-8">
              <div class="w-16 h-16 bg-dark-800 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-dark-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
                </svg>
              </div>
              <p class="text-dark-400">У вас пока нет заказов</p>
              <router-link to="/" class="text-primary-400 hover:text-primary-300 font-medium mt-2 inline-block">
                Перейти в меню
              </router-link>
            </div>

            <div v-else class="space-y-4">
              <div
                v-for="order in orders"
                :key="order.id"
                class="glass p-4 rounded-2xl"
              >
                <div class="flex items-center justify-between mb-3">
                  <span class="text-white font-semibold">Заказ #{{ order.id }}</span>
                  <span :class="[
                    'px-3 py-1 rounded-full text-xs font-medium',
                    getStatusClass(order.status)
                  ]">
                    {{ translateStatus(order.status) }}
                  </span>
                </div>
                <div class="flex items-center justify-between text-sm mb-3">
                  <span class="text-dark-400">{{ formatDate(order.created_at) }}</span>
                  <span class="text-primary-400 font-bold">{{ Math.round(order.total_price) }} ₽</span>
                </div>
                
                <!-- Состав заказа -->
                <div class="border-t border-dark-700 pt-3 mt-3">
                  <p class="text-dark-400 text-sm mb-2">Состав заказа:</p>
                  <div class="space-y-2">
                    <div
                      v-for="item in order.items"
                      :key="item.product_id"
                      class="flex items-center space-x-3 bg-dark-800/50 rounded-xl p-2"
                    >
                      <img
                        v-if="item.product?.image_url"
                        :src="item.product.image_url"
                        :alt="item.product?.name"
                        class="w-12 h-12 rounded-lg object-cover"
                      />
                      <div class="flex-1">
                        <p class="text-white text-sm font-medium">{{ item.product?.name || 'Товар' }}</p>
                        <p class="text-dark-500 text-xs">{{ item.quantity }} шт. × {{ Math.round(item.price_at_time_of_order) }} ₽</p>
                      </div>
                      <p class="text-primary-400 font-semibold">{{ Math.round(item.subtotal || item.price_at_time_of_order * item.quantity) }} ₽</p>
                    </div>
                  </div>
                </div>
              </div>
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
import { orderService } from '@/services'

const router = useRouter()
const authStore = useAuthStore()

const orders = ref([])
const isLoading = ref(true)

const getStatusClass = (status) => {
  const classes = {
    created: 'bg-blue-500/20 text-blue-400',
    paid: 'bg-green-500/20 text-green-400',
    cooking: 'bg-yellow-500/20 text-yellow-400',
    delivering: 'bg-purple-500/20 text-purple-400',
    completed: 'bg-green-500/20 text-green-400',
    cancelled: 'bg-red-500/20 text-red-400',
  }
  return classes[status] || 'bg-gray-500/20 text-gray-400'
}

const translateStatus = (status) => {
  const translations = {
    created: 'Создан',
    paid: 'Оплачен',
    cooking: 'Готовится',
    delivering: 'Доставляется',
    completed: 'Завершён',
    cancelled: 'Отменён',
  }
  return translations[status] || status
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}

const fetchOrders = async () => {
  isLoading.value = true
  try {
    orders.value = await orderService.getAll()
  } catch (error) {
    console.error('Ошибка при загрузке заказов:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  fetchOrders()
})
</script>
