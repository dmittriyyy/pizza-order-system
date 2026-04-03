<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-3xl mx-auto text-center">
      <h1 class="text-4xl font-bold text-white mb-6">О <span class="text-gradient">нас</span></h1>

      <div class="premium-card p-8 mb-8">
        <p class="text-dark-300 text-lg leading-relaxed mb-6">
          <strong class="text-white">Piazza Pizza</strong> — это не просто доставка еды, это философия вкуса и качества.
          Мы начали свой путь в 2020 году с небольшой пиццерии и выросли в любимую сеть города.
        </p>
        <p class="text-dark-300 text-lg leading-relaxed">
          Наши повара проходят обучение в Италии, чтобы передать вам настоящий вкус Неаполя.
          Мы используем только фермерские продукты: свежее мясо, овощи с грядки и сыр от местных производителей.
        </p>
      </div>

      <!-- Адрес пиццерии -->
      <div class="premium-card p-8 mb-8">
        <h2 class="text-2xl font-bold text-white mb-4">📍 Наш адрес</h2>
        <div class="text-dark-300 text-lg mb-2">
          <p>г. Калуга, <strong class="text-white">улица Кирова, 1</strong></p>
          <p class="text-dark-400 text-sm">Индекс: 248001</p>
        </div>
        <div class="flex items-center justify-center space-x-4 text-dark-400 text-sm mb-6">
          <span>🕐</span>
          <span>Ежедневно с 10:00 до 23:00</span>
        </div>
        
        <!-- Карта пиццерии -->
        <div class="w-full h-96 rounded-2xl overflow-hidden border border-dark-700 mb-4">
          <iframe
            src="https://yandex.ru/map-widget/v1/?um=constructor%3A0cdb2344ef96dd5eec2eb0de6d109ffcb3ea69e5b0d658ff82ca96d63b814fbe&amp;source=constructor"
            width="100%"
            height="400"
            frameborder="0"
            class="rounded-2xl"
          ></iframe>
        </div>
        
        <!-- Ссылка на Яндекс Карты -->
        <a
          href="https://yandex.ru/maps/-/CDu~KJq-"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center space-x-2 text-primary-400 hover:text-primary-300 transition-colors"
        >
          <span>🗺️</span>
          <span>Открыть карту в Яндекс Картах</span>
        </a>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div class="premium-card p-6">
          <h3 class="text-xl font-bold text-white mb-4">🎯 Наша миссия</h3>
          <p class="text-dark-400">
            Дарить людям радость от вкусной еды и объединять семьи за общим столом.
          </p>
        </div>
        <div class="premium-card p-6">
          <h3 class="text-xl font-bold text-white mb-4">⭐ Наши ценности</h3>
          <p class="text-dark-400">
            Качество, честность и забота о каждом клиенте — основа нашего бизнеса.
          </p>
        </div>
      </div>

      <!-- Условия использования Яндекс Карт -->
      <div class="glass p-6 rounded-2xl mb-8">
        <p class="text-dark-400 text-sm">
          🔗 Интеграция с Яндекс Картами осуществляется в соответствии с 
          <a
            href="https://yandex.ru/legal/maps_api/"
            target="_blank"
            rel="noopener noreferrer"
            class="text-primary-400 hover:text-primary-300 underline"
          >
            Условиями использования сервисов Яндекс Карт
          </a>
        </p>
      </div>

      <router-link to="/" class="btn-primary inline-block px-8 py-4">
        Перейти в меню
      </router-link>
    </div>
  </div>
</template>

<script setup>
</script>
