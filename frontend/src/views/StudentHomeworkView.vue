<template>
  <v-container fluid class="pa-4 pa-md-6" style="max-width: 1400px;">
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

    <!-- Inline Deadline Alerts -->
    <v-alert
      v-if="dueSoonAssignments.length > 0"
      type="warning"
      variant="tonal"
      density="comfortable"
      rounded="lg"
      class="mb-4 border-warning font-weight-medium"
      closable
      icon="mdi-clock-alert-outline"
    >
      <div>
        <div class="text-subtitle-2 font-weight-black">
          {{ dueSoonAssignments.length }} assignment{{ dueSoonAssignments.length > 1 ? 's' : '' }} due within 24 hours!
        </div>
        <div class="text-caption text-grey-darken-3">
          Please record and submit your exercises before the deadline to ensure your scores are recorded on time.
        </div>
      </div>
    </v-alert>

    <v-alert
      v-if="overdueAssignments.length > 0"
      type="error"
      variant="tonal"
      density="comfortable"
      rounded="lg"
      class="mb-4 border-error font-weight-medium"
      closable
      icon="mdi-alert-circle-outline"
    >
      <div>
        <div class="text-subtitle-2 font-weight-black">
          {{ overdueAssignments.length }} past-due assignment{{ overdueAssignments.length > 1 ? 's' : '' }}
        </div>
        <div class="text-caption text-grey-darken-3">
          These assignments have passed their deadline. Check with your educator if late submissions are accepted.
        </div>
      </div>
    </v-alert>

    <!-- 2-Column Responsive Workspace -->
    <v-row class="ma-0 ga-3">
      <!-- Left Column: Filter & Assignments Feed (Cols 12, md 8) -->
      <v-col cols="12" md="8" class="pa-0">

    <!-- Filter Tabs by Classroom if Student is in Multiple Classes -->
    <div v-if="enrolledClasses.length > 1" class="d-flex align-center ga-2 overflow-x-auto pb-2 mb-3">
      <v-chip
        :color="selectedClassFilter === 'all' ? 'primary' : 'grey-lighten-4'"
        :variant="selectedClassFilter === 'all' ? 'flat' : 'tonal'"
        size="small"
        class="font-weight-bold flex-shrink-0 cursor-pointer"
        @click="selectedClassFilter = 'all'"
      >
        All Classrooms ({{ assignments.length }})
      </v-chip>
      <v-chip
        v-for="cls in enrolledClasses"
        :key="cls.class_id"
        :color="selectedClassFilter === cls.class_id ? 'primary' : 'grey-lighten-4'"
        :variant="selectedClassFilter === cls.class_id ? 'flat' : 'tonal'"
        size="small"
        class="font-weight-bold flex-shrink-0 cursor-pointer"
        @click="selectedClassFilter = cls.class_id"
      >
        {{ cls.class_name }} ({{ getAssignmentsCountForClass(cls.class_id) }})
      </v-chip>
    </div>

    <!-- Assignments List -->
    <div class="d-flex flex-column ga-3">
      <v-card
        v-for="asg in filteredAssignments"
        :key="asg.assignment_id"
        border
        flat
        class="pa-4 bg-white rounded-lg"
      >
        <div class="d-flex align-center justify-space-between flex-wrap ga-2 mb-2">
          <div>
            <div class="d-flex align-center ga-2 flex-wrap">
              <span class="text-subtitle-1 font-weight-black text-primary">{{ asg.title }}</span>
              <v-chip color="indigo" size="x-small" variant="flat" class="font-weight-bold">
                {{ asg.class_name }}
              </v-chip>
              <v-chip
                size="x-small"
                :color="asg.assignment_type === 'picture' ? 'purple-darken-2' : 'teal-darken-2'"
                variant="tonal"
                class="font-weight-bold"
                :prepend-icon="asg.assignment_type === 'picture' ? 'mdi-image-filter-frames' : 'mdi-waveform'"
              >
                {{ asg.assignment_type === 'picture' ? 'Describe Picture (60s)' : 'Sentence Reading' }}
              </v-chip>
            </div>
            <div class="text-caption text-grey">Due Date: {{ asg.due_date || 'No Deadline' }}</div>
          </div>

          <v-chip
            :color="getDeadlineStatus(asg).color"
            :variant="getDeadlineStatus(asg).status === 'due_soon' ? 'flat' : 'tonal'"
            size="small"
            class="font-weight-black"
            :prepend-icon="getDeadlineStatus(asg).icon"
          >
            {{ getDeadlineStatus(asg).label }}
          </v-chip>
        </div>

        <!-- Format Branch 1: Picture Speaking Challenge -->
        <div v-if="asg.assignment_type === 'picture'" class="mb-3">
          <div class="d-flex ga-3 flex-column flex-md-row mb-2">
            <!-- Scene Image -->
            <div v-if="asg.image_url" class="rounded overflow-hidden border flex-shrink-0" style="max-width: 320px;">
              <v-img
                :src="asg.image_url"
                height="200"
                cover
                class="bg-grey-lighten-4"
              />
            </div>

            <!-- Guiding Questions & Target Keywords -->
            <div class="flex-grow-1 d-flex flex-column justify-space-between ga-2">
              <div v-if="asg.guiding_questions && asg.guiding_questions.length" class="bg-blue-lighten-5 pa-3 rounded border border-blue">
                <div class="text-caption font-weight-black text-blue-darken-3 mb-1 d-flex align-center ga-1">
                  <v-icon size="x-small">mdi-help-circle-outline</v-icon>
                  <span>GUIDING QUESTIONS (STRUCTURE YOUR TALK):</span>
                </div>
                <ul class="text-caption text-grey-darken-3 pl-4 mb-0">
                  <li v-for="(q, idx) in asg.guiding_questions" :key="idx" class="mb-1">
                    {{ q }}
                  </li>
                </ul>
              </div>

              <div v-if="asg.target_keywords && asg.target_keywords.length">
                <div class="text-caption font-weight-black text-grey-darken-3 mb-1 d-flex align-center ga-1">
                  <v-icon size="x-small">mdi-format-list-checks</v-icon>
                  <span>TARGET KEYWORDS (TRY TO INCLUDE):</span>
                </div>
                <div class="d-flex flex-wrap ga-1">
                  <v-chip
                    v-for="kw in asg.target_keywords"
                    :key="kw"
                    size="x-small"
                    color="grey-darken-2"
                    variant="outlined"
                    class="font-weight-bold"
                  >
                    {{ kw }}
                  </v-chip>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Format Branch 2: Standard Sentence Reading -->
        <div v-else class="pa-3 bg-purple-lighten-5 rounded border border-purple mb-3">
          <div class="text-caption font-weight-bold text-purple-darken-3 mb-1">Assigned Model Reading Sentence:</div>
          <div class="text-body-1 font-weight-black text-secondary">"{{ asg.topic_sentence }}"</div>
        </div>

        <!-- Submission Controls or Result -->
        <div v-if="!asg.is_submitted" class="d-flex align-center flex-wrap ga-2">
          <v-btn
            :color="currentRecordingAsgId === asg.assignment_id ? 'error' : 'primary'"
            variant="flat"
            class="font-weight-black text-none"
            :prepend-icon="currentRecordingAsgId === asg.assignment_id ? 'mdi-stop' : 'mdi-microphone'"
            @click="toggleRecording(asg)"
          >
            {{ currentRecordingAsgId === asg.assignment_id ? 'Stop & Submit Voice Recording' : (asg.assignment_type === 'picture' ? 'Start 60s Speaking Recording' : 'Start Voice Recording') }}
          </v-btn>
          <span v-if="currentRecordingAsgId === asg.assignment_id" class="text-caption text-error font-weight-bold">
            🔴 Recording in progress ({{ remainingSeconds }}s remaining)...
          </span>
        </div>

        <div v-else class="bg-grey-lighten-5 pa-3 rounded border">
          <div class="d-flex align-center justify-space-between mb-1">
            <span class="text-caption font-weight-bold text-grey-darken-3">Submitted Audio:</span>
            <v-chip size="x-small" color="success" variant="flat" class="font-weight-bold">Score: {{ asg.score?.toFixed(1) }}/10</v-chip>
          </div>
          <div v-if="asg.audio_url" class="d-flex align-center ga-2 mb-2">
            <audio controls :src="asg.audio_url" class="w-100" style="height: 32px;" />
          </div>
          <div v-if="asg.teacher_feedback" class="text-caption text-grey-darken-3 bg-white pa-2 rounded border" style="white-space: pre-line;">
            <div class="font-weight-bold text-indigo mb-1">Assessment & Feedback:</div>
            {{ asg.teacher_feedback }}
          </div>
        </div>
      </v-card>

      <div v-if="!filteredAssignments.length" class="text-center pa-8 bg-white border rounded-lg">
        <v-icon size="48" color="grey-lighten-1">mdi-clipboard-check-outline</v-icon>
        <template v-if="enrolledClasses.length">
          <div class="text-subtitle-1 font-weight-black text-indigo-darken-2 mt-2">
            You're all caught up!
          </div>
          <div class="text-subtitle-2 font-weight-medium text-grey-darken-1 mt-1">
            Your teacher has not assigned any homework for your classroom yet. Check back soon!
          </div>
        </template>
        <template v-else>
          <div class="text-subtitle-2 font-weight-bold text-grey-darken-1 mt-2">
            You are not enrolled in any classroom yet.
          </div>
          <div class="text-caption text-grey mt-1">
            Enter a classroom join code provided by your teacher to access class homework.
          </div>
          <v-btn
            color="primary"
            variant="tonal"
            class="mt-3 text-none font-weight-bold"
            prepend-icon="mdi-key-variant"
            @click="showJoinClassModal = true"
          >
            Enter Join Code (Example: CLS-836-58)
          </v-btn>
        </template>
      </div>
    </div>
  </v-col>

  <!-- Right Column: Classrooms & Performance Sidebar (Cols 12, md 4) -->
  <v-col cols="12" md="4" class="pa-0">
    <div class="sticky-side d-flex flex-column ga-3">
      <!-- Summary Metrics Card -->
      <v-card border flat class="pa-4 bg-white rounded-lg">
        <div class="text-caption font-weight-black text-secondary mb-2 d-flex align-center ga-1">
          <v-icon size="small" color="secondary">mdi-chart-pie</v-icon>
          <span>HOMEWORK PROGRESS</span>
        </div>
        <div class="d-flex align-center justify-space-between mb-2">
          <span class="text-caption font-weight-bold text-grey-darken-2">Submitted Rate:</span>
          <span class="text-subtitle-2 font-weight-black text-primary">
            {{ assignments.filter(a => a.is_submitted).length }} / {{ assignments.length }}
          </span>
        </div>
        <v-progress-linear
          :model-value="assignments.length ? (assignments.filter(a => a.is_submitted).length / assignments.length) * 100 : 0"
          color="primary"
          height="8"
          rounded
          class="mb-3"
        />
      </v-card>

      <!-- Enrolled Classes Card -->
      <v-card v-if="enrolledClasses.length" border flat class="pa-4 bg-white rounded-lg">
        <div class="text-caption font-weight-black text-secondary mb-3 d-flex align-center justify-space-between">
          <span>MY CLASSROOMS ({{ enrolledClasses.length }})</span>
          <v-btn size="x-small" variant="text" color="primary" @click="showJoinClassModal = true">
            + Join Another
          </v-btn>
        </div>
        <div class="d-flex flex-column ga-2">
          <div
            v-for="cls in enrolledClasses"
            :key="cls.class_id"
            class="pa-2.5 rounded-lg border bg-grey-lighten-5 d-flex align-center justify-space-between"
          >
            <div>
              <div class="font-weight-black text-caption text-indigo-darken-3 d-flex align-center ga-1">
                <v-icon size="x-small" color="indigo">mdi-google-classroom</v-icon>
                <span>{{ cls.class_name }}</span>
              </div>
              <div class="text-caption text-grey" style="font-size: 10px;">
                Code: <strong>{{ cls.join_code || 'Enrolled' }}</strong>
                <span v-if="cls.teacher_name"> &bull; Teacher: {{ cls.teacher_name }}</span>
              </div>
            </div>

            <v-btn
              icon="mdi-exit-to-app"
              variant="text"
              size="small"
              color="error"
              title="Leave Class"
              @click.stop="openLeaveClassModal(cls)"
            />
          </div>
        </div>
      </v-card>
    </div>
  </v-col>
