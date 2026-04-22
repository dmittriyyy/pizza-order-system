<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-6xl mx-auto">
      <h1 class="text-4xl font-bold text-white mb-8">Профиль</h1>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Левая колонка: Информация и форма -->
        <div class="lg:col-span-1 space-y-6">
          <!-- Карточка пользователя -->
          <div class="premium-card p-6">
            <div class="text-center mb-6">
              <div class="w-24 h-24 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
              </div>
              <h2 class="text-xl font-bold text-white">{{ userProfile.login || 'Пользователь' }}</h2>
              <p class="text-dark-400 text-sm mt-1">{{ userProfile.email || '' }}</p>
              <span class="inline-block mt-3 glass px-3 py-1 rounded-full text-xs text-dark-300">
                {{ translateRole(userProfile.role) }}
              </span>
            </div>

            <button
              @click="handleLogout"
              class="w-full btn-secondary py-3 text-sm"
            >
              Выйти
            </button>
          </div>

          <!-- Форма редактирования -->
          <div class="premium-card p-6">
            <h3 class="text-lg font-bold text-white mb-4">📝 Контакты</h3>
            <form @submit.prevent="saveProfile" class="space-y-4">
              <div>
                <label class="block text-dark-300 text-xs mb-1">Телефон</label>
                <input
                  v-model="formData.phone"
                  type="tel"
                  placeholder="+7 (___) ___-__-__"
                  class="input-primary text-sm py-2"
                />
              </div>
              <div>
                <label class="block text-dark-300 text-xs mb-1">Telegram</label>
                <input
                  v-model="formData.telegram"
                  type="text"
                  placeholder="@username"
                  class="input-primary text-sm py-2"
                />
              </div>
              <div>
                <label class="block text-dark-300 text-xs mb-1">Адрес по умолчанию</label>
                <textarea
                  v-model="formData.default_address"
                  placeholder="Улица, дом, квартира"
                  rows="3"
                  class="input-primary text-sm py-2"
                ></textarea>
              </div>
              <button
                type="submit"
                :disabled="isSaving"
                class="btn-primary w-full py-2 text-sm disabled:opacity-50"
              >
                {{ isSaving ? 'Сохранение...' : '💾 Сохранить' }}
              </button>
            </form>
          </div>
        </div>

        <!-- Правая колонка: История заказов -->
        <div class="lg:col-span-2">
          <div class="premium-card p-6">
            <h3 class="text-xl font-bold text-white mb-6">📦 История заказов</h3>

            <div v-if="isLoading" class="text-center py-12">
              <div class="inline-block w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
              <p class="text-dark-400 mt-4">Загрузка...</p>
            </div>

            <div v-else-if="orders.length === 0" class="text-center py-12">
              <div class="w-20 h-20 mx-auto mb-4 bg-dark-800 rounded-full flex items-center justify-center">
                <span class="text-4xl">🛒</span>
              </div>
              <p class="text-dark-400 mb-4">У вас пока нет заказов</p>
              <router-link to="/" class="btn-primary inline-block px-6 py-3">
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
                  <div class="flex items-center space-x-3">
                    <span class="text-white font-bold">Заказ #{{ order.id }}</span>
                    <span :class="[
                      'px-3 py-1 rounded-full text-xs font-medium',
                      getStatusClass(order.status)
                    ]">
                      {{ translateStatus(order.status) }}
                    </span>
                  </div>
                  <span class="text-primary-400 font-bold">{{ Math.round(order.total_price) }} ₽</span>
                </div>
                
                <div class="flex items-center justify-between text-sm mb-3">
                  <span class="text-dark-400">{{ formatDate(order.created_at) }}</span>
                  <div class="flex items-center space-x-2 text-dark-400">
                    <span>📍</span>
                    <span class="max-w-xs truncate">{{ order.delivery_address }}</span>
                  </div>
                </div>

                <!-- Состав заказа -->
                <div class="border-t border-dark-700 pt-3 mt-3">
                  <p class="text-dark-400 text-xs mb-2">Состав заказа:</p>
                  <div class="space-y-2">
                    <div
                      v-for="item in order.items"
                      :key="item.product_id"
                      class="flex items-center justify-between text-sm"
                    >
                      <div class="flex items-center space-x-2">
                        <span class="text-white">{{ item.product?.name || 'Товар' }}</span>
                        <span class="text-dark-500">× {{ item.quantity }}</span>
                      </div>
                      <span class="text-primary-400">{{ Math.round(item.subtotal) }} ₽</span>
                    </div>
                  </div>
                </div>

                <div
                  v-if="canLeaveFeedback(order)"
                  class="border-t border-dark-700 pt-3 mt-3 flex items-center justify-between"
                >
                  <p class="text-dark-400 text-xs">
                    Заказ завершён. Можно оставить отзыв для AI-агента постобслуживания.
                  </p>
                  <button
                    @click="openFeedbackModal(order)"
                    class="btn-secondary px-4 py-2 text-xs"
                  >
                    Оставить отзыв
                  </button>
                </div>

                <div
                  v-else-if="hasFeedback(order.id)"
                  class="border-t border-dark-700 pt-3 mt-3"
                >
                  <p class="text-green-400 text-xs">Отзыв по этому заказу уже оставлен.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="feedbackModalOpen"
        class="fixed inset-0 z-[70] flex items-center justify-center p-4"
      >
        <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="closeFeedbackModal"></div>
        <div class="relative premium-card w-full max-w-lg p-6 z-10">
          <h3 class="text-2xl font-bold text-white mb-4">Отзыв о заказе #{{ selectedOrder?.id }}</h3>
          <div class="mb-4">
            <label class="block text-dark-300 text-sm mb-2">Оценка</label>
            <div class="flex gap-2">
              <button
                v-for="value in 5"
                :key="value"
                @click="feedbackForm.rating = value"
                :class="[
                  'w-11 h-11 rounded-full text-lg font-bold transition-colors',
                  feedbackForm.rating >= value ? 'bg-primary-500 text-white' : 'glass text-dark-300'
                ]"
              >
                {{ value }}
              </button>
            </div>
          </div>
          <div class="mb-6">
            <label class="block text-dark-300 text-sm mb-2">Комментарий</label>
            <textarea
              v-model="feedbackForm.comment"
              rows="4"
              class="input-primary"
              placeholder="Что понравилось или что пошло не так?"
            ></textarea>
          </div>
          <div class="flex items-center justify-end gap-3">
            <button @click="closeFeedbackModal" class="btn-secondary px-5 py-3 text-sm">Отмена</button>
            <button
              @click="submitFeedback"
              :disabled="isSubmittingFeedback || !feedbackForm.rating"
              class="btn-primary px-5 py-3 text-sm disabled:opacity-50"
            >
              {{ isSubmittingFeedback ? 'Отправка...' : 'Отправить отзыв' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import { feedbackService } from '@/services'

const router = useRouter()
const authStore = useAuthStore()

const userProfile = ref({
  login: '',
  email: '',
  role: 'client',
  phone: '',
  telegram: '',
  default_address: '',
  address_comment: '',
})

const formData = reactive({
  phone: '',
  telegram: '',
  default_address: '',
})

const orders = ref([])
const feedback = ref([])
const isLoading = ref(true)
const isSaving = ref(false)
const feedbackModalOpen = ref(false)
const selectedOrder = ref(null)
const isSubmittingFeedback = ref(false)
const feedbackForm = reactive({
  rating: 5,
  comment: '',
})

const translateRole = (role) => {
  const roles = {
    admin: '👨‍💼 Администратор',
    cook: '👨‍🍳 Повар',
    courier: '🚚 Курьер',
    client: '👤 Клиент',
  }
  return roles[role] || role
}

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
    created: 'Создан',
    paid: 'Оплачен',
    cooking: 'Готовится',
    ready: 'Готов',
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

const fetchProfile = async () => {
  try {
    const response = await api.get('/api/profile/me', {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    userProfile.value = response.data
    
    // Заполняем форму текущими данными
    formData.phone = response.data.phone || ''
    formData.telegram = response.data.telegram || ''
    formData.default_address = response.data.default_address || ''
  } catch (error) {
    console.error('Ошибка при загрузке профиля:', error)
  }
}

const saveProfile = async () => {
  isSaving.value = true
  try {
    const response = await api.patch('/api/profile/me', formData, {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    userProfile.value = { ...userProfile.value, ...response.data }
    alert('✅ Профиль обновлён!')
  } catch (error) {
    console.error('Ошибка при сохранении:', error)
    alert('❌ Ошибка при сохранении профиля')
  } finally {
    isSaving.value = false
  }
}

const fetchOrders = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/api/orders', {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    orders.value = response.data
  } catch (error) {
    console.error('Ошибка при загрузке заказов:', error)
  } finally {
    isLoading.value = false
  }
}

const fetchFeedback = async () => {
  try {
    feedback.value = await feedbackService.getMine()
  } catch (error) {
    console.error('Ошибка при загрузке отзывов:', error)
  }
}

const hasFeedback = (orderId) => feedback.value.some((item) => item.order_id === orderId)

const canLeaveFeedback = (order) => order.status === 'completed' && !hasFeedback(order.id)

const openFeedbackModal = (order) => {
  selectedOrder.value = order
  feedbackForm.rating = 5
  feedbackForm.comment = ''
  feedbackModalOpen.value = true
}

const closeFeedbackModal = () => {
  feedbackModalOpen.value = false
  selectedOrder.value = null
}

const submitFeedback = async () => {
  if (!selectedOrder.value) return

  isSubmittingFeedback.value = true
  try {
    const created = await feedbackService.create({
      order_id: selectedOrder.value.id,
      rating: feedbackForm.rating,
      comment: feedbackForm.comment,
    })
    feedback.value = [created, ...feedback.value]
    closeFeedbackModal()
    alert('✅ Отзыв отправлен')
  } catch (error) {
    console.error('Ошибка при отправке отзыва:', error)
    alert(error.response?.data?.detail || '❌ Ошибка при отправке отзыва')
  } finally {
    isSubmittingFeedback.value = false
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  fetchProfile()
  fetchOrders()
  fetchFeedback()
})
</script>
