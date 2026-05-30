<template>
  <div class="fixed md:right-6 right-4 z-[100] md:bottom-24 bottom-[100px]">
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
        class="absolute bottom-0 right-0 w-[calc(100vw-32px)] md:w-96 h-[70vh] md:h-[500px] md:rounded-3xl rounded-t-[30px] rounded-b-none glass border border-white/20 md:border-dark-700 shadow-2xl overflow-hidden flex flex-col"
      >
        <div class="bg-gradient-to-r from-primary-500 to-primary-600 p-4 flex-shrink-0">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <span class="text-xl">{{ currentAgent.icon }}</span>
              </div>
              <div>
                <h3 class="text-white font-bold">{{ currentAgent.title }}</h3>
                <p class="text-white/70 text-xs">{{ currentAgent.subtitle }}</p>
              </div>
            </div>
            <button @click="closeChat" class="p-2 hover:bg-white/20 rounded-full">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
          </div>

          <div class="mt-3 grid grid-cols-2 gap-2">
            <button
              v-for="agent in agents"
              :key="agent.key"
              type="button"
              class="rounded-2xl px-3 py-2 text-sm font-semibold transition"
              :class="activeAgent === agent.key ? 'bg-white text-primary-700' : 'bg-white/15 text-white'"
              @click="switchAgent(agent.key)"
            >
              {{ agent.label }}
            </button>
          </div>
        </div>

        <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
          <div v-for="(message, index) in messages" :key="index" class="flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
            <div class="max-w-[85%] px-4 py-3 rounded-[20px]" :class="message.role === 'user' ? 'bg-primary-500 text-white rounded-br-sm' : 'glass text-white rounded-bl-sm'">
              <p class="text-sm whitespace-pre-line">{{ message.content }}</p>
            </div>
          </div>
          <div v-if="isTyping" class="flex justify-start">
            <div class="glass px-4 py-3 rounded-2xl rounded-bl-sm">
              <div class="flex space-x-2"><div class="w-2 h-2 bg-primary-400 rounded-full animate-bounce"></div><div class="w-2 h-2 bg-primary-400 rounded-full animate-bounce delay-100"></div><div class="w-2 h-2 bg-primary-400 rounded-full animate-bounce delay-200"></div></div>
            </div>
          </div>
        </div>

        <div class="p-4 border-t border-white/10 flex-shrink-0">
          <form @submit.prevent="sendMessage" class="flex items-center space-x-3">
            <input v-model="newMessage" type="text" :placeholder="currentAgent.placeholder" class="flex-1 glass px-4 py-3 rounded-[20px] text-white placeholder-gray-400 focus:outline-none" />
            <button type="submit" class="btn-primary p-3 rounded-[20px]">🚀</button>
          </form>
        </div>
      </div>
    </transition>

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
        class="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full shadow-lg shadow-primary-500/30 flex items-center justify-center hover:scale-110 active:scale-95 transition-all"
      >
        <span class="text-3xl">{{ currentAgent.icon }}</span>
      </button>
    </transition>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'
import api from '@/services/api'

const agents = [
  {
    key: 'consultant',
    label: 'Консультант',
    title: 'WOKI',
    subtitle: 'Меню и заказ',
    placeholder: 'Спросите о пицце или корзине...',
    welcome: 'Привет! Я WOKI 🍕 Помогу по меню, рекомендациям и добавлению в корзину.',
    icon: '🤖',
  },
  {
    key: 'support',
    label: 'Техподдержка',
    title: 'WOKI Support',
    subtitle: 'Заказ и доставка',
    placeholder: 'Где заказ, как добраться, как забрать...',
    welcome: 'Привет! Я агент техподдержки. Помогу со статусом заказа, доставкой, адресом и самовывозом.',
    icon: '🛟',
  },
]

const isOpen = ref(false)
const activeAgent = ref('consultant')
const newMessage = ref('')
const isTyping = ref(false)
const messagesContainer = ref(null)
const agentMessages = ref({
  consultant: [{ role: 'assistant', content: agents[0].welcome }],
  support: [{ role: 'assistant', content: agents[1].welcome }],
})

const currentAgent = computed(() => agents.find(agent => agent.key === activeAgent.value) || agents[0])
const messages = computed(() => agentMessages.value[activeAgent.value])

const openChat = () => {
  isOpen.value = true
  scrollToBottom()
}

const closeChat = () => {
  isOpen.value = false
}

const switchAgent = (agentKey) => {
  activeAgent.value = agentKey
  scrollToBottom()
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
}

const sendMessage = async () => {
  if (!newMessage.value.trim()) return
  const content = newMessage.value.trim()
  agentMessages.value[activeAgent.value].push({ role: 'user', content })
  newMessage.value = ''
  isTyping.value = true
  scrollToBottom()

  try {
    const sessionStorageKey = `chat_session_id_${activeAgent.value}`
    const sessionId = localStorage.getItem(sessionStorageKey) || `session_${activeAgent.value}_${Date.now()}`
    localStorage.setItem(sessionStorageKey, sessionId)

    const response = await api.post('/api/chat/send', {
      message: content,
      session_id: sessionId,
      agent_type: activeAgent.value,
    }, {
      timeout: 180000,
    })

    agentMessages.value[activeAgent.value].push({
      role: 'assistant',
      content: response.data.response,
      timestamp: new Date(),
    })
  } catch (error) {
    console.error('Ошибка чата:', error)
    agentMessages.value[activeAgent.value].push({
      role: 'assistant',
      content: 'Сейчас не получилось ответить. Попробуй ещё раз через минуту.',
    })
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}
</script>
