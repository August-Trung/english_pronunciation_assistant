<template>
  <v-container fluid class="pa-4 pa-md-6" style="max-width: 900px;">
    <!-- Vuetify Toast Notification -->
    <v-snackbar
      v-model="toast.show"
      :color="toast.color"
      location="top"
      timeout="4000"
      rounded="lg"
      elevation="4"
    >
      <div class="d-flex align-center ga-2 text-subtitle-2 font-weight-bold text-white">
        <v-icon>{{ toast.icon }}</v-icon>
        <span>{{ toast.text }}</span>
      </div>
    </v-snackbar>

    <!-- Homework Banner -->
    <v-card border flat class="pa-4 mb-4 bg-gradient-purple text-white rounded-lg elevation-1">
      <div class="d-flex align-center justify-space-between flex-wrap ga-3">
        <div class="d-flex align-center ga-3">
          <v-avatar color="white" size="48" class="elevation-1">
            <v-icon color="purple-darken-3" size="large">mdi-clipboard-text-outline</v-icon>
          </v-avatar>
          <div>
            <div class="text-h6 font-weight-black tracking-tight">CLASSROOM ASSIGNED HOMEWORK</div>
            <div class="text-caption opacity-90 font-weight-medium">
              Complete pronunciation reading exercises assigned by your teacher
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
          Enter Class Join Code
        </v-btn>
      </div>
    </v-card>

    <!-- Enrolled Classes Roster Bar & Leave Class Action -->
    <v-card v-if="enrolledClasses.length" border flat class="pa-3 mb-4 bg-white rounded-lg">
      <div class="text-caption font-weight-black text-secondary mb-2 d-flex align-center justify-space-between">
        <span>MY ENROLLED CLASSROOMS ({{ enrolledClasses.length }})</span>
        <span class="text-grey font-weight-regular">Click badge to view options</span>
      </div>
      <div class="d-flex align-center flex-wrap ga-2">
        <v-chip
          v-for="cls in enrolledClasses"
          :key="cls.class_id"
          color="indigo"
          variant="tonal"
          size="medium"
          class="font-weight-bold"
          prepend-icon="mdi-google-classroom"
        >
          {{ cls.class_name }} ({{ cls.join_code || 'Enrolled' }})
          <template #append>
            <v-btn
              icon="mdi-exit-to-app"
              variant="text"
              size="x-small"
              color="error"
              class="ml-1"
              title="Leave Class"
              @click.stop="openLeaveClassModal(cls)"
            />
          </template>
        </v-chip>
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
            <div class="text-caption text-grey">Due Date: {{ asg.due_date || 'No Deadline' }}</div>
          </div>

          <v-chip
            :color="asg.is_submitted ? 'success' : 'warning'"
            variant="flat"
            size="small"
            class="font-weight-black"
          >
            {{ asg.is_submitted ? `Submitted (${asg.score?.toFixed(1)}/10)` : 'Pending' }}
          </v-chip>
        </div>

        <!-- Target Sentence Card -->
        <div class="pa-3 bg-purple-lighten-5 rounded border border-purple mb-3">
          <div class="text-caption font-weight-bold text-purple-darken-3 mb-1">Assigned Model Reading Sentence:</div>
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
            {{ isRecording ? 'Stop & Submit Recording' : 'Start Voice Recording' }}
          </v-btn>
          <span v-if="isRecording" class="text-caption text-error font-weight-bold animate-pulse">
            🔴 Recording voice submission...
          </span>
        </div>

        <div v-else class="bg-grey-lighten-5 pa-3 rounded border">
          <div class="text-caption font-weight-bold text-grey-darken-3 mb-1">Submitted Audio on Supabase Storage:</div>
          <div v-if="asg.audio_url" class="d-flex align-center ga-2 mb-2">
            <audio controls :src="asg.audio_url" class="w-100" style="height: 32px;" />
          </div>
          <div v-if="asg.teacher_feedback" class="text-caption text-indigo font-weight-bold">
            Teacher Feedback: {{ asg.teacher_feedback }}
          </div>
        </div>
      </v-card>

      <div v-if="!assignments.length" class="text-center pa-8 bg-white border rounded-lg">
        <v-icon size="48" color="grey-lighten-1">mdi-clipboard-check-outline</v-icon>
        <div class="text-subtitle-2 font-weight-bold text-grey mt-2">
          You are not enrolled in any class yet or have no assigned homework.
        </div>
        <v-btn
          color="primary"
          variant="tonal"
          class="mt-3 text-none font-weight-bold"
          prepend-icon="mdi-key-variant"
          @click="showJoinClassModal = true"
        >
          Enter Join Code (Example: CLS-524-89)
        </v-btn>
      </div>
    </div>

    <!-- Modal 1: Join Class Dialog -->
    <v-dialog v-model="showJoinClassModal" max-width="450">
      <v-card border rounded="lg" class="pa-4">
        <div class="text-subtitle-1 font-weight-black text-primary mb-2 d-flex align-center ga-2">
          <v-icon color="primary">mdi-key-variant</v-icon>
          <span>Join New Classroom</span>
        </div>

        <v-text-field
          v-model="joinCodeInput"
          label="6-Digit Join Code:"
          placeholder="Example: CLS-524-89"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          prepend-inner-icon="mdi-google-classroom"
        />

        <v-card-actions class="px-0 pb-0">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showJoinClassModal = false">Cancel</v-btn>
          <v-btn color="primary" variant="flat" class="text-none font-weight-bold" :loading="isJoining" @click="submitJoinClass">
            Join Class
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Modal 2: Git-Style Safety Confirmation for Leaving Classroom -->
    <v-dialog v-model="showLeaveModal" max-width="480">
      <v-card v-if="targetLeaveClass" border rounded="lg" class="pa-5 bg-white">
        <div class="text-subtitle-1 font-weight-black text-error mb-2 d-flex align-center ga-2 border-b pb-2">
          <v-icon color="error">mdi-shield-alert-outline</v-icon>
          <span>SAFE UNENROLLMENT CONFIRMATION</span>
        </div>

        <div class="text-body-2 font-weight-bold text-grey-darken-3 mb-2">
          You are about to leave <strong>{{ targetLeaveClass.class_name }}</strong>.
        </div>

        <div class="bg-red-lighten-5 pa-3 rounded border border-red text-caption text-red-darken-4 font-weight-bold mb-3">
          To prevent accidental unenrollment, please type the exact Join Code of this class below:
          <div class="text-subtitle-2 font-weight-mono font-weight-black mt-1 text-center bg-white py-1 rounded border">
            {{ targetLeaveClass.join_code }}
          </div>
        </div>

        <v-text-field
          v-model="leaveInput"
          label="Type Join Code to confirm:"
          :placeholder="targetLeaveClass.join_code"
          variant="outlined"
          density="comfortable"
          class="mb-2"
          prepend-inner-icon="mdi-shield-check"
          hide-details
        />

        <v-card-actions class="px-0 pt-4 pb-0">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showLeaveModal = false">
            Cancel
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            class="text-none font-weight-bold"
            :disabled="leaveInput.trim().toUpperCase() !== targetLeaveClass.join_code.toUpperCase()"
            :loading="isLeaving"
            @click="confirmLeaveClass"
          >
            Confirm Leave Classroom
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  backendUrl: String,
  userId: Number
})

