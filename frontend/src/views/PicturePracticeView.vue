<template>
  <v-container fluid class="pa-0 max-width-1100">
    <!-- Header Banner -->
    <v-card border flat class="pa-3 pa-sm-4 mb-4 text-white rounded-lg" style="background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%);">
      <div class="d-flex align-center justify-space-between flex-wrap ga-2">
        <div class="d-flex align-center ga-2 ga-sm-3">
          <v-avatar color="white" size="44" class="flex-shrink-0 elevation-1">
            <v-icon color="blue-darken-3" size="default">mdi-image-filter-frames</v-icon>
          </v-avatar>
          <div>
            <div class="text-subtitle-1 text-sm-h6 font-weight-black tracking-tight leading-tight">
              DESCRIBE THE PICTURE
            </div>
            <div class="text-caption text-blue-lighten-4">
              Practice speaking fluently by describing pictures with instant feedback
            </div>
          </div>
        </div>

        <div class="d-flex align-center ga-2">
          <v-btn
            color="white"
            variant="flat"
            size="small"
            class="text-blue-darken-3 font-weight-black text-none"
            prepend-icon="mdi-plus-circle"
            @click="showCreateModal = true"
          >
            New AI Scenario
          </v-btn>
        </div>
      </div>
    </v-card>

    <!-- Recent Scenarios Quick Switcher -->
    <div v-if="scenarios.length > 0" class="mb-4">
      <div class="text-caption font-weight-bold text-grey-darken-2 mb-1">Recent Practice Scenarios:</div>
      <div class="d-flex flex-wrap ga-2 align-center">
        <v-chip
          v-for="s in scenarios"
          :key="s.scenario_id"
          :color="currentScenario?.scenario_id === s.scenario_id ? 'primary' : 'grey-lighten-2'"
          :variant="currentScenario?.scenario_id === s.scenario_id ? 'flat' : 'outlined'"
          size="small"
          class="font-weight-bold cursor-pointer"
          @click="selectScenario(s)"
        >
          <v-icon start size="x-small">mdi-image-outline</v-icon>
          {{ s.title }}
        </v-chip>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoadingInitial" class="text-center py-12">
      <v-progress-circular indeterminate color="primary" size="44" class="mb-2" />
      <div class="text-caption text-grey">Loading speaking scenarios...</div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!currentScenario" class="text-center py-12 border rounded-lg bg-white pa-6">
      <v-avatar color="blue-lighten-5" size="64" class="mb-3">
        <v-icon size="large" color="primary">mdi-image-plus</v-icon>
      </v-avatar>
      <div class="text-subtitle-1 font-weight-black text-grey-darken-4 mb-1">No Speaking Scenarios Available</div>
      <div class="text-caption text-grey mb-4 max-width-500 mx-auto">
        Create an AI scenario to practice describing scenes under IELTS Speaking Part 2 and TOEIC format.
      </div>
      <v-btn color="primary" variant="flat" class="text-none font-weight-bold" prepend-icon="mdi-sparkles" @click="showCreateModal = true">
        Generate AI Scenario
      </v-btn>
    </div>

    <!-- Main Practice Grid (2 Columns) -->
    <v-row v-else dense class="mb-4">
      <!-- Left Column: Visual Scenario & Guidance -->
      <v-col cols="12" md="6">
        <v-card border flat class="pa-4 rounded-lg bg-white h-100 d-flex flex-column justify-space-between">
          <div>
            <div class="d-flex align-center justify-space-between mb-2">
              <v-chip size="x-small" color="primary" variant="tonal" class="font-weight-black text-uppercase">
                {{ currentScenario.topic || 'Daily Life' }}
              </v-chip>
              <span class="text-caption text-grey">Scenario #{{ currentScenario.scenario_id }}</span>
            </div>

            <div class="text-h6 font-weight-black text-grey-darken-4 mb-2">
              {{ currentScenario.title }}
            </div>

            <!-- Picture Image Canvas with Hover Zoom -->
            <div class="image-wrapper rounded-lg overflow-hidden border mb-3 position-relative cursor-pointer" @click="showImagePreview = true">
              <v-img
                :src="currentScenarioImage"
                height="280"
                cover
                class="bg-grey-lighten-4"
                @error="handleImageError"
              >
                <template #placeholder>
                  <div class="d-flex align-center justify-center fill-height">
                    <v-progress-circular indeterminate color="primary" size="36" />
                  </div>
                </template>
              </v-img>
              <div class="image-zoom-overlay d-flex align-center justify-center">
                <v-icon color="white" size="large">mdi-magnify-plus-outline</v-icon>
              </div>
            </div>

            <!-- Guiding Questions -->
            <div class="bg-blue-lighten-5 pa-3 rounded-lg border border-blue mb-3">
              <div class="text-caption font-weight-black text-blue-darken-3 mb-1">
                <v-icon size="x-small" class="mr-1">mdi-help-circle-outline</v-icon>
                GUIDING QUESTIONS (STRUCTURE YOUR TALK):
              </div>
              <ul class="text-caption text-grey-darken-3 pl-4 mb-0">
                <li v-for="(q, idx) in (currentScenario.guiding_questions || [])" :key="idx" class="mb-1">
                  {{ q }}
                </li>
              </ul>
            </div>

            <!-- Target Keywords Checklist -->
            <div>
              <div class="text-caption font-weight-black text-grey-darken-3 mb-1">
                <v-icon size="x-small" class="mr-1">mdi-format-list-checks</v-icon>
                TARGET KEYWORDS (TRY TO INCLUDE):
              </div>
              <div class="d-flex flex-wrap ga-1">
                <v-chip
                  v-for="kw in (currentScenario.keywords || [])"
                  :key="kw"
                  size="small"
                  :color="isKeywordSpoken(kw) ? 'success' : 'grey-lighten-2'"
                  :variant="isKeywordSpoken(kw) ? 'flat' : 'outlined'"
                  class="font-weight-bold"
                >
                  <v-icon start size="x-small">
                    {{ isKeywordSpoken(kw) ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                  </v-icon>
                  {{ kw }}
                </v-chip>
              </div>
            </div>
          </div>
        </v-card>
      </v-col>

      <!-- Right Column: Speaking Studio & Assessment Report -->
      <v-col cols="12" md="6">
        <v-card border flat class="pa-4 rounded-lg bg-white h-100 d-flex flex-column justify-space-between">
          <!-- State 1: Idle / Ready to Record -->
          <div v-if="!isRecording && !isEvaluating && !evaluationResult" class="text-center py-8">
            <v-avatar color="blue-lighten-5" size="80" class="mb-4">
              <v-icon size="48" color="primary">mdi-microphone</v-icon>
            </v-avatar>
            <div class="text-h6 font-weight-black text-grey-darken-4 mb-1">60-Second Speaking Challenge</div>
            <div class="text-caption text-grey mb-6 max-width-400 mx-auto">
              Observe the picture carefully. Tap the button below to start your recording. Describe the setting, characters, and actions naturally.
            </div>

            <v-btn
              color="primary"
              size="large"
              variant="flat"
              class="text-none font-weight-black px-6"
              prepend-icon="mdi-record-rec"
              @click="startRecording"
            >
              Start Recording Now
            </v-btn>
          </div>

          <!-- State 2: Active Recording Live -->
          <div v-else-if="isRecording" class="text-center py-6">
            <div class="d-flex align-center justify-center ga-2 mb-4">
              <span class="recording-pulse"></span>
              <span class="text-caption font-weight-black text-error text-uppercase tracking-wider">RECORDING LIVE</span>
            </div>

            <div class="text-h2 font-weight-black text-grey-darken-4 mb-2 font-mono">
              00:{{ remainingSeconds < 10 ? '0' + remainingSeconds : remainingSeconds }}
            </div>
            <div class="text-caption text-grey mb-6">Speak clearly and aim to use the target keywords on the left</div>

            <!-- Waveform Animation Placeholder -->
            <div class="waveform-box d-flex align-center justify-center ga-1 mb-6">
              <span v-for="n in 12" :key="n" class="waveform-bar"></span>
            </div>

            <v-btn
              color="error"
              size="large"
              variant="flat"
              class="text-none font-weight-black px-6"
              prepend-icon="mdi-stop"
              @click="stopRecording"
            >
              Finish & Evaluate Speech
            </v-btn>
          </div>

          <!-- State 3: Processing & Evaluating -->
          <div v-else-if="isEvaluating" class="text-center py-12">
            <v-progress-circular indeterminate color="primary" size="56" width="5" class="mb-4" />
            <div class="text-subtitle-1 font-weight-black text-grey-darken-4 mb-1">Evaluating Your Response...</div>
            <div class="text-caption text-grey max-width-350 mx-auto">
              Analyzing your speech and evaluating your fluency, grammar, and vocabulary...
            </div>
          </div>

          <!-- State 4: Comprehensive AI Evaluation Card -->
          <div v-else-if="evaluationResult" class="d-flex flex-column justify-space-between fill-height">
            <div>
              <div class="d-flex align-center justify-space-between border-b pb-2 mb-3">
                <div class="d-flex align-center ga-2">
                  <v-avatar color="indigo-lighten-5" size="36">
                    <v-icon color="indigo">mdi-star-circle</v-icon>
                  </v-avatar>
                  <div>
                    <div class="text-subtitle-2 font-weight-black text-grey-darken-4">SPEAKING ASSESSMENT REPORT</div>
                    <div class="text-caption text-grey">Performance Breakdown</div>
                  </div>
                </div>

                <div class="text-right">
                  <span class="text-h5 font-weight-black text-primary">{{ evaluationResult.score }}</span>
                  <span class="text-caption text-grey">/100</span>
                </div>
              </div>

              <!-- Metric Badges Row -->
              <v-row dense class="mb-3">
                <v-col cols="4">
                  <v-card border flat class="pa-2 text-center rounded bg-grey-lighten-4">
                    <div class="text-caption text-grey-darken-1">Fluency</div>
                    <div class="text-subtitle-2 font-weight-black text-indigo-darken-3">{{ evaluationResult.fluency_score || 0 }}%</div>
                  </v-card>
                </v-col>
                <v-col cols="4">
                  <v-card border flat class="pa-2 text-center rounded bg-grey-lighten-4">
                    <div class="text-caption text-grey-darken-1">Vocabulary</div>
                    <div class="text-subtitle-2 font-weight-black text-green-darken-3">{{ evaluationResult.vocabulary_score || 0 }}%</div>
                  </v-card>
                </v-col>
                <v-col cols="4">
                  <v-card border flat class="pa-2 text-center rounded bg-grey-lighten-4">
                    <div class="text-caption text-grey-darken-1">Grammar</div>
                    <div class="text-subtitle-2 font-weight-black text-deep-purple-darken-3">{{ evaluationResult.grammar_score || 0 }}%</div>
                  </v-card>
                </v-col>
              </v-row>

              <!-- Spoken Transcription -->
              <div class="mb-3">
                <div class="text-caption font-weight-black text-grey-darken-2 mb-1">YOUR SPEECH TRANSCRIPTION:</div>
                <div class="text-body-2 text-grey-darken-4 bg-grey-lighten-5 pa-2 rounded border font-italic">
                  "{{ candidateTranscription || 'No speech captured.' }}"
                </div>
              </div>

              <!-- AI Tutor Feedback in Vietnamese -->
              <div class="mb-3">
                <div class="text-caption font-weight-black text-indigo-darken-3 mb-1">AI EXAMINER FEEDBACK (TIẾNG VIỆT):</div>
                <div class="text-caption text-grey-darken-4 bg-indigo-lighten-5 pa-3 rounded border border-indigo">
                  {{ evaluationResult.feedback }}
                </div>
              </div>

              <!-- Native Sample Response -->
              <div class="mb-3" v-if="evaluationResult.sample_response">
                <div class="d-flex align-center justify-space-between mb-1">
                  <div class="text-caption font-weight-black text-teal-darken-3">EXEMPLARY NATIVE RESPONSE:</div>
                  <v-btn
                    size="x-small"
                    variant="text"
                    color="teal-darken-3"
                    prepend-icon="mdi-volume-high"
                    @click="playSampleAudio(evaluationResult.sample_response)"
                  >
                    Listen
                  </v-btn>
                </div>
                <div class="text-caption text-grey-darken-3 bg-teal-lighten-5 pa-2 rounded border border-teal font-italic">
                  "{{ evaluationResult.sample_response }}"
                </div>
              </div>
            </div>

            <!-- Retry / Continue Actions -->
            <div class="d-flex align-center justify-space-between pt-3 border-t ga-2">
              <v-btn
                variant="outlined"
                color="primary"
                size="small"
                class="text-none flex-grow-1 font-weight-bold"
                prepend-icon="mdi-refresh"
                @click="resetChallenge"
              >
                Try Again
              </v-btn>

              <v-btn
                variant="flat"
                color="primary"
                size="small"
                class="text-none flex-grow-1 font-weight-bold"
                prepend-icon="mdi-arrow-right"
                @click="showCreateModal = true"
              >
                Next Challenge
              </v-btn>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Dialog: Image Fullscreen Zoom -->
    <v-dialog v-model="showImagePreview" max-width="800">
      <v-card class="pa-2 bg-black text-right">
        <v-btn icon="mdi-close" variant="text" color="white" size="small" @click="showImagePreview = false" />
        <v-img :src="currentScenarioImage" max-height="600" contain />
      </v-card>
    </v-dialog>

    <!-- Dialog: Create New AI Scenario Modal -->
    <v-dialog v-model="showCreateModal" max-width="540">
      <v-card border rounded="lg" class="pa-4 bg-white">
        <div class="d-flex align-center justify-space-between mb-3 border-b pb-2">
          <div class="d-flex align-center ga-2">
            <v-avatar color="primary-lighten-5" size="36">
              <v-icon color="primary">mdi-sparkles</v-icon>
            </v-avatar>
            <div class="text-subtitle-1 font-weight-black text-grey-darken-4">Create New Speaking Scenario</div>
          </div>
          <v-btn icon="mdi-close" variant="text" size="small" @click="showCreateModal = false" />
        </div>

        <div class="text-caption text-grey-darken-1 mb-3">
          Create an engaging picture scene with guiding questions and key vocabulary to practice your speaking skills.
        </div>

        <v-text-field
          v-model="scenarioTopic"
          label="Scenario Topic / Theme"
          placeholder="e.g. Modern Airport Terminal, Crowded Weekend Market, High-Tech Office..."
          variant="outlined"
          density="comfortable"
          class="mb-2"
          prepend-inner-icon="mdi-image-search-outline"
        />

        <!-- Topic suggestions -->
        <div class="mb-3">
          <div class="text-caption font-weight-bold text-grey mb-1">Quick Ideas:</div>
          <div class="d-flex flex-wrap ga-1">
            <v-chip
              v-for="idea in suggestedTopics"
              :key="idea"
              size="x-small"
              variant="tonal"
              color="blue-darken-2"
              class="cursor-pointer font-weight-bold"
              @click="scenarioTopic = idea"
            >
              {{ idea }}
            </v-chip>
          </div>
        </div>

        <v-select
          v-model="scenarioLevel"
          :items="['Beginner', 'Intermediate', 'Advanced']"
          label="Target Speaking Level"
          variant="outlined"
          density="comfortable"
          class="mb-2"
        />

        <v-card-actions class="px-0 pb-0 pt-2 border-t">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showCreateModal = false">Cancel</v-btn>
          <v-btn
            color="primary"
            variant="flat"
            class="text-none font-weight-bold"
            prepend-icon="mdi-auto-fix"
            :loading="isGeneratingScenario"
            @click="handleCreateScenario"
          >
            Generate Scenario
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  backendUrl: String,
  userId: Number
})

