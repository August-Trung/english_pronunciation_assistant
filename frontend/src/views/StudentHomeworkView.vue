<template>
  <v-container fluid class="pa-4 pa-md-6" style="max-width: 900px;">
    <!-- Homework Banner -->
    <v-card border flat class="pa-4 mb-4 bg-gradient-purple text-white rounded-lg elevation-1">
      <div class="d-flex align-center justify-space-between flex-wrap ga-3">
        <div class="d-flex align-center ga-3">
          <v-avatar color="white" size="48" class="elevation-1">
            <v-icon color="purple-darken-3" size="large">mdi-clipboard-text-outline</v-icon>
          </v-avatar>
          <div>
            <div class="text-h6 font-weight-black tracking-tight">BÀI TẬP VỀ NHÀ ĐƯỢC GIAO</div>
            <div class="text-caption opacity-90 font-weight-medium">
              Hoàn thành các bài luyện phát âm do Giáo viên Lớp 5A giao để tích lũy điểm số
            </div>
          </div>
        </div>

        <v-btn
          color="white"
          variant="flat"
          class="font-weight-black text-purple-darken-3 text-none"
          prepend-icon="mdi-key-variant"
          @click="showJoinClassModal = true"
        >
          Nhập Mã Vào Lớp Mới
        </v-btn>
      </div>
    </v-card>

    <!-- Assignments List -->
    <div class="d-flex flex-column ga-3">
      <v-card
        v-for="asg in assignments"
        :key="asg.assignment_id"
        border
        flat
        class="pa-4 bg-white rounded-lg"
      >
        <div class="d-flex align-center justify-space-between flex-wrap ga-2 mb-2">
          <div>
            <div class="d-flex align-center ga-2">
              <span class="text-subtitle-1 font-weight-black text-primary">{{ asg.title }}</span>
              <v-chip color="indigo" size="x-small" variant="flat" class="font-weight-bold">
                {{ asg.class_name }}
              </v-chip>
            </div>
            <div class="text-caption text-grey">Hạn nộp: {{ asg.due_date || 'Không có hạn' }}</div>
          </div>

          <v-chip
            :color="asg.is_submitted ? 'success' : 'warning'"
            variant="flat"
            size="small"
            class="font-weight-black"
          >
            {{ asg.is_submitted ? `Đã Nộp (${asg.score?.toFixed(1)}/10)` : 'Chưa Nộp' }}
          </v-chip>
        </div>

        <!-- Target Sentence Card -->
        <div class="pa-3 bg-purple-lighten-5 rounded border border-purple mb-3">
          <div class="text-caption font-weight-bold text-purple-darken-3 mb-1">Mẫu Bài Đọc Cần Thu Âm:</div>
          <div class="text-body-1 font-weight-black text-secondary">"{{ asg.topic_sentence }}"</div>
        </div>

        <!-- Submission Controls or Result -->
        <div v-if="!asg.is_submitted" class="d-flex align-center ga-2">
          <v-btn
            :color="isRecording ? 'error' : 'primary'"
            variant="flat"
            class="font-weight-black text-none"
            :prepend-icon="isRecording ? 'mdi-stop' : 'mdi-microphone'"
            @click="toggleRecording(asg)"
          >
            {{ isRecording ? 'Dừng & Nộp Bài' : 'Bắt Đầu Ghi Âm Bài Đọc' }}
          </v-btn>
          <span v-if="isRecording" class="text-caption text-error font-weight-bold animate-pulse">
            🔴 Đang ghi âm bài nộp...
          </span>
        </div>

        <div v-else class="bg-grey-lighten-5 pa-3 rounded border">
          <div class="text-caption font-weight-bold text-grey-darken-3 mb-1">Âm thanh đã nộp lên Supabase Storage:</div>
          <div v-if="asg.audio_url" class="d-flex align-center ga-2 mb-2">
            <audio controls :src="asg.audio_url" class="w-100" style="height: 32px;" />
          </div>
          <div v-if="asg.teacher_feedback" class="text-caption text-indigo font-weight-bold">
            Lời nhận xét của Giáo viên: {{ asg.teacher_feedback }}
          </div>
        </div>
      </v-card>

      <div v-if="!assignments.length" class="text-center pa-8 bg-white border rounded-lg">
        <v-icon size="48" color="grey-lighten-1">mdi-clipboard-check-outline</v-icon>
        <div class="text-subtitle-2 font-weight-bold text-grey mt-2">
          Bạn chưa gia nhập lớp học nào hoặc chưa có bài tập mới.
        </div>
        <v-btn
          color="primary"
          variant="tonal"
          class="mt-3 text-none font-weight-bold"
          prepend-icon="mdi-key-variant"
          @click="showJoinClassModal = true"
        >
          Nhập Mã Vào Lớp (Ví dụ: CLS-5A-89)
        </v-btn>
      </div>
    </div>

    <!-- Modal: Join Class Dialog -->
    <v-dialog v-model="showJoinClassModal" max-width="450">
      <v-card border rounded="lg" class="pa-4">
        <div class="text-subtitle-1 font-weight-black text-primary mb-2 d-flex align-center ga-2">
          <v-icon color="primary">mdi-key-variant</v-icon>
          <span>Gia Nhập Lớp Học Mới</span>
        </div>

        <v-text-field
          v-model="joinCodeInput"
          label="Mã Vào Lớp (6 Ký tự từ Giáo viên):"
          placeholder="Ví dụ: CLS-524-89"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          prepend-inner-icon="mdi-google-classroom"
        />

        <v-card-actions class="px-0 pb-0">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showJoinClassModal = false">Hủy</v-btn>
          <v-btn color="primary" variant="flat" class="text-none font-weight-bold" :loading="isJoining" @click="submitJoinClass">
            Gia Nhập Lớp
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  backendUrl: String,
  userId: Number
})

