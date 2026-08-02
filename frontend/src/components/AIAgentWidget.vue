<template>
  <div class="ai-agent-widget-root">
    <!-- Floating AI Copilot Trigger Button -->
    <v-btn
      color="indigo-darken-3"
      icon
      size="large"
      class="floating-agent-btn elevation-6"
      title="Open AI Agent Copilot"
      @click="isOpen = !isOpen"
    >
      <v-avatar size="36" color="amber-lighten-4">
        <v-icon color="indigo-darken-3" size="default">mdi-robot-excited</v-icon>
      </v-avatar>
    </v-btn>

    <!-- Floating Chat Drawer / Window -->
    <v-card
      v-if="isOpen"
      border
      rounded="xl"
      class="floating-agent-card elevation-16 d-flex flex-column"
    >
      <!-- Header -->
      <div class="pa-3 bg-gradient-indigo text-white d-flex align-center justify-space-between rounded-t-xl">
        <div class="d-flex align-center ga-2">
          <v-avatar color="amber" size="32" class="elevation-1">
            <v-icon color="indigo-darken-4" size="small">mdi-robot</v-icon>
          </v-avatar>
          <div>
            <div class="text-subtitle-2 font-weight-black leading-tight">FLUENT AI ASSISTANT</div>
            <div class="text-caption text-indigo-lighten-4" style="font-size: 11px;">
              Trợ lý Luyện âm & Học tập 24/7
            </div>
          </div>
        </div>

        <div class="d-flex align-center ga-1">
          <v-btn
            icon="mdi-minus"
            variant="text"
            density="compact"
            color="white"
            size="small"
            @click="isOpen = false"
          />
        </div>
      </div>

      <!-- Quick Role Suggestion Chips -->
      <div class="px-3 py-2 bg-grey-lighten-4 border-b d-flex align-center ga-1 overflow-x-auto">
        <template v-if="userRole === 'teacher' || userRole === 'admin' || userRole === 'super_admin'">
          <v-chip
            size="x-small"
            color="indigo-darken-3"
            variant="tonal"
            class="font-weight-bold cursor-pointer flex-shrink-0"
            prepend-icon="mdi-plus-box"
            @click="sendQuickPrompt('Tạo bài tập 3 câu chủ đề Environment cho lớp')"
          >
            Tạo bài tập AI
          </v-chip>
          <v-chip
            size="x-small"
            color="indigo-darken-3"
            variant="tonal"
            class="font-weight-bold cursor-pointer flex-shrink-0"
            prepend-icon="mdi-chart-box"
            @click="sendQuickPrompt('Thống kê danh sách học sinh điểm thấp')"
          >
            Thống kê điểm
          </v-chip>
        </template>
        <template v-else>
          <v-chip
            size="x-small"
            color="deep-orange"
            variant="tonal"
            class="font-weight-bold cursor-pointer flex-shrink-0"
            prepend-icon="mdi-flash"
            @click="sendQuickPrompt('Tự động tạo bài tập luyện các từ mình hay đọc sai')"
          >
            Tạo bài luyện từ yếu
          </v-chip>
          <v-chip
            size="x-small"
            color="indigo"
            variant="tonal"
            class="font-weight-bold cursor-pointer flex-shrink-0"
            prepend-icon="mdi-clock-alert-outline"
            @click="sendQuickPrompt('Kiểm tra danh sách bài tập lớp học sắp hết hạn')"
          >
            Bài tập cần làm
          </v-chip>
          <v-chip
            size="x-small"
            color="purple"
            variant="tonal"
            class="font-weight-bold cursor-pointer flex-shrink-0"
            prepend-icon="mdi-forum"
            @click="sendQuickPrompt('Đóng vai đối thoại giao tiếp tiếng Anh với mình')"
          >
            Luyện đối thoại
          </v-chip>
        </template>
      </div>

      <!-- Messages Body -->
      <div class="agent-messages-container pa-3 flex-grow-1 overflow-y-auto">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="mb-3 d-flex flex-column"
          :class="msg.sender === 'user' ? 'align-end' : 'align-start'"
        >
          <div
            class="pa-3 rounded-lg text-body-2"
            :class="msg.sender === 'user' ? 'bg-indigo text-white rounded-br-0' : 'bg-grey-lighten-4 text-grey-darken-4 border rounded-bl-0'"
            style="max-width: 88%; word-break: break-word; white-space: pre-line;"
          >
            <div class="d-flex align-center justify-space-between ga-2 mb-1" v-if="msg.sender === 'agent'">
              <span class="text-caption font-weight-black text-indigo-darken-3">AI COPILOT</span>
              <v-btn
                icon="mdi-volume-high"
                variant="text"
                density="compact"
                size="x-small"
                color="indigo"
                title="Listen AI voice"
                @click="playSpeech(msg.text)"
              />
            </div>
            <span>{{ msg.text }}</span>
          </div>
        </div>

        <div v-if="isLoading" class="d-flex align-center ga-2 text-caption text-indigo font-weight-bold pa-2">
          <v-progress-circular indeterminate size="18" color="indigo" width="2" />
          <span>Trợ lý AI đang xử lý...</span>
        </div>
      </div>

      <!-- Input Footer -->
      <div class="pa-2 bg-white border-t d-flex align-center ga-2">
        <v-text-field
          v-model="inputMsg"
          placeholder="Nhập yêu cầu (ví dụ: 'Tạo bài tập', 'Luyện từ sai')..."
          variant="outlined"
          density="compact"
          hide-details
          class="flex-grow-1"
          @keyup.enter="sendMessage"
        />
        <v-btn
          color="indigo-darken-3"
          icon="mdi-send"
          size="small"
          variant="flat"
          :disabled="!inputMsg.trim() || isLoading"
          @click="sendMessage"
        />
      </div>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  backendUrl: {
    type: String,
    required: true
  },
  userRole: {
    type: String,
    default: 'student'
  },
  userId: {
    type: Number,
    default: 1
  }
})

