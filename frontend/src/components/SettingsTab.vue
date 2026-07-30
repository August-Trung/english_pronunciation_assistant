<template>
  <v-container fluid class="pa-0">
    <v-row class="ma-0">
      <!-- Section 1: Student Profile & Daily Goal (Always Visible) -->
      <v-col cols="12" class="pa-1">
        <v-card border flat class="pa-3 bg-white" rounded="lg">
          <div class="d-flex align-center ga-2 mb-3">
            <v-avatar color="blue-lighten-5" size="36" class="text-primary mr-1 border">
              <v-icon size="small">mdi-account-outline</v-icon>
            </v-avatar>
            <div class="text-subtitle-1 font-weight-black text-secondary">Learner Profile Settings</div>
          </div>
          
          <v-row class="ma-0 align-center ga-2">
            <v-col cols="12" md="6" class="pa-1">
              <v-text-field
                v-model="localUserName"
                label="Full Name:"
                variant="outlined"
                density="comfortable"
                hide-details
                color="primary"
                prepend-inner-icon="mdi-card-account-details-outline"
                @update:model-value="saveSettings"
              />
            </v-col>
            <v-col cols="12" md="6" class="pa-1">
              <div class="d-flex align-center justify-space-between mb-1 px-1 flex-nowrap ga-2">
                <span class="text-caption font-weight-bold text-grey-darken-2 text-truncate">Daily Practice Target:</span>
                <span class="text-caption font-weight-black text-primary bg-blue-lighten-5 px-2 py-0.5 rounded-pill text-no-wrap flex-shrink-0">
                  {{ localDailyGoal }} / day
                </span>
              </div>
              <v-slider
                v-model="localDailyGoal"
                min="1"
                max="15"
                step="1"
                color="primary"
                track-color="grey-lighten-2"
                hide-details
                thumb-label="inverse"
                @update:model-value="saveSettings"
              />
            </v-col>
          </v-row>
        </v-card>
      </v-col>

      <!-- Developer Sections (Visible ONLY when isDevMode prop is true) -->
      <template v-if="isDevMode">
        <!-- Section 2: Backend API Config -->
        <v-col cols="12" class="pa-1">
          <v-card border flat class="pa-3 bg-white" rounded="lg">
            <div class="d-flex align-center ga-2 mb-3">
              <v-avatar color="indigo-lighten-5" size="36" class="text-indigo mr-1 border">
                <v-icon size="small">mdi-server-network</v-icon>
              </v-avatar>
              <div class="text-subtitle-1 font-weight-black text-secondary">[Dev] API Server Connection</div>
            </div>

            <v-row class="ma-0 align-center ga-2">
              <v-col cols="12" sm="8" class="pa-1">
                <v-text-field
                  v-model="localBackendUrl"
                  label="Backend API Endpoint URL:"
                  placeholder="Example: http://localhost:8000"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  color="primary"
                  prepend-inner-icon="mdi-link-variant"
                />
              </v-col>
              <v-col cols="12" sm="4" class="pa-1">
                <v-btn
                  color="primary"
                  variant="flat"
                  block
                  height="48"
                  class="font-weight-bold text-caption text-sm-body-2"
                  prepend-icon="mdi-transit-connection-variant"
                  :loading="isTestingConnection"
                  @click="testConnection"
                >
                  Test Connection
                </v-btn>
              </v-col>
            </v-row>

            <v-alert
              v-if="connectionStatus"
              :type="connectionStatus.success ? 'success' : 'error'"
              density="compact"
              variant="tonal"
              class="mt-3 py-2 text-caption text-sm-subtitle-2 font-weight-medium"
              hide-details
            >
              {{ connectionStatus.message }}
            </v-alert>
          </v-card>
        </v-col>

        <!-- Section 3: Restore Backup -->
        <v-col cols="12" class="pa-1">
          <v-card border flat class="pa-3 bg-white" rounded="lg">
            <div class="d-flex align-center ga-2 mb-2">
              <v-avatar color="purple-lighten-5" size="36" class="text-purple mr-1 border">
                <v-icon size="small">mdi-database-refresh-outline</v-icon>
              </v-avatar>
              <div class="text-subtitle-1 font-weight-black text-secondary">[Dev] Data Restore</div>
            </div>
            <div class="text-caption text-grey-darken-1 mb-3 pl-1">
              Upload a `.json` backup file to restore your historical practice records.
            </div>
            
            <v-row class="ma-0 align-center ga-2">
              <v-col cols="12" sm="8" class="pa-1">
                <v-file-input
                  label="Select Backup File (.json)"
                  accept="application/json"
                  density="comfortable"
                  variant="outlined"
                  hide-details
                  prepend-icon=""
                  prepend-inner-icon="mdi-file-download-outline"
                  @change="handleBackupUpload"
                />
              </v-col>
              <v-col cols="12" sm="4" class="pa-1">
                <v-btn
                  color="secondary"
                  variant="flat"
                  block
                  height="48"
                  class="font-weight-bold text-caption text-sm-body-2"
                  prepend-icon="mdi-cloud-upload-outline"
                  :disabled="!backupFile"
                  @click="restoreBackup"
                >
                  Restore Data
                </v-btn>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </template>

      <!-- Section 4: About App info (Always Visible) -->
      <v-col cols="12" class="pa-1">
        <v-card border flat class="pa-3 bg-blue-lighten-5" rounded="lg">
          <div class="d-flex align-center ga-2 mb-2">
            <v-icon color="primary">mdi-information-outline</v-icon>
            <div class="text-subtitle-2 font-weight-bold text-primary">About FLUENT Pronunciation Studio</div>
          </div>
          
          <div class="text-caption text-grey-darken-3 pl-1" style="line-height: 1.6;">
            <strong>FLUENT - Academic English Pronunciation Assistant</strong><br>
            Empowering students to master native English phonetics and build confident speaking skills through AI evaluation.
            All audio processing is privacy-first and secured.<br>
            • <strong>Version</strong>: 5.0 (Vite + Vue 3 + Vuetify 3 + FastAPI)<br>
            • <strong>Developed by</strong>: August Trung • <strong>Live Web App</strong>: <a href="https://fluent.augusttrung.com" target="_blank" class="text-primary font-weight-bold text-decoration-none">fluent.augusttrung.com</a>
          </div>
        </v-card>
      </v-col>

      <!-- Section 5: Frequently Asked Questions (FAQ) -->
      <v-col cols="12" class="pa-1">
        <v-card border flat class="pa-3 bg-white" rounded="lg">
          <div class="d-flex align-center ga-2 mb-3">
            <v-avatar color="amber-lighten-5" size="36" class="text-amber-darken-3 mr-1 border">
              <v-icon size="small">mdi-help-circle-outline</v-icon>
            </v-avatar>
            <div>
              <div class="text-subtitle-1 font-weight-black text-secondary">Frequently Asked Questions (FAQ)</div>
              <div class="text-caption text-grey-darken-1">Pedagogical AI evaluation, data privacy, and learning methodology guide</div>
            </div>
          </div>

          <v-expansion-panels variant="accordion" class="border rounded-lg overflow-hidden">
            <v-expansion-panel v-for="(faq, i) in faqs" :key="i" elevation="0" class="border-b">
              <v-expansion-panel-title class="py-3 px-3 text-caption text-sm-subtitle-2 font-weight-black text-grey-darken-4">
                <div class="d-flex align-center ga-2">
                  <v-icon color="primary" size="small">mdi-comment-question-outline</v-icon>
                  <span>{{ faq.question }}</span>
                </div>
              </v-expansion-panel-title>
              <v-expansion-panel-text class="text-caption text-grey-darken-3 py-2 px-3 bg-grey-lighten-5" style="line-height: 1.6;">
                <div v-html="faq.answer"></div>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, watch } from 'vue'

