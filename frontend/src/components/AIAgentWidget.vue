<template>
  <div class="ai-agent-widget-root">
    <!-- Floating AI Copilot Trigger Button (Kids Mascot) -->
    <v-btn
      icon
      size="x-large"
      class="floating-agent-btn kids-floating elevation-8"
      style="background: linear-gradient(135deg, #40C4FF 0%, #7C4DFF 100%) !important; border: 3px solid #FFFFFF; box-shadow: 0 8px 24px rgba(124, 77, 255, 0.4) !important;"
      title="Open AI Agent Copilot"
      @click="isOpen = !isOpen"
    >
      <img src="/assets/kids/mascot-buddy-duo.svg" alt="AI Mascot" style="width: 44px; height: 44px; object-fit: contain;" />
    </v-btn>

    <!-- Floating Chat Drawer / Window -->
    <v-card
      v-if="isOpen"
      border
      rounded="xl"
      class="floating-agent-card elevation-16 d-flex flex-column"
      :class="{ 'agent-expanded': isExpanded }"
      @paste="pasteImages"
      @keydown.esc="isExpanded = false"
    >
      <!-- Header (Kids Mascot Theme) -->
      <div class="pa-3 kids-gradient-purple text-white d-flex align-center justify-space-between rounded-t-xl">
        <div class="d-flex align-center ga-2">
          <img src="/assets/kids/mascot-buddy-duo.svg" alt="Mascot" style="width: 38px; height: 38px; object-fit: contain;" class="kids-floating" />
          <div>
            <div class="text-subtitle-2 font-weight-black leading-tight d-flex align-center ga-1">
              <span>FLUENT AI BUDDY</span>
              <span class="kids-pill-badge kids-pill-gold" style="font-size: 9px; padding: 1px 6px;">24/7 AI</span>
            </div>
            <div class="text-caption" style="font-size: 11px; color: #E1BEE7;">
              Your friendly English speaking tutor! ⭐
            </div>
          </div>
        </div>

        <div class="d-flex align-center ga-1">
          <v-btn :icon="isExpanded ? 'mdi-fullscreen-exit' : 'mdi-fullscreen'" variant="text" density="compact" size="small" :title="isExpanded ? 'Restore' : 'Expand'" :aria-label="isExpanded ? 'Restore chat' : 'Expand chat'" @click="isExpanded = !isExpanded" />
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
                :icon="speakingId === idx ? 'mdi-stop' : 'mdi-volume-high'"
                variant="text"
                density="compact"
                size="x-small"
                color="indigo"
                :title="speakingId === idx ? 'Stop Reading' : 'Read Response'"
                :aria-label="speakingId === idx ? 'Stop reading' : 'Read response'"
                :disabled="!speechSupported"
                @click="readMessage(msg, idx)"
              />
            </div>
            <div v-if="msg.files?.length" class="text-caption mb-2">📎 {{ msg.files.join(', ') }}</div>
            <div class="markdown-content"><template v-for="(part, partIndex) in inlineSpeechParts(msg.text, msg.sender === 'agent' && !msg.greeting)" :key="partIndex"><span v-html="formatMarkdown(part.source)"></span><button v-if="part.speech" type="button" class="inline-speech-button" :disabled="!speechSupported" :title="`Listen in English: ${part.speech}`" :aria-label="`Listen in English: ${part.speech}`" @click="playSpeech(part.speech, 'en-US', `${idx}-${partIndex}`)"><v-icon size="16">{{ speakingId === `${idx}-${partIndex}` ? 'mdi-stop' : 'mdi-volume-high' }}</v-icon></button></template></div>
            <v-btn v-if="actionTargets[msg.action]" size="small" color="primary" variant="tonal" class="mt-2 text-none" @click="openAction(msg.action)">{{ actionTargets[msg.action][1] }}</v-btn>
          </div>
        </div>

        <div v-if="isLoading" class="d-flex align-center ga-2 text-caption text-indigo font-weight-bold pa-2">
          <v-progress-circular indeterminate size="18" color="indigo" width="2" />
          <span>AI Assistant is processing...</span>
        </div>
      </div>

      <div v-if="speechError" role="status" class="px-3 py-1 text-caption text-error">{{ speechError }}</div>
      <!-- Input Footer -->
      <div v-if="selectedFiles.length" class="px-3 py-2 border-t">
        <div class="text-caption text-medium-emphasis">Attached to your next message.</div>
        <div v-if="imagePreviews.length" class="d-flex ga-2 my-2">
          <img v-for="image in imagePreviews" :key="image.url" :src="image.url" :alt="image.name" :title="image.name" width="56" height="56" class="rounded border" style="object-fit: cover" />
        </div>
        <div v-for="file in selectedFiles" :key="file.name" class="text-caption text-truncate">📎 {{ file.name }}</div>
        <v-btn size="x-small" variant="text" :disabled="isLoading" @click="confirmRemove = true">Remove Attachments</v-btn>
      </div>
      <div v-if="fileError" class="px-3 py-2 text-caption text-error" role="alert">{{ fileError }}</div>
      <div class="pa-2 bg-white border-t d-flex align-center ga-2">
        <input ref="fileInput" type="file" multiple accept=".png,.jpg,.jpeg,.webp,.pdf,.docx,.txt" hidden @change="selectFiles" />
        <v-menu v-model="attachmentMenuOpen" location="top start" :z-index="10010" :close-on-content-click="false">
          <template #activator="{ props: menuProps }">
            <v-btn v-bind="menuProps" icon="mdi-paperclip" variant="text" size="small" title="Attach Files" aria-label="Attachment options" :disabled="isLoading" />
          </template>
          <template #default>
            <v-card rounded="lg" width="280" class="pa-3">
              <div class="text-subtitle-2 mb-1">Attach Files</div>
              <div class="text-caption text-medium-emphasis">PNG, JPG, WEBP, PDF, DOCX, TXT</div>
              <div class="text-caption text-medium-emphasis mb-3">Up to 3 files · 4 MB each · 8 MB total</div>
              <div class="text-caption text-medium-emphasis mb-3">You can also paste an image into the chat with Ctrl+V.</div>
              <v-btn block color="indigo-darken-3" variant="tonal" prepend-icon="mdi-folder-open-outline" @click="openFilePicker">Select Files</v-btn>
            </v-card>
          </template>
        </v-menu>
        <v-text-field
          v-model="inputMsg"
          :disabled="isLoading"
          maxlength="4000"
          placeholder="Ask AI Assistant (e.g., 'Create assignment', 'Practice weak words')..."
          variant="outlined"
          density="compact"
          hide-details
          class="flex-grow-1"
          @keyup.enter="sendMessage"
        />
        <v-btn
          icon="mdi-send"
          size="small"
          class="kids-btn-3d kids-btn-sky"
          :disabled="(!inputMsg.trim() && !selectedFiles.length) || isLoading"
          @click="sendMessage"
        />
      </div>
    </v-card>
    <v-dialog v-model="confirmRemove" max-width="360">
      <v-card title="Remove Attachments?" text="The selected files will be removed from this draft.">
        <v-card-actions>
          <v-btn @click="confirmRemove = false">Cancel</v-btn>
          <v-btn color="error" @click="selectedFiles = []; confirmRemove = false">Remove</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted, onBeforeUnmount } from 'vue'
