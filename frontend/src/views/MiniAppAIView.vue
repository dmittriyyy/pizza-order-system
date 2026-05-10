<template>
  <div class="min-h-screen px-4 pt-6 pb-40">
    <div class="max-w-4xl mx-auto">
      <div class="premium-card overflow-hidden flex flex-col mini-ai-shell">
        <div class="bg-gradient-to-r from-primary-500 to-primary-600 p-5">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center">
              <span class="text-2xl">🤖</span>
            </div>
            <div>
              <h1 class="text-white font-bold text-2xl">WOKI</h1>
              <p class="text-white/70 text-sm">AI-помощник по меню и заказам</p>
            </div>
          </div>
        </div>

        <div ref="messagesContainer" class="flex-1 min-h-0 p-4 space-y-4 overflow-y-auto">
          <div
            v-for="(message, index) in messages"
            :key="index"
            class="flex"
            :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-[88%] px-4 py-3 rounded-[20px]"
              :class="message.role === 'user' ? 'bg-primary-500 text-white rounded-br-sm' : 'glass text-white rounded-bl-sm'"
            >
              <p class="text-sm whitespace-pre-line">{{ message.content }}</p>
            </div>
          </div>

          <div v-if="isTyping" class="flex justify-start">
            <div class="glass px-4 py-3 rounded-2xl rounded-bl-sm">
              <div class="flex space-x-2">
                <div class="w-2 h-2 bg-primary-400 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-primary-400 rounded-full animate-bounce delay-100"></div>
                <div class="w-2 h-2 bg-primary-400 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="mini-ai-composer p-4 border-t border-white/10 bg-dark-900/95">
          <form @submit.prevent="sendMessage" class="flex items-center gap-3 mini-ai-form">
            <input
              v-model="newMessage"
              type="text"
              placeholder="Спроси про меню, калории или добавление в корзину..."
              class="flex-1 glass px-4 py-3 rounded-[20px] text-white placeholder-gray-400 focus:outline-none"
            />
            <button type="submit" class="btn-primary px-5 py-3">Отправить</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import api from '@/services/api'

const isTyping = ref(false)
const newMessage = ref('')
const messagesContainer = ref(null)
const messages = ref([
  { role: 'assistant', content: 'Привет! Я WOKI 🍕 Могу подсказать по меню, подобрать блюдо и помочь добавить товар в корзину.' }
])

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim()) return

  const content = newMessage.value.trim()
  messages.value.push({ role: 'user', content })
  newMessage.value = ''
  isTyping.value = true
  scrollToBottom()

  try {
    const sessionId = localStorage.getItem('chat_session_id') || `session_${Date.now()}`
    localStorage.setItem('chat_session_id', sessionId)

    const response = await api.post('/api/chat/send', {
      message: content,
      session_id: sessionId,
    }, {
      timeout: 180000,
    })

    messages.value.push({
      role: 'assistant',
      content: response.data.response,
    })
  } catch (error) {
    console.error('Ошибка чата:', error)
    messages.value.push({
      role: 'assistant',
      content: 'Сейчас не получилось ответить. Попробуй ещё раз через пару секунд.',
    })
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
.mini-ai-shell {
  height: calc(100vh - 13rem);
  min-height: 520px;
}

.mini-ai-composer {
  padding-bottom: calc(1rem + env(safe-area-inset-bottom, 0px));
}

.mini-ai-form {
  align-items: stretch;
}

@media (max-width: 768px) {
  .mini-ai-shell {
    height: calc(100vh - 15rem);
    min-height: 480px;
  }
}
</style>
