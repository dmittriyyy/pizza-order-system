<template>
  <div class="min-h-screen">
    <!-- Герой секция -->
    <section class="relative h-[600px] flex items-center justify-center overflow-hidden">
      <!-- Фон -->
      <div class="absolute inset-0">
        <img 
          src="https://images.unsplash.com/photo-1513104890138-7c749659a591?w=1920&h=1080&fit=crop"
          alt="Pizza background"
          class="w-full h-full object-cover"
        />
        <div class="absolute inset-0 bg-gradient-to-b from-dark-950/70 via-dark-950/50 to-dark-950"></div>
      </div>

      <!-- Контент -->
      <div class="relative z-10 text-center px-4 max-w-4xl mx-auto">
        <h1 class="text-5xl md:text-7xl font-bold text-white mb-6 animate-fade-in">
          Лучшая пицца в <span class="text-gradient">городе</span>
        </h1>
        <p class="text-xl text-dark-300 mb-8 animate-fade-in" style="animation-delay: 0.2s">
          Готовим с любовью, доставляем с заботой. Попробуй идеальный вкус!
        </p>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in" style="animation-delay: 0.4s">
          <a href="#menu" class="btn-primary px-8 py-4 text-lg">
            Заказать сейчас
          </a>
          <a href="#about" class="btn-secondary px-8 py-4 text-lg">
            Узнать больше
          </a>
        </div>
      </div>
    </section>

    <!-- Преимущества -->
    <section class="py-16 px-4">
      <div class="max-w-7xl mx-auto">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="premium-card p-8 text-center">
            <div class="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span class="text-3xl">🚀</span>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">Быстрая доставка</h3>
            <p class="text-dark-400">Доставим за 30 минут или пицца бесплатно</p>
          </div>
          
          <div class="premium-card p-8 text-center">
            <div class="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span class="text-3xl">👨‍🍳</span>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">Опытные повара</h3>
            <p class="text-dark-400">Готовят по традиционным итальянским рецептам</p>
          </div>
          
          <div class="premium-card p-8 text-center">
            <div class="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span class="text-3xl">🌿</span>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">Свежие ингредиенты</h3>
            <p class="text-dark-400">Только фермерские продукты высшего качества</p>
          </div>
        </div>
      </div>
    </section>

    <section v-if="authStore.isAuthenticated" class="py-12 px-4">
      <div class="max-w-6xl mx-auto">
        <div class="premium-card p-8">
          <div class="mb-8">
            <div>
              <p class="text-primary-400 text-sm font-semibold uppercase tracking-[0.2em] mb-2">AI Рекомендации</p>
              <h2 class="text-3xl md:text-4xl font-bold text-white mb-3">Здравствуйте! Мы рады видеть вас снова</h2>
              <p class="text-dark-500 text-sm md:text-base mb-3">Персонально для вас</p>
              <p class="text-dark-300 text-base md:text-lg max-w-3xl">{{ recommendation.message }}</p>
            </div>
          </div>

          <div v-if="ordersCount >= 3 && recommendation.suggestions?.length" class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <article
              v-for="item in recommendation.suggestions.slice(0, 3)"
              :key="item.product_id"
              class="glass rounded-3xl p-5 min-h-[220px] flex flex-col"
            >
              <p class="text-white text-xl font-bold mb-2">{{ item.name }}</p>
              <p class="text-dark-400 text-sm leading-relaxed mb-4 flex-1">{{ item.reason }}</p>
              <button
                @click="handleAddRecommendation(item.product_id)"
                class="btn-primary w-full py-3 text-sm mt-auto"
              >
                В корзину
              </button>
            </article>
          </div>
          <div v-else class="glass p-5 rounded-3xl">
            <p class="text-white text-lg font-bold mb-2">Рекомендации скоро появятся</p>
            <p class="text-dark-400 text-sm leading-relaxed">
              Когда история заказов станет чуть богаче, я смогу точнее подобрать блюда и дополнения именно для вас.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Меню (Mobile: Glass background, Desktop: Dark background) -->
    <section id="menu" class="py-8 md:py-16 px-4 bg-white/5 backdrop-blur-sm md:bg-dark-900/50">
      <div class="max-w-7xl mx-auto">
        <div class="text-center mb-8 md:mb-12">
          <h2 class="text-3xl md:text-4xl font-bold text-white mb-4">Наше <span class="text-gradient">меню</span></h2>
          <p class="text-dark-400 text-base md:text-lg">Выбирай свои любимые вкусы</p>
        </div>

        <CategoryFilter />

        <div v-if="productsStore.isLoading" class="text-center py-12">
          <div class="inline-block w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          <p class="text-dark-400 mt-4">Загружаем меню...</p>
        </div>

        <div v-else-if="filteredProducts.length === 0" class="text-center py-12">
          <p class="text-dark-400 text-lg">В этой категории пока пусто</p>
        </div>

        <!-- Mobile: 2 columns, Desktop: 4 columns -->
        <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
          <ProductCard 
            v-for="product in filteredProducts" 
            :key="product.id"
            :product="product"
          />
        </div>
      </div>
    </section>

    <!-- О нас -->
    <section id="about" class="py-16 px-4">
      <div class="max-w-4xl mx-auto text-center">
        <h2 class="text-4xl font-bold text-white mb-6">О <span class="text-gradient">нас</span></h2>
        <p class="text-dark-300 text-lg leading-relaxed mb-8">
          Мы — команда энтузиастов, которые любят пиццу так же, как и вы. 
          С 2026 года мы готовим для вас лучшую пиццу в городе, используя только 
          свежие ингредиенты и традиционные рецепты.
        </p>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div>
            <p class="text-4xl font-bold text-gradient">50K+</p>
            <p class="text-dark-400 mt-2">Довольных клиентов</p>
          </div>
          <div>
            <p class="text-4xl font-bold text-gradient">100K+</p>
            <p class="text-dark-400 mt-2">Приготовленных пицц</p>
          </div>
          <div>
            <p class="text-4xl font-bold text-gradient">30 мин</p>
            <p class="text-dark-400 mt-2">Среднее время доставки</p>
          </div>
          <div>
            <p class="text-4xl font-bold text-gradient">4.9</p>
            <p class="text-dark-400 mt-2">Рейтинг в приложениях</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Футер -->
    <footer class="border-t border-dark-700 py-8 px-4">
      <div class="max-w-7xl mx-auto text-center text-dark-400">
        <p>© 2026 Piazza Pizza. Все права защищены.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import ProductCard from '@/components/ProductCard.vue'