const faqs = ref([
  {
    question: "How does AI detect dropped ending consonants and mispronounced phonetics?",
    answer: "<strong>Strict 3-Tier Evaluation Architecture:</strong> (1) Precise phoneme segmentation extracting spoken audio; (2) Phonetic Levenshtein Alignment comparing target vs spoken IPA; (3) AI scoring engine. Any dropped ending consonants (e.g. <code>-s</code>, <code>-ed</code>, <code>-t</code>) or vowel shifts are instantly flagged in red/amber cards."
  },
  {
    question: "What standards are used to evaluate the 6 pedagogical speaking skills?",
    answer: "Skills are evaluated according to international English phonetic standards (IPA chart) combined with Llama 3.3 70B AI engine. The engine analyzes vocabulary precision, speaking rhythm, fluency, sentence stress, and intonation to produce a 10-point academic score."
  },
  {
    question: "Is student voice recording data private and secure?",
    answer: "<strong>100% Private & Secure.</strong> Audio recordings are processed transiently in buffer memory for text extraction and scoring analysis. Records are stored securely under your private cloud account."
  },
  {
    question: "How can I achieve 9.0 - 10.0 scores in Topic Speaking Practice?",
    answer: "To achieve top scores: (1) <strong>Articulate clearly</strong> with distinct ending consonants and word stress; (2) <strong>Stay relevant</strong> to topic prompts; (3) <strong>Use natural sentence structures</strong>. Check the <strong>'Native Expressions'</strong> cards for authentic phrasing."
  },
  {
    question: "What is the difference between Shadowing Studio and Free Topic Practice?",
    answer: "• <strong>Shadowing Studio:</strong> Focuses on mouth muscle articulation, precise phonetic alignment, and mimicking native rhythm.<br>• <strong>Topic Practice:</strong> Focuses on spontaneous English expression, vocabulary choice, and dynamic response creation."
  },
  {
    question: "How do I review and master words I mispronounced?",
    answer: "All mispronounced or dropped consonant words are automatically saved to your <strong>'Weak Words Flashcards'</strong>. You can open flashcards anytime to listen to native audio and practice until mastered."
  },
  {
    question: "How does the IPA Phonetic Evaluation Engine function?",
    answer: "The engine uses G2P (Grapheme-to-Phoneme) <code>g2p_en</code> mapping combined with <strong>Phonetic Levenshtein Alignment</strong>. Each spoken sentence is decomposed into individual IPA symbols to pinpoint exact articulation errors."
  }
])