const assignments = ref([])
const showJoinClassModal = ref(false)
const joinCodeInput = ref('')
const isJoining = ref(false)

const isRecording = ref(false)
let mediaRecorder = null
let audioChunks = []

const fetchStudentAssignments = async () => {
  try {
    const res = await fetch(`${props.backendUrl}/api/assignments/student/${props.userId || 1}`)
    if (res.ok) {
      const data = await res.json()
      assignments.value = data.assignments || []
    }
  } catch (e) {
    console.error('Fetch student assignments error:', e)
  }
}

const submitJoinClass = async () => {
  if (!joinCodeInput.value.trim()) return
  isJoining.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: props.userId || 1,
        join_code: joinCodeInput.value.trim()
      })
    })
    if (res.ok) {
      const data = await res.json()
      alert(`Thành công! Bạn đã gia nhập ${data.class_name}`)
      showJoinClassModal.value = false
      joinCodeInput.value = ''
      await fetchStudentAssignments()
    } else {
      const err = await res.json()
      alert(err.detail || 'Mã lớp không hợp lệ.')
    }
  } catch (e) {
    alert('Lỗi gia nhập lớp: ' + e.message)
  } finally {
    isJoining.value = false
  }
}

const toggleRecording = async (asg) => {
  if (!isRecording.value) {
    // Start recording
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorder = new MediaRecorder(stream)
      audioChunks = []
      mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data)
      mediaRecorder.onstop = () => uploadSubmission(asg)
      mediaRecorder.start()
      isRecording.value = true
    } catch (e) {
      alert('Không thể mở micro: ' + e.message)
    }
  } else {
    // Stop recording and upload
    if (mediaRecorder) {
      mediaRecorder.stop()
      isRecording.value = false
    }
  }
}

const uploadSubmission = async (asg) => {
  const blob = new Blob(audioChunks, { type: 'audio/webm' })
  const formData = new FormData()
  formData.append('assignment_id', asg.assignment_id)
  formData.append('student_id', props.userId || 1)
  formData.append('student_name', 'Học sinh')
  formData.append('audio', blob, 'submission.webm')

  try {
    const res = await fetch(`${props.backendUrl}/api/assignments/submit`, {
      method: 'POST',
      body: formData
    })
    if (res.ok) {
      alert('Nộp bài thành công! File âm thanh đã lưu lên Supabase Storage.')
      await fetchStudentAssignments()
    }
  } catch (e) {
    alert('Lỗi nộp bài: ' + e.message)
  }
}

onMounted(() => {
  fetchStudentAssignments()
})
</script>

<style scoped>
.bg-gradient-purple {
  background: linear-gradient(135deg, #7b1fa2 0%, #4a148c 100%);
}
</style>