import CategoryFilter from '@/components/CategoryFilter.vue'
import { useProductsStore } from '@/stores/products'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import { orderService, recommendationService } from '@/services'

const productsStore = useProductsStore()
const authStore = useAuthStore()
const cartStore = useCartStore()

const filteredProducts = computed(() => productsStore.filteredProducts)
const recommendation = ref({
  message: 'Мы подбираем предложения с учётом ваших заказов и вкусовых предпочтений.',
  suggestions: [],
})
const ordersCount = ref(0)

const loadRecommendations = async () => {
  if (!authStore.isAuthenticated) {
    ordersCount.value = 0
    recommendation.value = { message: '', suggestions: [] }
    return
  }

  try {
    if (!authStore.user && authStore.token) {
      await authStore.fetchCurrentUser()
    }

    const orders = await orderService.getAll({ limit: 20 })
    ordersCount.value = Array.isArray(orders) ? orders.length : 0

    if (ordersCount.value >= 3) {
      recommendation.value = await recommendationService.getPersonal()
    } else {
      recommendation.value = {
        message: 'Мы уже запоминаем ваши предпочтения. После нескольких заказов здесь появятся персональные рекомендации для вас.',
        suggestions: [],
      }
    }
  } catch (error) {
    console.error('Ошибка при загрузке AI-рекомендаций:', error)
    recommendation.value = {
      message: 'Сейчас не удалось загрузить персональные рекомендации, но этот блок останется доступен.',
      suggestions: [],
    }
  }
}

const handleAddRecommendation = async (productId) => {
  try {
    await cartStore.addToCart(productId, 1)
  } catch (error) {
    console.error('Ошибка при добавлении рекомендации в корзину:', error)
  }
}

onMounted(async () => {
  try {
    await productsStore.initialize()
    console.log('Товары загружены:', productsStore.products.length)
    console.log('Категории:', productsStore.categories.length)
    await loadRecommendations()
  } catch (error) {
    console.error('Ошибка при загрузке меню:', error)
  }
})

watch(
  () => [authStore.token, authStore.user?.id],
  async () => {
    await loadRecommendations()
  }
)
</script>