const toast = ref({ show: false, text: '', color: 'success', icon: 'mdi-check-circle' })
const notify = (text, color = 'success', icon = 'mdi-check-circle') => {
  toast.value = { show: true, text, color, icon }
}

const assignments = ref([])
const showJoinClassModal = ref(false)
const joinCodeInput = ref('')
const isJoining = ref(false)

const showLeaveModal = ref(false)
const targetLeaveClass = ref(null)
const leaveInput = ref('')
const isLeaving = ref(false)

const isRecording = ref(false)
let mediaRecorder = null
let audioChunks = []

const enrolledClasses = computed(() => {
  const map = {}
  assignments.value.forEach(a => {
    if (a.class_id && !map[a.class_id]) {
      map[a.class_id] = {
        class_id: a.class_id,
        class_name: a.class_name,
        join_code: a.join_code || `CLS-${a.class_id}`
      }
    }
  })
  return Object.values(map)
})

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

const submitJoinClass = async (codeToJoin = null) => {
  const code = (codeToJoin || joinCodeInput.value || '').trim()
  if (!code) return
  isJoining.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: props.userId || 1,
        join_code: code
      })
    })
    if (res.ok) {
      const data = await res.json()
      notify(`Success! You joined ${data.class_name}`, 'success', 'mdi-google-classroom')
      showJoinClassModal.value = false
      joinCodeInput.value = ''
      localStorage.removeItem('pending_join_code')
      await fetchStudentAssignments()
    } else {
      const err = await res.json()
      notify(err.detail || 'Invalid Class Join Code.', 'error', 'mdi-alert-circle')
    }
  } catch (e) {
    notify('Failed to join class: ' + e.message, 'error', 'mdi-alert-circle')
  } finally {
    isJoining.value = false
  }
}

