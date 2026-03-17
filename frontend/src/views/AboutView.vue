<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-3xl mx-auto text-center">
      <h1 class="text-4xl font-bold text-white mb-6">О <span class="text-gradient">нас</span></h1>
      
      <div class="premium-card p-8 mb-8">
        <p class="text-dark-300 text-lg leading-relaxed mb-6">
          <strong class="text-white">Velo Pizza</strong> — это не просто доставка еды, это философия вкуса и качества. 
          Мы начали свой путь в 2026 году с небольшой пиццерии и выросли в любимую сеть города.
        </p>
        <p class="text-dark-300 text-lg leading-relaxed">
          Наши повара проходят обучение в Италии, чтобы передать вам настоящий вкус Неаполя. 
          Мы используем только фермерские продукты: свежее мясо, овощи с грядки и сыр от местных производителей.
        </p>
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

      <router-link to="/" class="btn-primary inline-block px-8 py-4">
        Перейти в меню
      </router-link>
    </div>
  </div>
</template>

<script setup>
</script>
