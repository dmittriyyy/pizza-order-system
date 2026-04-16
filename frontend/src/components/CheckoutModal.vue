<template>
  <div v-if="isOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
    <!-- Overlay -->
    <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="close"></div>

    <!-- Модалка -->
    <div class="relative premium-card max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-fade-in">
      <!-- Заголовок -->
      <div class="sticky top-0 bg-dark-900/95 backdrop-blur border-b border-dark-700 p-6 flex items-center justify-between z-10">
        <h2 class="text-2xl font-bold text-white">📦 Оформление заказа</h2>
        <button @click="close" class="w-10 h-10 glass-button rounded-full flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Форма -->
      <div class="p-6 space-y-6">
        <!-- Выбор адреса: ввод или карта -->
        <div class="space-y-3">
          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">
              Адрес доставки *
            </label>
            <input
              v-model="formData.delivery_address"
              type="text"
              placeholder="Улица, дом, квартира"
              class="input-primary"
              required
            />
            <p class="text-dark-500 text-xs mt-1">💡 Введите адрес вручную или выберите на карте ниже</p>
          </div>

          <!-- Яндекс Карта -->
          <CheckoutMap
            v-model="selectedLocation"
            @address-selected="onAddressSelected"
            @update:address="onAddressUpdate"
          />
        </div>

        <!-- Комментарий к заказу -->
        <div>
          <label class="block text-dark-300 text-sm font-medium mb-2">
            💬 Комментарий к заказу
          </label>
          <textarea
            v-model="formData.order_comment"
            placeholder="Например: дверь не открывать, звонить в дверь / без лука / добавить соус..."
            rows="3"
            class="input-primary"
          ></textarea>
        </div>

        <!-- Желаемое время доставки -->
        <div>
          <label class="block text-dark-300 text-sm font-medium mb-2">
            Желаемое время доставки
          </label>
          <input
            v-model="formData.delivery_time"
            type="text"
            placeholder="Например: к 19:00 или как можно быстрее"
            class="input-primary"
          />
        </div>

        <!-- Контактные данные -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">
              Имя получателя
            </label>
            <input
              v-model="formData.customer_name"
              type="text"
              placeholder="Как к вам обращаться"
              class="input-primary"
            />
          </div>
          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">
              Телефон
            </label>
            <input
              v-model="formData.customer_phone"
              type="tel"
              placeholder="+7 (___) ___-__-__"
              class="input-primary"
            />
          </div>
        </div>

        <!-- Способ оплаты -->
        <div>
          <label class="block text-dark-300 text-sm font-medium mb-2">
            Способ оплаты *
          </label>
          <div class="grid grid-cols-3 gap-3">
            <button
              v-for="method in paymentMethods"
              :key="method.value"
              @click="formData.payment_method = method.value"
              :class="[
                'p-4 rounded-2xl border-2 transition-all duration-300 text-center',
                formData.payment_method === method.value
                  ? 'border-primary-500 bg-primary-500/20 text-white'
                  : 'border-dark-700 glass text-dark-400 hover:border-dark-500'
              ]"
            >
              <div class="text-2xl mb-1">{{ method.icon }}</div>
              <div class="text-xs font-medium">{{ method.label }}</div>
            </button>
          </div>
        </div>

        <!-- Итого -->
        <div class="glass p-4 rounded-2xl flex items-center justify-between">
          <span class="text-dark-400">Итого к оплате:</span>
          <span class="text-2xl font-bold text-gradient">{{ total }} ₽</span>
        </div>
      </div>

      <!-- Кнопка -->
      <div class="sticky bottom-0 bg-dark-900/95 backdrop-blur border-t border-dark-700 p-6">
        <button
          @click="submitOrder"
          :disabled="isSubmitting || !formData.delivery_address"
          class="btn-primary w-full py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isSubmitting ? 'Оформление...' : `Заказать на ${total} ₽` }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { orderService } from '@/services'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import CheckoutMap from '@/components/CheckoutMap.vue'

const props = defineProps({
  isOpen: Boolean,
  total: Number,
})

const emit = defineEmits(['close', 'success'])

const authStore = useAuthStore()
const cartStore = useCartStore()
const router = useRouter()

const isSubmitting = ref(false)
const userProfile = ref(null)
const selectedLocation = ref(null)
const hasManualAddressSelection = ref(false)

const paymentMethods = [
  { value: 'cash_on_delivery', label: 'При получении', icon: '💵' },
  { value: 'credit_card', label: 'Картой онлайн', icon: '💳' },
  { value: 'sbp', label: 'СБП', icon: '📱' },
]

const formData = ref({
  delivery_address: '',
  delivery_time: '',
  customer_name: '',
  customer_phone: '',
  payment_method: 'cash_on_delivery',
  order_comment: '',
  delivery_lat: null,
  delivery_lng: null,
})

const close = () => {
  hasManualAddressSelection.value = false
  emit('close')
}

const onAddressSelected = (location) => {
  if (location) {
    hasManualAddressSelection.value = true
    selectedLocation.value = location
    formData.value.delivery_address = location.address
    formData.value.delivery_lat = location.lat
    formData.value.delivery_lng = location.lng
  }
}

const onAddressUpdate = (address) => {
  hasManualAddressSelection.value = true
  formData.value.delivery_address = address
}

const fetchUserProfile = async () => {
  try {
    const response = await api.get('/api/profile/me', {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    userProfile.value = response.data

    formData.value.customer_name = response.data.first_name || ''
    formData.value.customer_phone = response.data.phone || ''
    if (!hasManualAddressSelection.value) {
      formData.value.delivery_address = response.data.default_address || ''
    }
  } catch (error) {
    console.error('Ошибка при загрузке профиля:', error)
  }
}

const submitOrder = async () => {
  if (!authStore.isAuthenticated) {
    close()
    router.push('/login')
    return
  }

  isSubmitting.value = true
  try {
    await orderService.create(formData.value)
    await cartStore.clearCart()
    emit('success')
    close()
    router.push('/')
  } catch (error) {
    console.error('Ошибка при оформлении заказа:', error)
    alert(error.response?.data?.detail || 'Ошибка при оформлении заказа')
  } finally {
    isSubmitting.value = false
  }
}

watch(() => props.isOpen, (newVal) => {
  if (newVal && authStore.isAuthenticated) {
    hasManualAddressSelection.value = false
    fetchUserProfile()
  }
})

onMounted(() => {
  if (props.isOpen && authStore.isAuthenticated) {
    fetchUserProfile()
  }
})
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>