const isOpen = ref(false)
const isLoading = ref(false)
const inputMsg = ref('')

const messages = ref([
  {
    sender: 'agent',
    text: '👋 **Chào bạn! Mình là Trợ lý AI Fluent.**\n\nBạn có thể ra lệnh hoặc hỏi mình bất cứ điều gì (ví dụ: *Tạo bài tập AI*, *Thống kê điểm*, *Luyện từ đọc sai*).'
  }
])

const sendQuickPrompt = (promptText) => {
  inputMsg.value = promptText
  sendMessage()
}

const sendMessage = async () => {
  const text = inputMsg.value.trim()
  if (!text || isLoading.value) return

  messages.value.push({ sender: 'user', text })
  inputMsg.value = ''
  isLoading.value = true

  try {
    const res = await fetch(`${props.backendUrl}/api/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: props.userId || 1,
        role: props.userRole || 'student',
        message: text,
        conversation_history: messages.value.slice(-6).map(m => ({
          role: m.sender === 'user' ? 'user' : 'assistant',
          content: m.text
        }))
      })
    })

    if (res.ok) {
      const data = await res.json()
      messages.value.push({ sender: 'agent', text: data.reply || 'AI Agent response received.' })
    } else {
      messages.value.push({ sender: 'agent', text: '⚠️ AI Copilot error processing message.' })
    }
  } catch (e) {
    messages.value.push({ sender: 'agent', text: '⚠️ Connection error to AI Agent service.' })
  } finally {
    isLoading.value = false
  }
}

const playSpeech = (text) => {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel()
    const cleanText = text.replace(/[*#_~`]/g, '')
    const utterance = new SpeechSynthesisUtterance(cleanText)
    utterance.lang = 'vi-VN'
    window.speechSynthesis.speak(utterance)
  }
}
</script>

<style scoped>
.ai-agent-widget-root {
  position: relative;
  z-index: 9999;
}

.floating-agent-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  border: 2px solid #FFD54F;
  box-shadow: 0 0 15px rgba(63, 81, 181, 0.5);
  animation: pulse-glow 2.5s infinite;
}

@keyframes pulse-glow {
  0% {
    box-shadow: 0 0 0 0 rgba(63, 81, 181, 0.7);
  }
  70% {
    box-shadow: 0 0 0 14px rgba(63, 81, 181, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(63, 81, 181, 0);
  }
}

.floating-agent-card {
  position: fixed;
  bottom: 84px;
  right: 24px;
  width: 380px;
  height: 480px;
  max-width: calc(100vw - 32px);
  max-height: calc(100vh - 120px);
  z-index: 10000;
  background-color: #ffffff;
}

.bg-gradient-indigo {
  background: linear-gradient(135deg, #1A237E 0%, #3F51B5 100%);
}

.agent-messages-container {
  background-color: #FAFAFA;
}
</style>
