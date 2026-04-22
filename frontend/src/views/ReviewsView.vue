<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-5xl mx-auto">
      <div class="text-center mb-10">
        <h1 class="text-4xl font-bold text-white mb-4">Отзывы <span class="text-gradient">клиентов</span></h1>
        <p class="text-dark-400 text-lg">Живые впечатления о заказах Piazza Pizza</p>
      </div>

      <div v-if="isLoading" class="text-center py-12">
        <div class="inline-block w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
        <p class="text-dark-400 mt-4">Загружаем отзывы...</p>
      </div>

      <div v-else-if="reviews.length === 0" class="premium-card p-8 text-center">
        <p class="text-dark-300 text-lg">Пока нет публичных отзывов.</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <article v-for="review in reviews" :key="review.id" class="premium-card p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="text-primary-400 text-lg">{{ renderStars(review.rating) }}</div>
            <span class="text-xs text-dark-500">{{ review.author_name || review.user_login || 'Клиент Piazza Pizza' }}</span>
          </div>
          <p class="text-white text-base leading-relaxed mb-4">
            {{ review.comment || 'Клиент оставил высокую оценку без комментария.' }}
          </p>
          <div class="text-sm text-dark-400">
            {{ formatDate(review.created_at) }}
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { feedbackService } from '@/services'

const isLoading = ref(false)
const reviews = ref([])

const renderStars = (rating) => '★'.repeat(rating) + '☆'.repeat(5 - rating)

const formatDate = (value) => new Date(value).toLocaleDateString('ru-RU', {
  day: '2-digit',
  month: 'long',
  year: 'numeric',
})

onMounted(async () => {
  isLoading.value = true
  try {
    reviews.value = await feedbackService.getPublic({ limit: 20 })
  } catch (error) {
    console.error('Ошибка загрузки отзывов:', error)
  } finally {
    isLoading.value = false
  }
})
</script>
