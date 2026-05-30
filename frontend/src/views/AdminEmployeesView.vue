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

      <div class="premium-card p-6 mb-8 border border-primary-500/15 shadow-[0_24px_60px_rgba(0,0,0,0.24)]">
        <div class="flex flex-col lg:flex-row lg:items-end gap-4">
          <div class="flex-1">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-500/10 text-primary-300 text-xs font-bold uppercase tracking-[0.18em] mb-3">
              Быстрое назначение
            </div>
            <h2 class="text-2xl font-bold text-white mb-2">Назначить существующего пользователя</h2>
            <p class="text-dark-400 text-sm mb-4">
              Введите логин, email, `@telegram` или `telegram_id`, чтобы выдать роль без создания нового аккаунта.
            </p>
            <label class="block text-dark-300 text-sm font-medium mb-2">Профиль пользователя</label>
            <input
              v-model.trim="assignForm.query"
              type="text"
              placeholder="Например: user или @username"
              class="input-primary"
            />
          </div>

          <div class="w-full lg:w-64">
            <label class="block text-dark-300 text-sm font-medium mb-2">Роль</label>
            <select v-model="assignForm.role" class="input-primary role-select">
              <option value="admin">👨‍💼 Админ</option>
              <option value="cook">👨‍🍳 Повар</option>
              <option value="courier">🚚 Курьер</option>
              <option value="client">👤 Клиент</option>
            </select>
          </div>

          <button
            @click="assignExistingEmployee"
            :disabled="isAssigning || !assignForm.query"
            class="btn-primary px-6 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isAssigning ? 'Назначение...' : 'Выдать роль' }}
          </button>
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
                  <div class="mb-2">
                    <span :class="roleBadgeClass(emp.role)" class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold">
                      <span>{{ roleEmoji(emp.role) }}</span>
                      <span>{{ roleLabel(emp.role) }}</span>
                    </span>
                  </div>
                  <select
                    :value="emp.role"
                    @change="updateRole(emp.id, $event.target.value)"
                    class="glass px-3 py-1.5 rounded-xl text-sm text-white focus:outline-none role-select w-full"
                  >
                    <option value="admin">👨‍💼 Админ</option>
                    <option value="cook">👨‍🍳 Повар</option>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import EmployeeEditModal from '@/components/EmployeeEditModal.vue'

const router = useRouter()
const authStore = useAuthStore()

const employees = ref([])
const isModalOpen = ref(false)
const selectedEmployee = ref(null)
const isAssigning = ref(false)
const assignForm = reactive({
  query: '',
  role: 'admin',
})

const adminsCount = computed(() => employees.value.filter(e => e.role === 'admin').length)
const cooksCount = computed(() => employees.value.filter(e => e.role === 'cook').length)
const couriersCount = computed(() => employees.value.filter(e => e.role === 'courier').length)
const currentUserId = computed(() => authStore.user?.id)

const getInitials = (emp) => {
  const first = emp.first_name?.charAt(0) || ''
  const last = emp.last_name?.charAt(0) || ''
  return (first + last) || emp.login.charAt(0).toUpperCase()
}

const roleLabel = (role) => {
  const labels = {
    admin: 'Админ',
    cook: 'Повар',
    courier: 'Курьер',
    client: 'Клиент',
  }
  return labels[role] || role
}

const roleEmoji = (role) => {
  const emojis = {
    admin: '👨‍💼',
    cook: '👨‍🍳',
    courier: '🚚',
    client: '👤',
  }
  return emojis[role] || '👤'
}

const roleBadgeClass = (role) => {
  const classes = {
    admin: 'bg-purple-500/15 text-purple-300 border border-purple-500/20',
    cook: 'bg-yellow-500/15 text-yellow-300 border border-yellow-500/20',
    courier: 'bg-blue-500/15 text-blue-300 border border-blue-500/20',
    client: 'bg-white/5 text-dark-200 border border-white/10',
  }
  return classes[role] || classes.client
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

const assignExistingEmployee = async () => {
  if (!assignForm.query) return

  isAssigning.value = true
  try {
    await api.post('/api/admin/employees/assign-existing', {
      query: assignForm.query,
      role: assignForm.role,
    }, {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })

    alert('✅ Роль выдана')
    assignForm.query = ''
    assignForm.role = 'admin'
    fetchEmployees()
  } catch (error) {
    console.error('Ошибка при назначении роли:', error)
    alert('❌ ' + (error.response?.data?.detail || 'Не удалось выдать роль'))
  } finally {
    isAssigning.value = false
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

<style scoped>
.role-select {
  appearance: none;
  background-image:
    linear-gradient(45deg, transparent 50%, rgba(255,255,255,0.6) 50%),
    linear-gradient(135deg, rgba(255,255,255,0.6) 50%, transparent 50%);
  background-position:
    calc(100% - 18px) calc(50% - 3px),
    calc(100% - 12px) calc(50% - 3px);
  background-size: 6px 6px, 6px 6px;
  background-repeat: no-repeat;
  padding-right: 2.5rem;
}
</style>
