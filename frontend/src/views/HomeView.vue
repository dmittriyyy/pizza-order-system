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

      <div v-if="isTelegramMiniApp && !authStore.isAuthenticated" class="absolute top-4 left-4 right-4 z-20">
        <div class="max-w-5xl mx-auto">
          <div class="glass rounded-[24px] px-4 py-3 md:px-5 md:py-4 flex items-center justify-between gap-4">
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-11 h-11 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-lg shadow-primary-500/20 shrink-0">
                <span class="text-xl">🍕</span>
              </div>
              <div class="min-w-0">
                <p class="text-white font-semibold text-sm md:text-base truncate">Piazza Pizza</p>
                <p class="text-dark-300 text-xs md:text-sm truncate">Войдите, чтобы заказывать в Mini App</p>
              </div>
            </div>

            <div class="flex items-center gap-2 shrink-0">
              <router-link to="/register" class="mini-auth-link">
                Регистрация
              </router-link>
              <router-link to="/login" class="mini-auth-button">
                Войти
              </router-link>
            </div>
          </div>
        </div>
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

    <section v-if="authStore.isAuthenticated" class="px-4 pb-4 md:pb-6">
      <div class="max-w-7xl mx-auto">
        <div class="premium-card p-4 md:p-5">
          <p class="text-primary-400 text-xs font-semibold uppercase tracking-[0.18em] text-center mb-2">
            AI Рекомендации
          </p>

          <div class="flex items-center justify-center gap-2 mb-3">
            <h2 class="text-base md:text-lg font-bold text-white text-center">Что взять сегодня</h2>
            <span
              v-if="isRecommendationsLoading"
              class="inline-block w-3 h-3 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"
            ></span>
          </div>

          <p class="text-dark-300 text-sm md:text-base text-center compact-message max-w-3xl mx-auto">
            {{ recommendation.message }}
          </p>

          <div
            v-if="ordersCount >= 3 && recommendation.suggestions?.length"
            class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3"
          >
            <article
              v-for="item in recommendationCards"
              :key="item.product_id"
              class="glass rounded-2xl overflow-hidden flex flex-col"
            >
              <div class="relative h-36 overflow-hidden">
                <img
                  :src="item.image_url || defaultRecommendationImage"
                  :alt="item.name"
                  class="w-full h-full object-cover"
                />
                <div class="absolute inset-0 bg-gradient-to-t from-dark-950 via-dark-950/40 to-transparent"></div>
                <div class="absolute left-4 right-4 bottom-4 flex items-end justify-between gap-3">
                  <p class="text-white text-sm md:text-base font-bold leading-tight">{{ item.name }}</p>
                  <div class="shrink-0 text-right">
                    <span class="text-lg font-bold text-gradient">{{ Math.round(item.price) }}</span>
                    <span class="text-dark-300 text-xs ml-1">₽</span>
                  </div>
                </div>
              </div>

              <div class="p-4 flex-1 flex flex-col">
                <p class="text-primary-400 text-[11px] font-semibold uppercase tracking-[0.16em] mb-2">
                  Почему рекомендуем
                </p>
                <p class="text-dark-300 text-sm compact-reason flex-1">
                  {{ item.reason }}
                </p>

                <button
                  type="button"
                  class="btn-primary mt-4 w-full px-4 py-3 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="isRecommendationAdding(item.product_id)"
                  @click="handleAddRecommendation(item.product_id)"
                >
                  <span v-if="isRecommendationAdding(item.product_id)">Добавляем...</span>
                  <span v-else>В корзину</span>
                </button>
              </div>
            </article>
          </div>

          <div v-else class="mt-4 glass rounded-2xl px-4 py-3">
            <p class="text-dark-300 text-sm leading-relaxed text-center">
              Сделайте ещё пару заказов, и здесь появятся короткие персональные подсказки.
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
import { isTelegramMiniApp as detectTelegramMiniApp } from '@/services/telegram'

const productsStore = useProductsStore()
const authStore = useAuthStore()
const cartStore = useCartStore()

const filteredProducts = computed(() => productsStore.filteredProducts)
const isTelegramMiniApp = computed(() => detectTelegramMiniApp())
const recommendation = ref({
  message: 'Мы подбираем предложения с учётом ваших заказов и вкусовых предпочтений.',
  suggestions: [],
})
const ordersCount = ref(0)
const isRecommendationsLoading = ref(false)
const addingRecommendationIds = ref([])
const defaultRecommendationImage = 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800&h=600&fit=crop'

const recommendationCards = computed(() =>
  (recommendation.value.suggestions || [])
    .slice(0, 3)
    .map((item) => {
      const product = productsStore.getProductById(item.product_id)

      return {
        ...item,
        image_url: product?.image_url,
        price: product?.price ?? 0,
      }
    })
)

const isRecommendationAdding = (productId) => addingRecommendationIds.value.includes(productId)

const loadRecommendations = async () => {
  if (!authStore.isAuthenticated) {
    ordersCount.value = 0
    recommendation.value = { message: '', suggestions: [] }
    isRecommendationsLoading.value = false
    return
  }

  isRecommendationsLoading.value = true

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
  } finally {
    isRecommendationsLoading.value = false
  }
}

const handleAddRecommendation = async (productId) => {
  if (isRecommendationAdding(productId)) {
    return
  }

  addingRecommendationIds.value = [...addingRecommendationIds.value, productId]

  try {
    await cartStore.addToCart(productId, 1)
  } catch (error) {
    console.error('Ошибка при добавлении рекомендации в корзину:', error)
  } finally {
    addingRecommendationIds.value = addingRecommendationIds.value.filter((id) => id !== productId)
  }
}

onMounted(async () => {
  const [productsResult] = await Promise.allSettled([
    productsStore.initialize(),
    loadRecommendations(),
  ])

  if (productsResult.status === 'rejected') {
    console.error('Ошибка при загрузке меню:', productsResult.reason)
  }
})

watch(
  () => [authStore.token, authStore.user?.id],
  async () => {
    await loadRecommendations()
  }
)
</script>

<style scoped>
.compact-message {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.compact-reason {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.mini-auth-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  padding: 0 18px;
  border-radius: 16px;
  background: linear-gradient(135deg, #ea670a, #e65a00);
  color: #fff;
  font-weight: 700;
  font-size: 14px;
  box-shadow: 0 14px 28px rgba(234, 103, 10, 0.2);
}

.mini-auth-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  padding: 0 16px;
  border-radius: 16px;
  color: #d1d5db;
  font-weight: 600;
  font-size: 14px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
}
</style>
