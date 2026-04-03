<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-7xl mx-auto">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-4xl font-bold text-white mb-2">👥 Сотрудники</h1>
          <p class="text-dark-400">Управление командой Piazza Pizza</p>
        </div>
        <button @click="openAddModal" class="btn-primary px-6 py-3">
          ➕ Добавить сотрудника
        </button>
      </div>

      <!-- Статистика -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div class="premium-card p-6 text-center">
          <div class="text-3xl font-bold text-purple-400">{{ adminsCount }}</div>
          <div class="text-dark-400 text-sm mt-1">Админы</div>
        </div>
        <div class="premium-card p-6 text-center">
          <div class="text-3xl font-bold text-yellow-400">{{ cooksCount }}</div>
          <div class="text-dark-400 text-sm mt-1">Повара</div>
        </div>
        <div class="premium-card p-6 text-center">
          <div class="text-3xl font-bold text-blue-400">{{ couriersCount }}</div>
          <div class="text-dark-400 text-sm mt-1">Курьеры</div>
        </div>
        <div class="premium-card p-6 text-center">
          <div class="text-3xl font-bold text-primary-400">{{ employees.length }}</div>
          <div class="text-dark-400 text-sm mt-1">Всего</div>
        </div>
      </div>

      <!-- Таблица сотрудников -->
      <div class="premium-card p-6">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-dark-700">
                <th class="text-left py-3 px-4 text-dark-300 font-medium">Сотрудник</th>
                <th class="text-left py-3 px-4 text-dark-300 font-medium">Роль</th>
                <th class="text-left py-3 px-4 text-dark-300 font-medium">Контакты</th>
                <th class="text-left py-3 px-4 text-dark-300 font-medium">Статус</th>
                <th class="text-right py-3 px-4 text-dark-300 font-medium">Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="emp in employees"
                :key="emp.id"
                class="border-b border-dark-800 hover:bg-dark-800/50"
              >
                <td class="py-3 px-4">
                  <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center">
                      <span class="text-white font-bold">{{ getInitials(emp) }}</span>
                    </div>
                    <div>
                      <p class="text-white font-medium">{{ emp.first_name || '' }} {{ emp.last_name || '' }}</p>
                      <p class="text-dark-500 text-xs">{{ emp.login }}</p>
                    </div>
                  </div>
                </td>
                <td class="py-3 px-4">
                  <select
                    :value="emp.role"
                    @change="updateRole(emp.id, $event.target.value)"
                    class="glass px-3 py-1.5 rounded-xl text-sm text-white focus:outline-none"
                  >
                    <option value="admin">👨‍💼 Админ</option>
                    <option value="cook">👨‍ Повар</option>
                    <option value="courier">🚚 Курьер</option>
                    <option value="client">👤 Клиент</option>
                  </select>
                </td>
                <td class="py-3 px-4 text-sm">
                  <div class="space-y-1">
                    <p v-if="emp.phone" class="text-dark-400">📞 {{ emp.phone }}</p>
                    <p v-if="emp.telegram" class="text-dark-400">✈️ {{ emp.telegram }}</p>
                    <p v-if="emp.email" class="text-dark-400">✉️ {{ emp.email }}</p>
                  </div>
                </td>
                <td class="py-3 px-4">
                  <span :class="[
                    'px-3 py-1 rounded-full text-xs font-medium',
                    emp.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                  ]">
                    {{ emp.status === 'active' ? 'Активен' : 'Не активен' }}
                  </span>
                </td>
                <td class="py-3 px-4 text-right">
                  <div class="flex items-center justify-end space-x-2">
                    <button
                      @click="openEditModal(emp)"
                      class="btn-secondary px-4 py-2 text-sm"
                    >
                      ✏️
                    </button>
                    <button
                      v-if="emp.id !== currentUserId"
                      @click="confirmDelete(emp)"
                      class="bg-red-500/20 hover:bg-red-500/30 text-red-400 px-4 py-2 rounded-xl text-sm transition-colors"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Модальное окно добавления/редактирования -->
    <EmployeeEditModal
      v-if="isModalOpen"
      :employee="selectedEmployee"
      @close="closeModal"
      @saved="onEmployeeSaved"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import EmployeeEditModal from '@/components/EmployeeEditModal.vue'

const router = useRouter()
const authStore = useAuthStore()

const employees = ref([])
const isModalOpen = ref(false)
const selectedEmployee = ref(null)

const adminsCount = computed(() => employees.value.filter(e => e.role === 'admin').length)
const cooksCount = computed(() => employees.value.filter(e => e.role === 'cook').length)
const couriersCount = computed(() => employees.value.filter(e => e.role === 'courier').length)
const currentUserId = computed(() => authStore.user?.id)

const getInitials = (emp) => {
  const first = emp.first_name?.charAt(0) || ''
  const last = emp.last_name?.charAt(0) || ''
  return (first + last) || emp.login.charAt(0).toUpperCase()
}

const fetchEmployees = async () => {
  try {
    const response = await api.get('/api/admin/employees', {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    employees.value = response.data
  } catch (error) {
    console.error('Ошибка при загрузке сотрудников:', error)
  }
}

const updateRole = async (userId, newRole) => {
  if (!confirm(`Изменить роль сотрудника?`)) {
    fetchEmployees()
    return
  }
  
  try {
    await api.patch(`/api/admin/employees/${userId}`, {
      role: newRole
    }, {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    alert('✅ Роль обновлена')
    fetchEmployees()
  } catch (error) {
    console.error('Ошибка при обновлении роли:', error)
    alert('❌ Ошибка при обновлении роли')
    fetchEmployees()
  }
}

const openAddModal = () => {
  selectedEmployee.value = null
  isModalOpen.value = true
}

const openEditModal = (employee) => {
  selectedEmployee.value = { ...employee }
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
  selectedEmployee.value = null
}

const onEmployeeSaved = () => {
  fetchEmployees()
  closeModal()
}

const confirmDelete = async (employee) => {
  if (!confirm(`Удалить сотрудника "${employee.first_name || employee.login}"?`)) return
  
  try {
    await api.delete(`/api/admin/employees/${employee.id}`, {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    alert('✅ Сотрудник удалён')
    fetchEmployees()
  } catch (error) {
    console.error('Ошибка при удалении:', error)
    alert('❌ ' + (error.response?.data?.detail || 'Ошибка при удалении'))
  }
}

onMounted(() => {
  if (!authStore.isAuthenticated || !authStore.isAdmin) {
    router.push('/')
    return
  }
  fetchEmployees()
})
</script>
