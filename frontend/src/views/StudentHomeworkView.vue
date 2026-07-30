<template>
  <v-container fluid class="pa-4 pa-md-6" style="max-width: 900px;">
    <!-- Vuetify Toast Notification -->
    <v-snackbar
      v-model="toast.show"
      :color="toast.color"
      location="top"
      timeout="3500"
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

    <!-- Modal: Join Class Dialog -->
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
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'

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
      notify(`Success! You joined ${data.class_name}`, 'success', 'mdi-google-classroom')
      showJoinClassModal.value = false
      joinCodeInput.value = ''
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

onMounted(() => {
  fetchStudentAssignments()
})
</script>

<style scoped>
.bg-gradient-purple {
  background: linear-gradient(135deg, #7b1fa2 0%, #4a148c 100%);
}
</style>