const imageFailed = ref(false)

const handleImageError = () => {
  imageFailed.value = true
}

const makeSvgCard = (title, topic, subtitle) => {
  const t = (topic || '').toLowerCase()
  let c1 = '#0F172A', c2 = '#1E1B4B', c3 = '#2563EB', accent = '#93C5FD', pill = '#1D4ED8'
  if (t.includes('science') || t.includes('lab') || t.includes('tech') || t.includes('computer')) {
    c1 = '#090D16'; c2 = '#0F172A'; c3 = '#0284C7'; accent = '#38BDF8'; pill = '#0369A1'
  } else if (t.includes('cafe') || t.includes('coffee') || t.includes('food') || t.includes('market') || t.includes('daily')) {
    c1 = '#1C1917'; c2 = '#451A03'; c3 = '#B45309'; accent = '#FBBF24'; pill = '#78350F'
  } else if (t.includes('work') || t.includes('interview') || t.includes('job') || t.includes('office') || t.includes('business')) {
    c1 = '#0B0F19'; c2 = '#1E1B4B'; c3 = '#4338CA'; accent = '#A5B4FC'; pill = '#312E81'
  } else if (t.includes('travel') || t.includes('nature') || t.includes('airport')) {
    c1 = '#042F2E'; c2 = '#064E3B'; c3 = '#059669'; accent = '#6EE7B7'; pill = '#065F46'
  }

  const safeTitle = (title || 'Speaking Scene').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').slice(0, 45)
  const safeTopic = (topic || 'Daily Life').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').slice(0, 25).toUpperCase()
  const safeSub = (subtitle || 'Observe details, setting, characters and actions').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').slice(0, 60)

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="480" viewBox="0 0 800 480">
    <defs>
      <linearGradient id="bgG" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="${c1}"/>
        <stop offset="50%" stop-color="${c2}"/>
        <stop offset="100%" stop-color="${c3}"/>
      </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#bgG)"/>
    <circle cx="700" cy="80" r="140" fill="${accent}" opacity="0.15"/>
    <circle cx="100" cy="400" r="120" fill="${c3}" opacity="0.2"/>
    <rect x="36" y="36" width="728" height="408" rx="20" fill="white" fill-opacity="0.04" stroke="white" stroke-opacity="0.12" stroke-width="1.5"/>
    <g transform="translate(64, 60)">
      <rect width="170" height="28" rx="14" fill="${pill}" fill-opacity="0.5" stroke="${accent}" stroke-opacity="0.4" stroke-width="1"/>
      <text x="85" y="19" fill="${accent}" font-family="system-ui, sans-serif" font-size="11" font-weight="700" text-anchor="middle" letter-spacing="1.2">${safeTopic}</text>
    </g>
    <circle cx="400" cy="180" r="44" fill="white" fill-opacity="0.08" stroke="${accent}" stroke-width="2"/>
    <circle cx="400" cy="180" r="36" fill="${c1}" fill-opacity="0.85"/>
    <path d="M392 166h16v16h-16zM388 186h24v4h-24z" fill="${accent}"/>
    <text x="400" y="275" fill="#FFFFFF" font-family="system-ui, sans-serif" font-size="28" font-weight="800" text-anchor="middle">${safeTitle}</text>
    <text x="400" y="312" fill="#CBD5E1" font-family="system-ui, sans-serif" font-size="16" font-weight="500" text-anchor="middle">${safeSub}</text>
    <rect x="280" y="380" width="240" height="26" rx="13" fill="white" fill-opacity="0.06" stroke="white" stroke-opacity="0.1" stroke-width="1"/>
    <text x="400" y="397" fill="#94A3B8" font-family="system-ui, sans-serif" font-size="11" font-weight="600" text-anchor="middle" letter-spacing="1">DESCRIBE PICTURE SCENARIO</text>
  </svg>`
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`
}