import { speechPlan, chooseVoice, inlineSpeechParts } from '../utils/assistantSpeech'
import { clipboardImages, namedClipboardImage } from '../utils/clipboardImages'
import { formatAssistantMarkdown as formatMarkdown } from '../utils/assistantFormatting'
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

const isExpanded = ref(false)
const messagesContainer = ref(null)
const selectedFiles = ref([])
const imagePreviews = ref([])
const releasePreviews = () => imagePreviews.value.forEach(image => URL.revokeObjectURL(image.url))
watch(selectedFiles, files => {
  releasePreviews()
  imagePreviews.value = files.filter(file => file.type.startsWith('image/'))
    .map(file => ({ name: file.name, url: URL.createObjectURL(file) }))
})
onBeforeUnmount(releasePreviews)
const fileInput = ref(null)
const attachmentMenuOpen = ref(false)
const openFilePicker = () => {
  fileInput.value?.click()
  attachmentMenuOpen.value = false
}
const fileError = ref('')
const confirmRemove = ref(false)
const selectFiles = (event) => {
  addFiles(Array.from(event.target.files || []))
  event.target.value = ''
}
const addFiles = (incoming) => {
  if (isLoading.value) return
  const files = [...selectedFiles.value, ...incoming]
  if (files.length > 3 || files.some(f => !f.size || f.size > 4 * 1024 * 1024) || files.reduce((sum, f) => sum + f.size, 0) > 8 * 1024 * 1024) {
    fileError.value = 'Select up to 3 nonempty files: 4 MB per file, 8 MB in total.'
    return
  }
  if (files.some(f => !/\.(png|jpe?g|webp|pdf|docx|txt)$/i.test(f.name))) {
    fileError.value = 'Unsupported file format.'
    return
  }
  selectedFiles.value = files
  fileError.value = ''
}
const pasteImages = (event) => {
  const images = clipboardImages(event.clipboardData)
  if (!images.length) return // Keep normal text paste behavior.
  event.preventDefault()
  if (isLoading.value) return
  const files = images.map(namedClipboardImage)
  if (files.some(file => !file)) {
    fileError.value = 'Paste a PNG, JPG, or WEBP image. Other image formats are not supported.'
    return
  }
  addFiles(files)
}
const encodeFile = (file) => new Promise((resolve, reject) => {
  const reader = new FileReader()
  reader.onload = () => resolve({ name: file.name, data: String(reader.result).split(',')[1] })
  reader.onerror = () => reject(new Error('Unable to read attachment.'))
  reader.readAsDataURL(file)
})
const isOpen = ref(false)
const isLoading = ref(false)
const inputMsg = ref('')

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
    greeting: true,
    text: '👋 **Chào bạn! Mình là FLUENT AI ASSISTANT.**\n\nMình có thể giải thích cách phát âm, tra bài chưa nộp và xem điểm theo tài khoản đăng nhập. Với giáo viên, mình hỗ trợ tìm lớp và mở luồng soạn bài; bài chỉ được giao khi Thầy/Cô kiểm tra và bấm Assign Homework.'
  }
])

