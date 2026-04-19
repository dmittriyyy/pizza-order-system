<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-7xl mx-auto">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-4xl font-bold text-white mb-2">✏️ Изменить меню</h1>
          <p class="text-dark-400">Добавление, редактирование и удаление товаров</p>
        </div>
        <button @click="openAddModal" class="btn-primary px-6 py-3">
          ➕ Добавить товар
        </button>
      </div>

      <!-- Статистика -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div class="premium-card p-6 text-center">
          <div class="text-3xl font-bold text-primary-400">{{ products.length }}</div>
          <div class="text-dark-400 text-sm mt-1">Всего товаров</div>
        </div>
        <div class="premium-card p-6 text-center">
          <div class="text-3xl font-bold text-blue-400">{{ categories.length }}</div>
          <div class="text-dark-400 text-sm mt-1">Категорий</div>
        </div>
      </div>

      <!-- Таблица товаров -->
      <div class="premium-card p-6">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-dark-700">
                <th class="text-left py-3 px-4 text-dark-300 font-medium">Фото</th>
                <th class="text-left py-3 px-4 text-dark-300 font-medium">Название</th>
                <th class="text-left py-3 px-4 text-dark-300 font-medium">Категория</th>
                <th class="text-left py-3 px-4 text-dark-300 font-medium">Цена</th>
                <th class="text-left py-3 px-4 text-dark-300 font-medium">КБЖУ</th>
                <th class="text-right py-3 px-4 text-dark-300 font-medium">Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="product in products"
                :key="product.id"
                class="border-b border-dark-800 hover:bg-dark-800/50"
              >
                <td class="py-3 px-4">
                  <img
                    :src="product.image_url || 'https://via.placeholder.com/100x100?text=No+Image'"
                    :alt="product.name"
                    class="w-16 h-16 rounded-xl object-cover"
                  />
                </td>
                <td class="py-3 px-4">
                  <div>
                    <p class="text-white font-medium">{{ product.name }}</p>
                    <p class="text-dark-500 text-xs truncate max-w-xs">{{ product.description }}</p>
                  </div>
                </td>
                <td class="py-3 px-4">
                  <span class="glass px-3 py-1 rounded-full text-xs">
                    {{ getCategoryName(product.category_id) }}
                  </span>
                </td>
                <td class="py-3 px-4">
                  <span class="text-primary-400 font-bold">{{ Math.round(product.price) }} ₽</span>
                  <span v-if="product.discount > 0" class="text-dark-500 text-xs line-through ml-2">
                    {{ Math.round(product.price / (1 - product.discount / 100)) }} ₽
                  </span>
                </td>
                <td class="py-3 px-4 text-xs text-dark-400">
                  <div>{{ getTotalCalories(product) }} ккал за порцию</div>
                  <div>Б:{{ product.protein }} Ж:{{ product.fat }} У:{{ product.carbohydrates }} / 100г</div>
                </td>
                <td class="py-3 px-4 text-right">
                  <div class="flex items-center justify-end space-x-2">
                    <button
                      @click="openEditModal(product)"
                      class="btn-secondary px-4 py-2 text-sm"
                    >
                      ✏️
                    </button>
                    <button
                      @click="confirmDelete(product)"
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
    <ProductEditModal
      v-if="isModalOpen"
      :product="selectedProduct"
      :categories="categories"
      @close="closeModal"
      @saved="onProductSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import ProductEditModal from '@/components/ProductEditModal.vue'

const router = useRouter()
const authStore = useAuthStore()

const products = ref([])
const categories = ref([])
const isModalOpen = ref(false)
const selectedProduct = ref(null)

const getCategoryName = (categoryId) => {
  const category = categories.value.find(c => c.id === categoryId)
  return category?.name || 'Без категории'
}

const getTotalCalories = (product) => {
  if (typeof product.total_calories === 'number') return product.total_calories

  const caloriesPer100g = Number(product.calories || 0)
  const weight = Number(product.weight || 0)
  if (!caloriesPer100g || !weight) return 0
  return Math.round((caloriesPer100g * weight) / 100)
}

const fetchProducts = async () => {
  try {
    const response = await api.get('/api/products', {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    products.value = response.data.products || []
  } catch (error) {
    console.error('Ошибка при загрузке товаров:', error)
  }
}

const fetchCategories = async () => {
  try {
    const response = await api.get('/api/categories', {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    categories.value = response.data || []
  } catch (error) {
    console.error('Ошибка при загрузке категорий:', error)
  }
}

const openAddModal = () => {
  selectedProduct.value = null
  isModalOpen.value = true
}

const openEditModal = (product) => {
  selectedProduct.value = { ...product }
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
  selectedProduct.value = null
}

const onProductSaved = () => {
  fetchProducts()
  closeModal()
}

const confirmDelete = async (product) => {
  if (!confirm(`Удалить товар "${product.name}"?`)) return
  
  try {
    await api.delete(`/api/products/${product.id}`, {
      headers: {
        'Authorization': `Bearer ${authStore.getToken}`
      }
    })
    alert('✅ Товар удалён')
    fetchProducts()
  } catch (error) {
    console.error('Ошибка при удалении:', error)
    alert('❌ Ошибка при удалении товара')
  }
}

onMounted(() => {
  if (!authStore.isAuthenticated || !authStore.isAdmin) {
    router.push('/')
    return
  }
  fetchProducts()
  fetchCategories()
})
</script>