</v-row>

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
const classesList = ref([])
const showJoinClassModal = ref(false)
const joinCodeInput = ref('')
const isJoining = ref(false)

const showLeaveModal = ref(false)
const targetLeaveClass = ref(null)
const leaveInput = ref('')
const isLeaving = ref(false)

const currentRecordingAsgId = ref(null)
const remainingSeconds = ref(60)
let timerInterval = null
let mediaRecorder = null
let audioChunks = []

const enrolledClasses = computed(() => {
  if (classesList.value?.length) {
    return classesList.value
  }
  const map = {}
  assignments.value?.forEach(a => {
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

const selectedClassFilter = ref('all')
const filteredAssignments = computed(() => {
  if (selectedClassFilter.value === 'all') return assignments.value
  return assignments.value.filter(a => a.class_id === selectedClassFilter.value)
})

const getAssignmentsCountForClass = (classId) => {
  return assignments.value.filter(a => a.class_id === classId).length
}

const parseDueDate = (dueStr) => {
  if (!dueStr) return null
  const str = String(dueStr).trim()
  if (/^\d{4}-\d{2}-\d{2}$/.test(str)) {
    return new Date(`${str}T23:59:59`)
  }
  return new Date(str.replace(' ', 'T'))
}

const getDeadlineStatus = (asg) => {
  if (asg.is_submitted) {
    return { status: 'submitted', label: `Submitted (${asg.score != null ? asg.score.toFixed(1) : '10'}/10)`, color: 'success', icon: 'mdi-check-circle' }
  }
  if (!asg.due_date) {
    return { status: 'pending', label: 'Pending', color: 'warning', icon: undefined }
  }
  const dueDate = parseDueDate(asg.due_date)
  if (!dueDate || isNaN(dueDate.getTime())) {
    return { status: 'pending', label: 'Pending', color: 'warning', icon: undefined }
  }
  const now = Date.now()
  const diffHours = (dueDate.getTime() - now) / (1000 * 60 * 60)
  
  if (diffHours < 0) {
    return { status: 'overdue', label: 'Past Due', color: 'error', icon: 'mdi-alert-circle' }
  }
  if (diffHours <= 24) {
    const totalMinutes = Math.max(1, Math.round((dueDate.getTime() - now) / (1000 * 60)))
    const hrs = Math.floor(totalMinutes / 60)
    const mins = totalMinutes % 60
    const timeText = hrs > 0 ? `${hrs}h left` : `${mins}m left`
    return { status: 'due_soon', label: `Due Soon (${timeText})`, color: 'warning', icon: 'mdi-clock-fast' }
  }
  return { status: 'pending', label: 'Pending', color: 'warning', icon: undefined }
}

const dueSoonAssignments = computed(() => {
  return assignments.value.filter(a => getDeadlineStatus(a).status === 'due_soon')
})

const overdueAssignments = computed(() => {
  return assignments.value.filter(a => getDeadlineStatus(a).status === 'overdue')
})

const getActiveStudentId = () => {
  return props.userId || Number(localStorage.getItem('user_id')) || null
}

const fetchEnrolledClasses = async () => {
  const uid = getActiveStudentId()
  if (!uid) return
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/student/${uid}`)
    if (res.ok) {
      const data = await res.json()
      classesList.value = data.classes || []
    }
  } catch (e) {
    console.error('Fetch student classes error:', e)
  }
}

const fetchStudentAssignments = async () => {
  const uid = getActiveStudentId()
  if (!uid) return
  try {
    const res = await fetch(`${props.backendUrl}/api/assignments/student/${uid}`)
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
  const uid = getActiveStudentId()
  if (!uid) {
    notify('Please sign in to join a classroom.', 'warning', 'mdi-account-lock')
    return
  }
  isJoining.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: uid,
        join_code: code
      })
    })
    if (res.ok) {
      const data = await res.json()
      notify(`Success! You joined ${data.class_name}`, 'success', 'mdi-google-classroom')
      showJoinClassModal.value = false
      joinCodeInput.value = ''
      localStorage.removeItem('pending_join_code')
      await fetchEnrolledClasses()
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
  const uid = getActiveStudentId()
  if (!uid) return
  isLeaving.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/leave`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: uid,
        class_id: targetLeaveClass.value.class_id
      })
    })
    if (res.ok) {
      notify(`Successfully left ${targetLeaveClass.value.class_name}`, 'success', 'mdi-exit-to-app')
      showLeaveModal.value = false
      targetLeaveClass.value = null
      leaveInput.value = ''
      await fetchEnrolledClasses()
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
    const uid = getActiveStudentId()
    if (!uid) {
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
  if (currentRecordingAsgId.value !== asg.assignment_id) {
    if (currentRecordingAsgId.value && mediaRecorder) {
      mediaRecorder.stop()
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorder = new MediaRecorder(stream)
      audioChunks = []
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.push(e.data)
      }
      mediaRecorder.onstop = () => {
        stream.getTracks().forEach(t => t.stop())
        if (timerInterval) clearInterval(timerInterval)
        uploadSubmission(asg)
      }
      mediaRecorder.start()
      currentRecordingAsgId.value = asg.assignment_id
      remainingSeconds.value = asg.time_limit_seconds || 60

      timerInterval = setInterval(() => {
        if (remainingSeconds.value > 1) {
          remainingSeconds.value--
        } else {
          toggleRecording(asg)
        }
      }, 1000)
    } catch (e) {
      notify('Microphone access denied: ' + e.message, 'error', 'mdi-microphone-off')
    }
  } else {
    if (timerInterval) clearInterval(timerInterval)
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop()
    }
    currentRecordingAsgId.value = null
  }
}

const uploadSubmission = async (asg) => {
  const uid = getActiveStudentId()
  const blob = new Blob(audioChunks, { type: 'audio/webm' })
  const formData = new FormData()
  formData.append('assignment_id', asg.assignment_id)
  formData.append('student_id', uid || 1)
  formData.append('student_name', 'Student')
  formData.append('audio', blob, 'submission.webm')

  try {
    const res = await fetch(`${props.backendUrl}/api/assignments/submit`, {
      method: 'POST',
      body: formData
    })
    if (res.ok) {
      notify('Submission successful! AI speech score recorded.', 'success', 'mdi-check-circle')
      await fetchStudentAssignments()
    }
  } catch (e) {
    notify('Submission error: ' + e.message, 'error', 'mdi-alert-circle')
  }
}

onMounted(async () => {
  await fetchEnrolledClasses()
  await fetchStudentAssignments()
  await handleUrlJoinCode()
})
</script>

<style scoped>
.bg-gradient-purple {
  background: linear-gradient(135deg, #7b1fa2 0%, #4a148c 100%);
}
</style>