watch(() => [props.userId, props.userRole], () => {
  messages.value = [{ sender: 'agent', text: 'Tài khoản hoặc vai trò đã thay đổi. Mình sẽ bắt đầu cuộc trò chuyện mới để tránh nhầm dữ liệu.' }]
  inputMsg.value = ''
  selectedFiles.value = []
  fileError.value = ''
})

watch(messages, () => {
  scrollToBottom()
}, { deep: true })

const sendQuickPrompt = (promptText) => {
  inputMsg.value = promptText
  sendMessage()
}

const sendMessage = async () => {
  const text = inputMsg.value.trim() || (selectedFiles.value.length ? 'Hãy đọc và giải thích nội dung các file đính kèm.' : '')
  if (!text || isLoading.value) return

  const token = ['teacher', 'admin', 'super_admin'].includes(props.userRole)
    ? (localStorage.getItem('teacher_auth_token') || localStorage.getItem('admin_auth_token') || localStorage.getItem('token'))
    : localStorage.getItem('token')
  if (!token) {
    messages.value.push({ sender: 'agent', text: 'Bạn cần đăng nhập để dùng trợ lý và tra dữ liệu đúng tài khoản.' })
    return
  }
  const history = messages.value.slice(-8).map(m => ({ role: m.sender === 'user' ? 'user' : 'assistant', content: m.text }))
  const files = [...selectedFiles.value]
  const accountId = props.userId
  const accountRole = props.userRole
  messages.value.push({ sender: 'user', text, files: files.map(f => f.name) })
  inputMsg.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const attachments = await Promise.all(files.map(encodeFile))
    const res = await fetch(`${props.backendUrl}/api/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        user_id: props.userId || 1,
        role: props.userRole || 'student',
        message: text,
        conversation_history: history,
        attachments
      })
    })

    if (accountId !== props.userId || accountRole !== props.userRole) return
    if (res.ok) {
      const data = await res.json()
      if (accountId !== props.userId || accountRole !== props.userRole) return
      if (data.status === 'success') {
        selectedFiles.value = []
        fileError.value = ''
      } else {
        inputMsg.value = text
      }
      messages.value.push({ sender: 'agent', text: data.reply || 'Chưa nhận được câu trả lời. Vui lòng thử lại.', action: data.action })
    } else {
      const error = await res.json().catch(() => ({}))
      inputMsg.value = text
      messages.value.push({ sender: 'agent', text: res.status === 401 ? 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.' : (error.detail || 'Không thể xử lý yêu cầu lúc này. Vui lòng thử lại.') })
    }
  } catch (e) {
    if (accountId !== props.userId || accountRole !== props.userRole) return
    inputMsg.value = text
    messages.value.push({ sender: 'agent', text: 'Không kết nối được với trợ lý. Tin nhắn chưa được xử lý; vui lòng thử lại.' })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const speechSupported = typeof window !== 'undefined' && 'speechSynthesis' in window
const speakingId = ref(null)
const speechError = ref('')
let voices = []
let speechGeneration = 0
let activeUtterance = null
const refreshVoices = () => { if (speechSupported) voices = window.speechSynthesis.getVoices() }
const stopSpeech = () => {
  speechGeneration += 1
  if (speechSupported) window.speechSynthesis.cancel()
  activeUtterance = null
  speakingId.value = null
}
const playSpeech = (text, language, id) => {
  const wasSpeaking = speakingId.value === id
  stopSpeech()
  speechError.value = ''
  if (wasSpeaking || !text) return
  if (!speechSupported) { speechError.value = 'Speech playback is unavailable in this browser.'; return }
  refreshVoices()
  const voice = chooseVoice(voices, language)
  if (!voice) {
    speechError.value = `No ${language.startsWith('en') ? 'English' : 'Vietnamese'} voice is available. Enable this language in your device speech settings and try again.`
    return
  }
  const generation = speechGeneration
  const utterance = new SpeechSynthesisUtterance(text)
  activeUtterance = utterance
  utterance.lang = language
  utterance.voice = voice
  utterance.rate = language.startsWith('en') ? 0.9 : 1
  utterance.onend = () => { if (generation === speechGeneration) { speakingId.value = null; activeUtterance = null } }
  utterance.onerror = () => {
    if (generation !== speechGeneration) return
    speakingId.value = null
    activeUtterance = null
    speechError.value = 'Speech playback failed. Please try again.'
  }
  speakingId.value = id
  window.speechSynthesis.speak(activeUtterance)
}
const readMessage = (message, id) => {
  const plan = speechPlan(message.text, message.greeting)
  playSpeech(plan.text, plan.language, id)
}
onMounted(() => {
  refreshVoices()
  if (speechSupported) window.speechSynthesis.addEventListener('voiceschanged', refreshVoices)
})
onBeforeUnmount(() => {
  stopSpeech()
  if (speechSupported) window.speechSynthesis.removeEventListener('voiceschanged', refreshVoices)
})
watch(isOpen, open => {
  if (!open) {
    stopSpeech()
    attachmentMenuOpen.value = false
  }
})
watch(() => [props.userId, props.userRole], stopSpeech)

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

<style scoped>
.floating-agent-card.agent-expanded {
  inset: 12px;
  width: auto;
  height: auto;
  max-width: none;
  max-height: none;
}
.agent-messages-container { min-height: 0; }
.floating-agent-card > :not(.agent-messages-container) { flex-shrink: 0; }
@media (max-width: 600px) {
  .floating-agent-card { right: 12px; bottom: 88px; width: calc(100vw - 24px); }
  .floating-agent-card.agent-expanded { inset: 0; border-radius: 0 !important; height: 100dvh; }
}
</style>

<style scoped>
.inline-speech-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  vertical-align: middle;
  width: 28px;
  height: 28px;
  margin-inline: 3px;
  border-radius: 50%;
  color: rgb(var(--v-theme-primary));
  cursor: pointer;
}
.inline-speech-button:hover { background: rgba(var(--v-theme-primary), 0.12); }
.inline-speech-button:focus-visible { outline: 2px solid currentColor; outline-offset: 2px; }
.inline-speech-button:disabled { opacity: 0.4; cursor: default; }
</style>
