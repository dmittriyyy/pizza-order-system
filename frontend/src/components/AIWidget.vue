<template>
  <div class="fixed bottom-6 right-6 z-40">
    <!-- Окно чата -->
    <transition 
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform translate-y-4 opacity-0 scale-95"
      enter-to-class="transform translate-y-0 opacity-100 scale-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-y-0 opacity-100 scale-100"
      leave-to-class="transform translate-y-4 opacity-0 scale-95"
    >
      <div 
        v-if="isOpen"
        class="absolute bottom-20 right-0 w-96 max-w-[calc(100vw-3rem)] glass-dark border border-dark-700 rounded-3xl shadow-2xl overflow-hidden"
      >
        <!-- Заголовок чата -->
        <div class="bg-gradient-to-r from-primary-500 to-primary-600 p-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <span class="text-xl">🤖</span>
              </div>
              <div>
                <h3 class="text-white font-bold">WOKI</h3>
                <p class="text-white/70 text-xs">Онлайн • Отвечает за 1.5с</p>
              </div>
            </div>
            <button 
              @click="closeChat"
              class="p-2 hover:bg-white/20 rounded-full transition-colors"
            >
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- Сообщения -->
        <div ref="messagesContainer" class="h-80 overflow-y-auto p-4 space-y-4 scrollbar-hide">
          <div 
            v-for="(message, index) in messages" 
            :key="index"
            :class="[
              'flex',
              message.role === 'user' ? 'justify-end' : 'justify-start'
            ]"
          >
            <div
              :class="[
                'max-w-[80%] px-4 py-3 rounded-2xl',
                message.role === 'user' 
                  ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-br-sm'
                  : 'glass text-white rounded-bl-sm'
              ]"
            >
              <p class="text-sm">{{ message.content }}</p>
              <p 
                :class="[
                  'text-xs mt-1',
                  message.role === 'user' ? 'text-white/70' : 'text-dark-400'
                ]"
              >
                {{ formatTime(message.timestamp) }}
              </p>
            </div>
          </div>
          
          <!-- Индикатор набора -->
          <div v-if="isTyping" class="flex justify-start">
            <div class="glass px-4 py-3 rounded-2xl rounded-bl-sm">
              <div class="flex space-x-2">
                <div class="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                <div class="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                <div class="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Поле ввода -->
        <div class="p-4 border-t border-dark-700">
          <form @submit.prevent="sendMessage" class="flex items-center space-x-3">
            <input
              v-model="newMessage"
              type="text"
              placeholder="Спросите о пицце..."
              class="flex-1 glass px-4 py-3 rounded-2xl text-white placeholder-dark-500 focus:outline-none focus:border-primary-500 transition-colors"
              :disabled="isTyping"
            />
            <button
              type="submit"
              :disabled="!newMessage.trim() || isTyping"
              class="btn-primary p-3 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
              </svg>
            </button>
          </form>
        </div>
      </div>
    </transition>

    <!-- Кнопка открытия -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform scale-0 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-0 opacity-0"
    >
      <button
        v-show="!isOpen"
        @click="openChat"
        class="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full shadow-lg shadow-primary-500/30 flex items-center justify-center hover:scale-110 active:scale-95 transition-all duration-300"
      >
        <span class="text-3xl">🤖</span>
      </button>
    </transition>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import api from '@/services/api'

const isOpen = ref(false)
const newMessage = ref('')
const isTyping = ref(false)
const messagesContainer = ref(null)
const sessionId = ref(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)

const messages = ref([
  {
    role: 'assistant',
    content: 'Привет! Я WOKI, твой AI-помощник по пицце 🍕 Спрашивай меня о чём угодно!',
    timestamp: new Date(),
  },
])

// Загрузка истории при открытии
const loadHistory = async () => {
  try {
    const response = await api.get(`/api/chat/history?session_id=${sessionId.value}&limit=20`)
    if (response.data.messages && response.data.messages.length > 0) {
      messages.value = response.data.messages.map(msg => ({
        role: 'user',
        content: msg.message,
        timestamp: new Date(msg.timestamp)
      })).reduce((acc, msg, idx) => {
        // Добавляем пару сообщение-ответ
        if (idx % 2 === 0 && response.data.messages[idx/2]) {
          acc.push({
            role: 'assistant',
            content: response.data.messages[idx/2].response,
            timestamp: new Date(response.data.messages[idx/2].timestamp)
          })
        }
        return acc
      }, [])
    }
  } catch (error) {
    console.log('История не загружена (начало новой сессии)')
  }
}

const openChat = () => {
  isOpen.value = true
  scrollToBottom()
  if (messages.value.length === 1) {
    loadHistory()
  }
}

const closeChat = () => {
  isOpen.value = false
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatTime = (date) => {
  return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

const sendMessage = async () => {
  const content = newMessage.value.trim()
  if (!content) return

  // Добавляем сообщение пользователя
  messages.value.push({
    role: 'user',
    content,
    timestamp: new Date(),
  })
  newMessage.value = ''
  scrollToBottom()

  // Отправляем в Ollama через API
  isTyping.value = true

  try {
    const response = await api.post('/api/chat/send', {
      message: content,
      session_id: sessionId.value
    }, {
      timeout: 180000  // 180 секунд таймаут
    })

    messages.value.push({
      role: 'assistant',
      content: response.data.response,
      timestamp: new Date(),
    })
  } catch (error) {
    console.error('Ошибка отправки сообщения:', error)
    messages.value.push({
      role: 'assistant',
      content: 'Извините, произошла ошибка. Попробуйте ещё раз.',
      timestamp: new Date(),
    })
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

onMounted(() => {
  // Инициализация при загрузке компонента
  console.log('🤖 AI Widget initialized')
})
</script>
