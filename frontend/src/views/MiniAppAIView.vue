<template>
  <div class="mini-ai-page">
    <section class="mini-ai-shell">
      <header class="mini-ai-header">
        <div class="mini-ai-avatar">AI</div>
        <div class="min-w-0">
          <h1 class="mini-ai-title">WOKI</h1>
          <p class="mini-ai-subtitle">Меню, подбор вкуса и помощь с заказом</p>
        </div>
      </header>

      <div ref="messagesContainer" class="mini-ai-messages">
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="mini-ai-message-row"
          :class="message.role === 'user' ? 'mini-ai-message-row--user' : 'mini-ai-message-row--assistant'"
        >
          <div
            class="mini-ai-bubble"
            :class="message.role === 'user' ? 'mini-ai-bubble--user' : 'mini-ai-bubble--assistant'"
          >
            <p>{{ message.content }}</p>
          </div>
        </div>

        <div v-if="messages.length === 1" class="mini-ai-prompts">
          <button
            v-for="prompt in quickPrompts"
            :key="prompt"
            type="button"
            class="mini-ai-prompt"
            @click="applyPrompt(prompt)"
          >
            {{ prompt }}
          </button>
        </div>

        <div v-if="isTyping" class="mini-ai-message-row mini-ai-message-row--assistant">
          <div class="mini-ai-typing">
            <div class="mini-ai-dot"></div>
            <div class="mini-ai-dot"></div>
            <div class="mini-ai-dot"></div>
          </div>
        </div>
      </div>

      <footer class="mini-ai-composer">
        <form @submit.prevent="sendMessage" class="mini-ai-form">
          <input
            v-model="newMessage"
            type="text"
            placeholder="Спроси про меню или заказ..."
            class="mini-ai-input"
          />
          <button type="submit" class="mini-ai-send" :disabled="!newMessage.trim() || isTyping">
            <span>➤</span>
          </button>
        </form>
      </footer>
    </section>
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import api from '@/services/api'

const isTyping = ref(false)
const newMessage = ref('')
const messagesContainer = ref(null)
const quickPrompts = [
  'Посоветуй пиццу',
  'Что есть острое?',
  'Добавь пепперони',
]
const messages = ref([
  { role: 'assistant', content: 'Привет! Я WOKI. Подскажу по меню, помогу выбрать вкус и собрать корзину.' }
])

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const applyPrompt = (prompt) => {
  newMessage.value = prompt
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
      agent_type: 'consultant',
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
.mini-ai-page {
  min-height: calc(100dvh - 9rem);
  padding: 10px 12px 0;
}

.mini-ai-shell {
  height: calc(100dvh - 10rem);
  min-height: 420px;
  max-width: 760px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background:
    radial-gradient(circle at top left, rgba(234, 103, 10, 0.22), transparent 34%),
    linear-gradient(180deg, rgba(31, 41, 55, 0.94), rgba(12, 16, 24, 0.98));
  box-shadow: 0 18px 46px rgba(0, 0, 0, 0.28);
}

.mini-ai-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.mini-ai-avatar {
  width: 46px;
  height: 46px;
  border-radius: 17px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: linear-gradient(135deg, #ea670a, #cc1a1a);
  color: #fff;
  font-size: 15px;
  font-weight: 900;
  box-shadow: 0 12px 28px rgba(234, 103, 10, 0.22);
}

.mini-ai-title {
  color: #fff;
  font-size: 22px;
  line-height: 1.1;
  font-weight: 800;
}

.mini-ai-subtitle {
  margin-top: 3px;
  color: #c7cbd1;
  font-size: 13px;
  line-height: 1.25;
}

.mini-ai-messages {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mini-ai-message-row {
  display: flex;
}

.mini-ai-message-row--user {
  justify-content: flex-end;
}

.mini-ai-message-row--assistant {
  justify-content: flex-start;
}

.mini-ai-bubble {
  max-width: min(86%, 560px);
  padding: 11px 13px;
  border-radius: 19px;
  color: #fff;
  font-size: 14px;
  line-height: 1.42;
  white-space: pre-line;
}

.mini-ai-bubble--assistant {
  border-bottom-left-radius: 6px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.mini-ai-bubble--user {
  border-bottom-right-radius: 6px;
  background: linear-gradient(135deg, #ea670a, #d9480f);
}

.mini-ai-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: 2px;
}

.mini-ai-prompt {
  min-height: 38px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid rgba(234, 103, 10, 0.28);
  background: rgba(234, 103, 10, 0.11);
  color: #ffd7bd;
  font-size: 13px;
  font-weight: 700;
}

.mini-ai-typing {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 12px 14px;
  border-radius: 18px;
  border-bottom-left-radius: 6px;
  background: rgba(255, 255, 255, 0.08);
}

.mini-ai-dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: #fb923c;
  animation: mini-ai-bounce 1s infinite ease-in-out;
}

.mini-ai-dot:nth-child(2) {
  animation-delay: 0.12s;
}

.mini-ai-dot:nth-child(3) {
  animation-delay: 0.24s;
}

.mini-ai-composer {
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(11, 15, 23, 0.92);
}

.mini-ai-form {
  display: flex;
  align-items: center;
  gap: 9px;
}

.mini-ai-input {
  min-width: 0;
  flex: 1;
  height: 48px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.07);
  color: #fff;
  padding: 0 14px;
  outline: none;
  font-size: 15px;
}

.mini-ai-input::placeholder {
  color: #9ca3af;
}

.mini-ai-send {
  width: 48px;
  height: 48px;
  border-radius: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: linear-gradient(135deg, #ea670a, #cc1a1a);
  color: #fff;
  font-weight: 900;
  box-shadow: 0 12px 26px rgba(234, 103, 10, 0.24);
}

.mini-ai-send:disabled {
  opacity: 0.45;
  box-shadow: none;
}

@keyframes mini-ai-bounce {
  0%,
  80%,
  100% {
    transform: translateY(0);
    opacity: 0.55;
  }

  40% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

@media (min-width: 768px) {
  .mini-ai-page {
    padding-top: 18px;
  }

  .mini-ai-shell {
    height: calc(100dvh - 11rem);
  }
}
</style>