const openLeaveClassModal = (cls) => {
  targetLeaveClass.value = cls
  leaveInput.value = ''
  showLeaveModal.value = true
}

const confirmLeaveClass = async () => {
  if (!targetLeaveClass.value) return
  isLeaving.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/leave`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: props.userId || 1,
        class_id: targetLeaveClass.value.class_id
      })
    })
    if (res.ok) {
      notify(`Successfully left ${targetLeaveClass.value.class_name}`, 'success', 'mdi-exit-to-app')
      showLeaveModal.value = false
      targetLeaveClass.value = null
      leaveInput.value = ''
      await fetchStudentAssignments()
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to leave class.', 'error', 'mdi-alert-circle')
    }
  } catch (e) {
    notify('Error leaving class: ' + e.message, 'error', 'mdi-alert-circle')
  } finally {
    isLeaving.value = false
  }
}

const handleUrlJoinCode = async () => {
  const urlParams = new URLSearchParams(window.location.search)
  let code = urlParams.get('join_code') || localStorage.getItem('pending_join_code')
  
  if (code && code.trim()) {
    code = code.trim()
    const activeUser = props.userId || localStorage.getItem('user_id')
    if (!activeUser) {
      localStorage.setItem('pending_join_code', code)
      notify('QR Code detected! Please Sign In or Register to auto-join class.', 'info', 'mdi-qrcode-scan')
    } else {
      await submitJoinClass(code)
      // Clean query parameter from address bar
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }
}

const toggleRecording = async (asg) => {
  if (!isRecording.value) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorder = new MediaRecorder(stream)
      audioChunks = []
      mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data)
      mediaRecorder.onstop = () => uploadSubmission(asg)
      mediaRecorder.start()
      isRecording.value = true
    } catch (e) {
      notify('Microphone access denied: ' + e.message, 'error', 'mdi-microphone-off')
    }
  } else {
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
  formData.append('student_name', 'Student')
  formData.append('audio', blob, 'submission.webm')

  try {
    const res = await fetch(`${props.backendUrl}/api/assignments/submit`, {
      method: 'POST',
      body: formData
    })
    if (res.ok) {
      notify('Submission successful! Voice file uploaded to Supabase Storage.', 'success', 'mdi-cloud-upload')
      await fetchStudentAssignments()
    }
  } catch (e) {
    notify('Submission error: ' + e.message, 'error', 'mdi-alert-circle')
  }
}

onMounted(async () => {
  await fetchStudentAssignments()
  await handleUrlJoinCode()
})
</script>

<style scoped>
.bg-gradient-purple {
  background: linear-gradient(135deg, #7b1fa2 0%, #4a148c 100%);
}
</style>
