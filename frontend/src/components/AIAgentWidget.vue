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
              24/7 Smart Pronunciation & Learning Tutor
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
            color="indigo"
            variant="tonal"
            class="font-weight-bold cursor-pointer flex-shrink-0"
            prepend-icon="mdi-plus-box"
            @click="sendQuickPrompt('Tôi muốn tạo bài tập cho lớp của tôi')"
          >
            Create Assignment
          </v-chip>
          <v-chip
            size="x-small"
            color="indigo"
            variant="tonal"
            class="font-weight-bold cursor-pointer flex-shrink-0"
            prepend-icon="mdi-chart-bar"
            @click="sendQuickPrompt('Xem bảng điểm lớp của tôi')"
          >
            Class Gradebook
          </v-chip>
        </template>
        <template v-else>
          <v-chip
            size="x-small"
            color="indigo"
            variant="tonal"
            class="font-weight-bold cursor-pointer flex-shrink-0"
            prepend-icon="mdi-account-voice"
            @click="sendQuickPrompt('Tôi muốn luyện tập phát âm âm /θ/ trong tiếng Anh')"
          >
            Practice /θ/
          </v-chip>
          <v-chip
            size="x-small"
            color="indigo"
            variant="tonal"
            class="font-weight-bold cursor-pointer flex-shrink-0"
            prepend-icon="mdi-flash"
            @click="sendQuickPrompt('Tự động tạo bài tập luyện các từ mình hay đọc sai')"
          >
            Practice Weak Words
          </v-chip>
          <v-chip
            size="x-small"
            color="indigo"
            variant="tonal"
            class="font-weight-bold cursor-pointer flex-shrink-0"
            prepend-icon="mdi-clock-alert-outline"
            @click="sendQuickPrompt('Kiểm tra bài tập lớp học cần nộp')"
          >
            Pending Homework
          </v-chip>
          <v-chip
            size="x-small"
            color="purple"
            variant="tonal"
            class="font-weight-bold cursor-pointer flex-shrink-0"
            prepend-icon="mdi-forum"
            @click="sendQuickPrompt('Start interactive hotel receptionist speaking roleplay')"
          >
            Voice Roleplay
          </v-chip>
        </template>
      </div>

      <!-- Messages Body -->
      <div ref="messagesContainer" class="agent-messages-container pa-3 flex-grow-1 overflow-y-auto">
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
              <span class="text-caption font-weight-black text-indigo-darken-3">FLUENT AI ASSISTANT</span>
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
            <div class="markdown-content" v-html="formatMarkdown(msg.text)"></div>
            <v-btn v-if="actionTargets[msg.action]" size="small" color="primary" variant="tonal" class="mt-2 text-none" @click="openAction(msg.action)">{{ actionTargets[msg.action][1] }}</v-btn>
          </div>
        </div>

        <div v-if="isLoading" class="d-flex align-center ga-2 text-caption text-indigo font-weight-bold pa-2">
          <v-progress-circular indeterminate size="18" color="indigo" width="2" />
          <span>AI Assistant is processing...</span>
        </div>
      </div>

      <!-- Input Footer -->
      <div class="pa-2 bg-white border-t d-flex align-center ga-2">
        <v-text-field
          v-model="inputMsg"
          placeholder="Ask AI Assistant (e.g., 'Create assignment', 'Practice weak words')..."
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
import { ref, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const actionTargets = { open_teacher: ['/teacher', 'Open Teacher Hub'], open_homework: ['/homework', 'Open Homework'], open_speaking: ['/', 'Open Speaking'] }
const openAction = (action) => {
  const target = actionTargets[action]
  if (target) { router.push(target[0]); isOpen.value = false }
}

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
const formatMarkdown = (text) => {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const messages = ref([
  {
    sender: 'agent',
    text: '👋 **Chào bạn! Mình là FLUENT AI ASSISTANT.**\n\nMình có thể giải thích cách phát âm, tra bài chưa nộp và xem điểm theo tài khoản đăng nhập. Với giáo viên, mình hỗ trợ tìm lớp và mở luồng soạn bài; bài chỉ được giao khi Thầy/Cô kiểm tra và bấm Assign Homework.'
  }
])

watch(() => [props.userId, props.userRole], () => {
  messages.value = [{ sender: 'agent', text: 'Tài khoản hoặc vai trò đã thay đổi. Mình sẽ bắt đầu cuộc trò chuyện mới để tránh nhầm dữ liệu.' }]
  inputMsg.value = ''
})

watch(messages, () => {
  scrollToBottom()
}, { deep: true })

const sendQuickPrompt = (promptText) => {
  inputMsg.value = promptText
  sendMessage()
}

const sendMessage = async () => {
  const text = inputMsg.value.trim()
  if (!text || isLoading.value) return

  const token = ['teacher', 'admin', 'super_admin'].includes(props.userRole)
    ? (localStorage.getItem('teacher_auth_token') || localStorage.getItem('admin_auth_token') || localStorage.getItem('token'))
    : localStorage.getItem('token')
  if (!token) {
    messages.value.push({ sender: 'agent', text: 'Bạn cần đăng nhập để dùng trợ lý và tra dữ liệu đúng tài khoản.' })
    return
  }
  const history = messages.value.slice(-8).map(m => ({ role: m.sender === 'user' ? 'user' : 'assistant', content: m.text }))
  messages.value.push({ sender: 'user', text })
  inputMsg.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const res = await fetch(`${props.backendUrl}/api/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        user_id: props.userId || 1,
        role: props.userRole || 'student',
        message: text,
        conversation_history: history
      })
    })

    if (res.ok) {
      const data = await res.json()
      messages.value.push({ sender: 'agent', text: data.reply || 'Chưa nhận được câu trả lời. Vui lòng thử lại.', action: data.action })
    } else {
      const error = await res.json().catch(() => ({}))
      messages.value.push({ sender: 'agent', text: res.status === 401 ? 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.' : (error.detail || 'Không thể xử lý yêu cầu lúc này. Vui lòng thử lại.') })
    }
  } catch (e) {
    messages.value.push({ sender: 'agent', text: 'Không kết nối được với trợ lý. Tin nhắn chưa được xử lý; vui lòng thử lại.' })
  } finally {
    isLoading.value = false
    scrollToBottom()
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
