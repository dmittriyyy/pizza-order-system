<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Overlay -->
    <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="close"></div>

    <!-- Модалка -->
    <div class="relative premium-card max-w-4xl w-full max-h-[90vh] overflow-y-auto animate-fade-in">
      <!-- Заголовок -->
      <div class="sticky top-0 bg-dark-900/95 backdrop-blur border-b border-dark-700 p-6 flex items-center justify-between z-10">
        <h2 class="text-2xl font-bold text-white">
          {{ isEdit ? '✏️ Редактирование товара' : '➕ Новый товар' }}
        </h2>
        <button @click="close" class="w-10 h-10 glass-button rounded-full flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Форма -->
      <form @submit.prevent="saveProduct" class="p-6 space-y-6">
        <!-- Основная информация -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">Название *</label>
            <input
              v-model="formData.name"
              type="text"
              required
              class="input-primary"
              placeholder="Например: Пепперони"
            />
          </div>
          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">Категория *</label>
            <select v-model="formData.category_id" required class="input-primary">
              <option value="">Выберите категорию</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-dark-300 text-sm font-medium mb-2">Описание *</label>
          <textarea
            v-model="formData.description"
            required
            rows="3"
            class="input-primary"
            placeholder="Описание товара..."
          ></textarea>
        </div>

        <!-- Цена и скидка -->
        <div class="grid grid-cols-2 gap-6">
          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">Цена (₽) *</label>
            <input
              v-model.number="formData.price"
              type="number"
              step="0.01"
              required
              class="input-primary"
            />
          </div>
          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">Скидка (%)</label>
            <input
              v-model.number="formData.discount"
              type="number"
              min="0"
              max="100"
              class="input-primary"
            />
          </div>
        </div>

        <!-- КБЖУ -->
        <div class="glass p-4 rounded-2xl">
          <h3 class="text-lg font-bold text-white mb-4">📊 Пищевая ценность (на 100г)</h3>
          <div class="grid grid-cols-4 gap-4">
            <div>
              <label class="block text-dark-300 text-xs mb-1">Калории (ккал)</label>
              <input v-model.number="formData.calories" type="number" class="input-primary text-sm" />
            </div>
            <div>
              <label class="block text-dark-300 text-xs mb-1">Белки (г)</label>
              <input v-model.number="formData.protein" type="number" step="0.1" class="input-primary text-sm" />
            </div>
            <div>
              <label class="block text-dark-300 text-xs mb-1">Жиры (г)</label>
              <input v-model.number="formData.fat" type="number" step="0.1" class="input-primary text-sm" />
            </div>
            <div>
              <label class="block text-dark-300 text-xs mb-1">Углеводы (г)</label>
              <input v-model.number="formData.carbohydrates" type="number" step="0.1" class="input-primary text-sm" />
            </div>
          </div>
        </div>

        <!-- Вес и состав -->
        <div class="grid grid-cols-2 gap-6">
          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">Вес порции (г)</label>
            <input v-model.number="formData.weight" type="number" class="input-primary" />
          </div>
          <div>
            <label class="block text-dark-300 text-sm font-medium mb-2">Состав (через запятую)</label>
            <input
              v-model="ingredientsInput"
              type="text"
              class="input-primary"
              placeholder="моцарелла, томаты, базилик"
            />
          </div>
        </div>

        <!-- Фото -->
        <div>
          <label class="block text-dark-300 text-sm font-medium mb-2">📷 Фото товара</label>
          <div class="glass p-4 rounded-2xl">
            <div v-if="formData.image_url" class="mb-4">
              <img :src="formData.image_url" alt="Preview" class="h-40 rounded-xl object-cover" />
            </div>
            <div class="flex items-center space-x-4">
              <input
                v-model="formData.image_url"
                type="url"
                placeholder="URL изображения"
                class="input-primary flex-1"
              />
              <label class="btn-secondary px-4 py-2 cursor-pointer">
                📁 Загрузить
                <input
                  type="file"
                  @change="onFileSelected"
                  accept="image/*"
                  class="hidden"
                />
              </label>
            </div>
            <p v-if="uploading" class="text-dark-400 text-sm mt-2">🔄 Загрузка...</p>
          </div>
        </div>

        <!-- Кнопки -->
        <div class="flex items-center justify-end space-x-4 pt-6 border-t border-dark-700">
          <button type="button" @click="close" class="btn-secondary px-6 py-3">
            Отмена
          </button>
          <button
            type="submit"
            :disabled="isSaving"
            class="btn-primary px-6 py-3 disabled:opacity-50"
          >
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
  product: Object,
  categories: Array,
  isOpen: Boolean,
})

const emit = defineEmits(['close', 'saved'])

const isEdit = computed(() => !!props.product)
const isSaving = ref(false)
const uploading = ref(false)
const ingredientsInput = ref('')

const defaultForm = {
  name: '',
  description: '',
  price: 0,
  category_id: '',
  image_url: '',
  calories: 0,
  protein: 0,
  fat: 0,
  carbohydrates: 0,
  weight: 0,
  discount: 0,
  ingredients: [],
}

const formData = reactive({ ...defaultForm })

watch(() => props.product, (newProduct) => {
  if (newProduct) {
    Object.assign(formData, newProduct)
    ingredientsInput.value = newProduct.ingredients?.join(', ') || ''
  } else {
    Object.assign(formData, defaultForm)
    ingredientsInput.value = ''
  }
}, { immediate: true })

const close = () => {
  Object.assign(formData, defaultForm)
  emit('close')
}

const onFileSelected = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  uploading.value = true
  try {
    const formDataUpload = new FormData()
    formDataUpload.append('file', file)

    // Если редактируем существующий товар
    if (props.product?.id) {
      const response = await api.post(
        `/api/products/${props.product.id}/images`,
        formDataUpload,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token') ? `Bearer ${localStorage.getItem('access_token')}` : ''}`,
          },
        }
      )
      formData.image_url = response.data.image_url
      alert('✅ Фото загружено!')
    } else {
      alert('⚠️ Сначала сохраните товар, потом загрузите фото')
    }
  } catch (error) {
    console.error('Ошибка загрузки фото:', error)
    alert('❌ Ошибка при загрузке фото: ' + (error.response?.data?.detail || error.message))
  } finally {
    uploading.value = false
  }
}

const saveProduct = async () => {
  isSaving.value = true
  try {
    // Преобразуем состав из строки в массив
    const ingredients = ingredientsInput.value
      .split(',')
      .map(i => i.trim())
      .filter(i => i)

    const payload = {
      ...formData,
      ingredients,
    }

    const token = localStorage.getItem('access_token')
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    }

    if (isEdit.value) {
      // Обновление
      await api.patch(`/api/products/${props.product.id}`, payload, { headers })
    } else {
      // Создание
      await api.post('/api/products', payload, { headers })
    }

    emit('saved')
  } catch (error) {
    console.error('Ошибка при сохранении:', error)
    alert('❌ Ошибка при сохранении товара: ' + (error.response?.data?.detail || error.message))
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
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