const getImageUrl = (url) => {
  if (!url) return '/logo-augusttrung.png'
  if (url.startsWith('http') || url.startsWith('data:')) return url
  const base = props.backendUrl?.replace(/\/$/, '') || 'https://agrse-fluent-english-backend.hf.space'
  return `${base}${url.startsWith('/') ? '' : '/'}${url}`
}

const currentScenarioImage = computed(() => {
  const rawUrl = currentScenario.value?.image_url
  if (imageFailed.value || !rawUrl || rawUrl.includes('pollinations.ai')) {
    return makeSvgCard(
      currentScenario.value?.title || 'Speaking Scenario',
      currentScenario.value?.topic || 'Daily Life',
      currentScenario.value?.image_prompt || ''
    )
  }
  return getImageUrl(rawUrl)
})

const scenarios = ref([])
const currentScenario = ref(null)
const isLoadingInitial = ref(false)

const showCreateModal = ref(false)
const isGeneratingScenario = ref(false)
const showImagePreview = ref(false)
const scenarioTopic = ref('')
const scenarioLevel = ref('Intermediate')

const suggestedTopics = [
  'City Street Cafe',
  'Airport Departure Lounge',
  'University Science Lab',
  'Crowded Weekend Market',
  'Hospital Emergency Room'
]

