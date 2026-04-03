<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Overlay -->
    <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="close"></div>

    <!-- Модалка -->
    <div class="relative premium-card max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-fade-in">
      <!-- Заголовок -->
      <div class="sticky top-0 bg-dark-900/95 backdrop-blur border-b border-dark-700 p-6 flex items-center justify-between z-10">
        <h2 class="text-2xl font-bold text-white">
          {{ isEdit ? '✏️ Редактирование сотрудника' : '➕ Новый сотрудник' }}
        </h2>
        <button @click="close" class="w-10 h-10 glass-button rounded-full flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Форма -->
      <form @submit.prevent="saveEmployee" class="p-6 space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">Имя *</label>
            <input v-model="formData.first_name" type="text" required class="input-primary" />
          </div>
          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">Фамилия *</label>
            <input v-model="formData.last_name" type="text" required class="input-primary" />
          </div>
        </div>

        <div>
          <label class="block text-dark-300 text-sm font-medium mb-2">Логин *</label>
          <input v-model="formData.login" type="text" required class="input-primary" />
        </div>

        <div>
          <label class="block text-dark-300 text-sm font-medium mb-2">Email</label>
          <input v-model="formData.email" type="email" class="input-primary" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">Телефон</label>
            <input v-model="formData.phone" type="tel" class="input-primary" />
          </div>
          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">Telegram</label>
            <input v-model="formData.telegram" type="text" class="input-primary" />
          </div>
        </div>

        <div v-if="!isEdit">
          <label class="block text-dark-300 text-sm font-medium mb-2">Роль *</label>
          <select v-model="formData.role" required class="input-primary">
            <option value="client">👤 Клиент</option>
            <option value="cook">👨‍ Повар</option>
            <option value="courier">🚚 Курьер</option>
            <option value="admin">👨‍💼 Админ</option>
          </select>
        </div>

        <div v-if="!isEdit" class="glass p-4 rounded-xl">
          <p class="text-dark-400 text-sm">
            ℹ️ Пароль будет установлен автоматически. Сотрудник сможет изменить его после первого входа.
          </p>
        </div>

        <!-- Кнопки -->
        <div class="flex items-center justify-end space-x-4 pt-6 border-t border-dark-700">
          <button type="button" @click="close" class="btn-secondary px-6 py-3">Отмена</button>
          <button type="submit" :disabled="isSaving" class="btn-primary px-6 py-3 disabled:opacity-50">
            {{ isSaving ? '💾 Сохранение...' : '💾 Сохранить' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import api from '@/services/api'

const props = defineProps({
  employee: Object,
  isOpen: Boolean,
})

const emit = defineEmits(['close', 'saved'])

const isEdit = computed(() => !!props.employee)
const isSaving = ref(false)

const defaultForm = {
  first_name: '',
  last_name: '',
  login: '',
  email: '',
  phone: '',
  telegram: '',
  role: 'client',
}

const formData = reactive({ ...defaultForm })

watch(() => props.employee, (newEmployee) => {
  if (newEmployee) {
    Object.assign(formData, newEmployee)
  } else {
    Object.assign(formData, defaultForm)
  }
}, { immediate: true })

const close = () => {
  Object.assign(formData, defaultForm)
  emit('close')
}

const saveEmployee = async () => {
  isSaving.value = true
  try {
    const token = localStorage.getItem('access_token')
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    }

    if (isEdit.value) {
      await api.patch(`/api/admin/employees/${props.employee.id}`, formData, { headers })
    } else {
      await api.post('/api/admin/employees', formData, { headers })
    }

    emit('saved')
  } catch (error) {
    console.error('Ошибка при сохранении:', error)
    alert('❌ Ошибка: ' + (error.response?.data?.detail || error.message))
  } finally {
    isSaving.value = false
  }
}
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