const props = defineProps({
  userName: {
    type: String,
    required: true
  },
  dailyGoal: {
    type: Number,
    required: true
  },
  backendUrl: {
    type: String,
    required: true
  },
  isDevMode: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update-settings', 'restore-history'])

// Local state initialized from props
const localUserName = ref(props.userName || '')
const localDailyGoal = ref(props.dailyGoal || 5)
const localBackendUrl = ref(props.backendUrl || '')

const isTestingConnection = ref(false)
const connectionStatus = ref(null)

const backupFile = ref(null)

// Watch props to sync changes
watch(() => props.userName, (newVal) => { if (newVal) localUserName.value = newVal })
watch(() => props.dailyGoal, (newVal) => { localDailyGoal.value = newVal || 5 }, { immediate: true })
watch(() => props.backendUrl, (newVal) => { if (newVal) localBackendUrl.value = newVal })

// Save settings to parent
const saveSettings = () => {
  emit('update-settings', {
    userName: localUserName.value,
    dailyGoal: localDailyGoal.value,
    backendUrl: localBackendUrl.value
  })
}

// Watch backend URL change to trigger auto-save
watch(localBackendUrl, () => {
  saveSettings()
})

const testConnection = async () => {
  isTestingConnection.value = true
  connectionStatus.value = null
  
  try {
    const url = localBackendUrl.value.replace(/\/$/, '')
    const response = await fetch(`${url}/api/health`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    })
    
    if (!response.ok) throw new Error()
    
    const data = await response.json()
    if (data.status === 'healthy') {
      connectionStatus.value = {
        success: true,
        message: `🟢 Connection successful! AI Server is healthy (Model: ${data.model_size}).`
      }
    } else {
      connectionStatus.value = {
        success: true,
        message: '🟡 Connection successful! AI Server is warming up model momentarily.'
      }
    }
  } catch (err) {
    connectionStatus.value = {
      success: false,
      message: '🔴 Unable to reach server. Please check the API URL or ensure backend server is active.'
    }
  } finally {
    isTestingConnection.value = false
  }
}

const handleBackupUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    backupFile.value = file
  } else {
    backupFile.value = null
  }
}

const restoreBackup = () => {
  if (!backupFile.value) return
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result)
      if (data && Array.isArray(data.history)) {
        emit('restore-history', data.history)
        alert(`🎉 Restore successful! Restored ${data.history.length} history records into the app.`)
        backupFile.value = null
      } else {
        throw new Error('Invalid schema format.')
      }
    } catch (err) {
      alert('Restore failed. File format does not match application backup schema.')
      console.error(err)
    }
  }
  reader.readAsText(backupFile.value)
}
</script>