// Recording state
const isRecording = ref(false)
const remainingSeconds = ref(60)
let timerInterval = null
let mediaRecorder = null
let recordedAudioChunks = []

// Evaluation state
const isEvaluating = ref(false)
const candidateTranscription = ref('')
const evaluationResult = ref(null)

const selectScenario = (s) => {
  currentScenario.value = s
  imageFailed.value = false
  resetChallenge()
}

const isKeywordSpoken = (keyword) => {
  if (!candidateTranscription.value || !keyword) return false
  return candidateTranscription.value.toLowerCase().includes(keyword.toLowerCase())
}

const fetchScenarios = async () => {
  isLoadingInitial.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/picture-practice/scenarios?user_id=${props.userId || 1}`)
    if (res.ok) {
      const data = await res.json()
      scenarios.value = data.scenarios || []
      if (scenarios.value.length > 0 && !currentScenario.value) {
        currentScenario.value = scenarios.value[0]
      }
    }
  } catch (err) {
    console.error('Failed to load scenarios:', err)
  } finally {
    isLoadingInitial.value = false
  }
}

const handleCreateScenario = async () => {
  const topic = scenarioTopic.value.trim() || 'Daily Life Scene'
  isGeneratingScenario.value = true

  try {
    const res = await fetch(`${props.backendUrl}/api/picture-practice/create-scenario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topic,
        level: scenarioLevel.value.toLowerCase(),
        user_id: props.userId || 1
      })
    })

    if (res.ok) {
      const newScenario = await res.json()
      showCreateModal.value = false
      scenarioTopic.value = ''
      await fetchScenarios()
      currentScenario.value = newScenario
      imageFailed.value = false
      resetChallenge()
    }
  } catch (err) {
    console.error('Scenario creation failed:', err)
  } finally {
    isGeneratingScenario.value = false
  }
}

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    recordedAudioChunks = []
    mediaRecorder = new MediaRecorder(stream)
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) recordedAudioChunks.push(e.data)
    }
    mediaRecorder.onstop = () => {
      stream.getTracks().forEach(t => t.stop())
      evaluateSpeakingSubmission()
    }

    mediaRecorder.start()
    isRecording.value = true
    remainingSeconds.value = 60

    timerInterval = setInterval(() => {
      if (remainingSeconds.value > 1) {
        remainingSeconds.value--
      } else {
        stopRecording()
      }
    }, 1000)
  } catch (err) {
    alert('Microphone access is required to practice speaking.')
  }
}

const stopRecording = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  if (isRecording.value) {
    isRecording.value = false
    mediaRecorder?.stop()
  }
}

const evaluateSpeakingSubmission = async () => {
  if (recordedAudioChunks.length === 0 || !currentScenario.value) return
  isEvaluating.value = true

  try {
    const audioBlob = new Blob(recordedAudioChunks, { type: 'audio/webm' })
    const formData = new FormData()
    formData.append('audio', audioBlob, 'speaking.webm')
    formData.append('topic_sentence', currentScenario.value.title)
    formData.append('user_id', props.userId || 1)

    // 1. Transcribe speech via Whisper API
    const assessRes = await fetch(`${props.backendUrl}/api/assess_pronunciation`, {
      method: 'POST',
      body: formData
    })

    let transcribedText = ''
    if (assessRes.ok) {
      const assessData = await assessRes.json()
      transcribedText = assessData.transcription || assessData.transcribed || ''
    }
    candidateTranscription.value = transcribedText || 'Speech captured without transcription'

    // 2. Evaluate picture speaking with LLM examiner
    const evalRes = await fetch(`${props.backendUrl}/api/picture-practice/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scenario_id: currentScenario.value.scenario_id,
        transcription: candidateTranscription.value,
        user_id: props.userId || 1
      })
    })

    if (evalRes.ok) {
      evaluationResult.value = await evalRes.json()
    }
  } catch (err) {
    console.error('Failed to evaluate speaking submission:', err)
  } finally {
    isEvaluating.value = false
  }
}

const playSampleAudio = (text) => {
  if (!text) return
  window.speechSynthesis?.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'en-US'
  window.speechSynthesis?.speak(utterance)
}

const resetChallenge = () => {
  if (timerInterval) clearInterval(timerInterval)
  isRecording.value = false
  isEvaluating.value = false
  evaluationResult.value = null
  candidateTranscription.value = ''
  remainingSeconds.value = 60
}

onMounted(() => {
  fetchScenarios()
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<style scoped>
.max-width-1100 {
  max-width: 1100px;
  margin: 0 auto;
}
.max-width-500 {
  max-width: 500px;
}
.max-width-400 {
  max-width: 400px;
}
.max-width-350 {
  max-width: 350px;
}

.image-wrapper {
  position: relative;
}
.image-zoom-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  opacity: 0;
  transition: opacity 0.2s ease;
}
.image-wrapper:hover .image-zoom-overlay {
  opacity: 1;
}

.recording-pulse {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #EF4444;
  animation: pulse 1.2s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
  70% { transform: scale(1.15); box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

.waveform-box {
  height: 40px;
}
.waveform-bar {
  width: 4px;
  height: 24px;
  background-color: #3B82F6;
  border-radius: 2px;
  animation: wave 1s infinite ease-in-out;
}
.waveform-bar:nth-child(2n) { animation-delay: 0.2s; height: 32px; }
.waveform-bar:nth-child(3n) { animation-delay: 0.4s; height: 16px; }
.waveform-bar:nth-child(4n) { animation-delay: 0.1s; height: 36px; }

@keyframes wave {
  0%, 100% { transform: scaleY(0.4); }
  50% { transform: scaleY(1); }
}
</style>
