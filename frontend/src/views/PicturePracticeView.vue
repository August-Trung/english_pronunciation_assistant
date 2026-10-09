<template>
  <v-container fluid class="pa-0 max-width-1400">
    <!-- Header Banner -->
    <v-card border flat class="pa-3 pa-sm-4 mb-4 text-white rounded-lg" style="background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%);">
      <div class="d-flex align-center justify-space-between flex-wrap ga-2">
        <div class="d-flex align-center ga-2 ga-sm-3">
          <v-avatar color="white" size="44" class="flex-shrink-0 elevation-1">
            <v-icon color="blue-darken-3" size="default">mdi-image-filter-frames</v-icon>
          </v-avatar>
          <div>
            <div class="text-subtitle-1 text-sm-h6 font-weight-black tracking-tight leading-tight">
              DESCRIBE THE PICTURE STUDIO
            </div>
            <div class="text-caption text-blue-lighten-4">
              IELTS Speaking Part 2 & TOEIC Questions 3-4 Multimodal Practice with Instant AI Grounding
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
            @click="openCreateModal"
          >
            New Scenario
          </v-btn>
        </div>
      </div>
    </v-card>

    <!-- Recent Scenarios Quick Switcher -->
    <div v-if="scenarios.length > 0" class="mb-4">
      <div class="d-flex align-center justify-space-between mb-1">
        <span class="text-caption font-weight-bold text-grey-darken-2">Recent Practice Scenarios:</span>
        <span class="text-caption text-grey">{{ scenarios.length }} scenarios saved</span>
      </div>
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
        Create an AI scenario with custom prompt, search real photos, or upload your own image to practice describing scenes.
      </div>
      <v-btn color="primary" variant="flat" class="text-none font-weight-bold" prepend-icon="mdi-sparkles" @click="openCreateModal">
        Create Scenario
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
                {{ currentScenario.topic || 'General Practice' }}
              </v-chip>
              <span class="text-caption text-grey font-weight-medium">Scenario #{{ currentScenario.scenario_id || currentScenario.id || 1 }}</span>
            </div>

            <div class="text-h6 font-weight-black text-grey-darken-4 mb-1">
              {{ currentScenario.title }}
            </div>

            <!-- Clearly Display User's Input Prompt / Topic -->
            <div v-if="currentScenario.topic" class="d-flex align-center ga-1 mb-3 text-caption text-grey-darken-2 bg-grey-lighten-4 px-2 py-1 rounded border">
              <v-icon size="x-small" color="primary">mdi-message-text-outline</v-icon>
              <span class="text-grey font-weight-medium">Your Prompt / Topic:</span>
              <strong class="text-grey-darken-4 font-weight-bold">"{{ currentScenario.topic }}"</strong>
            </div>

            <!-- Picture Image Canvas with Hover Zoom -->
            <div class="image-wrapper rounded-lg overflow-hidden border mb-3 position-relative cursor-pointer" @click="showImagePreview = true">
              <v-img
                :src="currentScenarioImage"
                height="300"
                cover
                class="bg-grey-lighten-4"
              >
                <template #placeholder>
                  <div class="d-flex flex-column align-center justify-center fill-height bg-grey-lighten-3 ga-2">
                    <v-progress-circular indeterminate color="primary" size="36" />
                    <span class="text-caption text-grey font-weight-medium">Loading AI Picture...</span>
                  </div>
                </template>
                <template #error>
                  <div class="d-flex flex-column align-center justify-center fill-height bg-grey-lighten-3 pa-4 text-center ga-1">
                    <v-icon color="grey-darken-1" size="36">mdi-image-broken-variant</v-icon>
                    <div class="text-caption font-weight-bold text-grey-darken-3">Image failed to load</div>
                    <v-btn size="x-small" color="primary" variant="outlined" prepend-icon="mdi-refresh" @click.stop="reloadImage">
                      Retry
                    </v-btn>
                  </div>
                </template>
              </v-img>
              <div class="image-zoom-overlay d-flex align-center justify-center">
                <v-icon color="white" size="large">mdi-magnify-plus-outline</v-icon>
                <span class="text-caption text-white font-weight-bold ml-1">Click to Zoom</span>
              </div>
            </div>

            <!-- Guiding Questions Section (Dynamic) -->
            <div v-if="currentScenario?.guiding_questions?.length" class="mb-3">
              <div class="text-caption font-weight-black text-grey-darken-3 mb-2 d-flex align-center ga-1">
                <v-icon size="x-small" color="primary">mdi-help-circle-outline</v-icon>
                <span>GUIDING QUESTIONS:</span>
              </div>
              <div class="d-flex flex-column ga-2">
                <div
                  v-for="(q, idx) in currentScenario.guiding_questions"
                  :key="idx"
                  class="bg-grey-lighten-5 pa-3 rounded-lg border text-caption text-grey-darken-3 d-flex align-start ga-2"
                >
                  <v-chip size="x-small" color="primary" variant="flat" class="font-weight-black flex-shrink-0 mt-0">
                    Q{{ idx + 1 }}
                  </v-chip>
                  <span class="font-weight-medium line-height-normal">{{ q }}</span>
                </div>
              </div>
            </div>

            <!-- Target Keywords Checklist -->
            <div>
              <div class="d-flex align-center justify-space-between mb-1">
                <div class="text-caption font-weight-black text-grey-darken-3 d-flex align-center ga-1">
                  <v-icon size="x-small" color="primary">mdi-format-list-checks</v-icon>
                  <span>TARGET KEYWORDS (TRY TO INCLUDE):</span>
                </div>
                <span v-if="evaluationResult" class="text-caption font-weight-bold text-success">
                  {{ matchedKeywordsCount }} / {{ (currentScenario.keywords || []).length }} used
                </span>
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
          <!-- State 1: Active Recording Studio / Ready to Speak -->
          <div v-if="!evaluationResult && !isEvaluating">
            <div class="d-flex align-center justify-space-between mb-3 border-b pb-2">
              <div class="d-flex align-center ga-2">
                <v-icon color="primary" size="small">mdi-microphone</v-icon>
                <span class="text-subtitle-2 font-weight-black text-grey-darken-4">Speaking Studio</span>
              </div>
              <v-chip size="x-small" color="primary" variant="tonal" class="font-weight-bold">
                <v-icon start size="x-small">mdi-timer-outline</v-icon>
                Pacing: 45s – 60s
              </v-chip>
            </div>

            <!-- Stopwatch Digital Display & Pacing Indicator -->
            <div class="text-center py-6 bg-grey-lighten-5 rounded-lg border mb-4">
              <div class="text-h3 font-weight-black font-mono tracking-tight mb-2" :class="timerColorClass">
                {{ formatTime(elapsedSeconds) }}
              </div>

              <!-- Pacing Advice Pill -->
              <v-chip
                size="small"
                :color="pacingBadge.color"
                variant="flat"
                class="font-weight-bold"
              >
                <v-icon start size="x-small">{{ pacingBadge.icon }}</v-icon>
                {{ pacingBadge.label }}
              </v-chip>

              <!-- Recording Visualizer Waveform -->
              <div v-if="isRecording" class="waveform-box d-flex align-center justify-center ga-1 mt-4">
                <span class="waveform-bar" v-for="n in 8" :key="n" />
              </div>
            </div>

            <!-- Microphone Controls -->
            <div class="d-flex flex-column align-center ga-3">
              <div class="d-flex align-center ga-3 w-100 justify-center">
                <v-btn
                  v-if="!isRecording"
                  color="primary"
                  variant="flat"
                  size="large"
                  class="font-weight-black text-none px-8"
                  prepend-icon="mdi-microphone"
                  @click="startRecording"
                >
                  Start Speaking
                </v-btn>

                <template v-else>
                  <v-btn
                    color="error"
                    variant="flat"
                    size="large"
                    class="font-weight-black text-none px-6"
                    prepend-icon="mdi-stop-circle"
                    @click="stopRecording"
                  >
                    Finish & Submit
                  </v-btn>
                  <v-btn
                    variant="outlined"
                    color="grey-darken-2"
                    size="large"
                    class="font-weight-bold text-none"
                    @click="cancelRecording"
                  >
                    Cancel
                  </v-btn>
                </template>
              </div>

              <div class="text-caption text-grey text-center max-width-400">
                Tip: Describe the setting, actions, key objects, and your overall impression of the picture.
              </div>
            </div>
          </div>

          <!-- State 2: Evaluating Loader -->
          <div v-else-if="isEvaluating" class="text-center py-12">
            <v-progress-circular indeterminate color="primary" size="48" width="4" class="mb-3" />
            <div class="text-subtitle-2 font-weight-black text-grey-darken-3">
              AI Examiner Analyzing Your Speech...
            </div>
            <div class="text-caption text-grey mt-1">
              Transcribing audio via Whisper & scoring vocabulary, fluency, and picture details
            </div>
          </div>

          <!-- State 3: Detailed Assessment Report -->
          <div v-else class="evaluation-report">
            <div class="d-flex align-center justify-space-between mb-3 border-b pb-2">
              <div class="d-flex align-center ga-2">
                <v-icon color="success" size="small">mdi-certificate</v-icon>
                <span class="text-subtitle-2 font-weight-black text-grey-darken-4">Evaluation Report</span>
              </div>
              <v-chip color="primary" variant="flat" size="small" class="font-weight-black">
                Score: {{ evaluationResult.score }} / 100
              </v-chip>
            </div>

            <!-- Score Cards -->
            <v-row dense class="mb-3">
              <v-col cols="4">
                <div class="bg-blue-lighten-5 pa-2 rounded text-center border">
                  <div class="text-caption text-grey font-weight-bold">Fluency</div>
                  <div class="text-subtitle-1 font-weight-black text-primary">{{ evaluationResult.fluency_score || 70 }}</div>
                </div>
              </v-col>
              <v-col cols="4">
                <div class="bg-indigo-lighten-5 pa-2 rounded text-center border">
                  <div class="text-caption text-grey font-weight-bold">Vocabulary</div>
                  <div class="text-subtitle-1 font-weight-black text-indigo">{{ evaluationResult.vocabulary_score || 75 }}</div>
                </div>
              </v-col>
              <v-col cols="4">
                <div class="bg-purple-lighten-5 pa-2 rounded text-center border">
                  <div class="text-caption text-grey font-weight-bold">Grammar</div>
                  <div class="text-subtitle-1 font-weight-black text-purple">{{ evaluationResult.grammar_score || 70 }}</div>
                </div>
              </v-col>
            </v-row>

            <!-- Transcription -->
            <div class="bg-grey-lighten-4 pa-3 rounded-lg border mb-3">
              <div class="text-caption font-weight-black text-grey-darken-2 mb-1">YOUR SPEECH TRANSCRIPTION:</div>
              <div class="text-body-2 text-grey-darken-4 font-italic" style="line-height: 1.5;">
                "{{ candidateTranscription }}"
              </div>
            </div>

            <!-- AI Examiner Feedback -->
            <div class="bg-amber-lighten-5 pa-3 rounded-lg border border-amber mb-3">
              <div class="text-caption font-weight-black text-amber-darken-4 mb-1 d-flex align-center ga-1">
                <v-icon size="x-small" color="amber-darken-4">mdi-comment-text-outline</v-icon>
                <span>AI EXAMINER FEEDBACK:</span>
              </div>
              <div class="text-caption text-grey-darken-3" style="line-height: 1.5; white-space: pre-line;">
                {{ evaluationResult.feedback }}
              </div>
            </div>

            <!-- Band 8+ Model Answer for Shadowing -->
            <div v-if="currentScenario.sample_response || evaluationResult.sample_response" class="bg-teal-lighten-5 pa-3 rounded-lg border border-teal mb-4">
              <div class="d-flex align-center justify-space-between mb-1">
                <div class="text-caption font-weight-black text-teal-darken-4 d-flex align-center ga-1">
                  <v-icon size="x-small" color="teal-darken-4">mdi-star-circle</v-icon>
                  <span>BAND 8+ MODEL ANSWER (LISTEN & SHADOW):</span>
                </div>
                <v-btn
                  size="x-small"
                  variant="flat"
                  color="teal-darken-3"
                  class="font-weight-bold text-none"
                  :prepend-icon="isPlayingSample ? 'mdi-stop' : 'mdi-volume-high'"
                  @click="toggleSampleAudio(currentScenario.sample_response || evaluationResult.sample_response)"
                >
                  {{ isPlayingSample ? 'Stop' : 'Listen' }}
                </v-btn>
              </div>
              <div class="text-caption text-grey-darken-4" style="line-height: 1.5;">
                {{ currentScenario.sample_response || evaluationResult.sample_response }}
              </div>
            </div>

            <!-- Bottom Actions -->
            <div class="d-flex align-center ga-2">
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
                prepend-icon="mdi-plus-circle"
                @click="openCreateModal"
              >
                New Scenario
              </v-btn>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Dialog: Image Fullscreen Zoom -->
    <v-dialog v-model="showImagePreview" max-width="850">
      <v-card class="pa-2 bg-black text-right" rounded="lg">
        <v-btn icon="mdi-close" variant="text" color="white" size="small" @click="showImagePreview = false" />
        <v-img :src="currentScenarioImage" max-height="650" contain />
      </v-card>
    </v-dialog>

    <!-- Dialog: Multi-mode Create New Scenario Modal -->
    <v-dialog v-model="showCreateModal" max-width="580">
      <v-card border rounded="lg" class="pa-4 bg-white">
        <div class="d-flex align-center justify-space-between mb-3 border-b pb-2">
          <div class="d-flex align-center ga-2">
            <v-avatar color="primary-lighten-5" size="36">
              <v-icon color="primary">mdi-sparkles</v-icon>
            </v-avatar>
            <div>
              <div class="text-subtitle-1 font-weight-black text-grey-darken-4">New Speaking Scenario</div>
              <div class="text-caption text-grey">Create with AI prompt, search photos, or upload an image</div>
            </div>
          </div>
          <v-btn icon="mdi-close" variant="text" size="small" @click="showCreateModal = false" />
        </div>

        <!-- 3 Modes Tabs -->
        <v-tabs v-model="creationMode" color="primary" density="comfortable" class="mb-3 border-b">
          <v-tab value="ai_gen" class="text-none font-weight-bold text-caption">
            <v-icon start size="small">mdi-auto-fix</v-icon>
            AI Prompt
          </v-tab>
          <v-tab value="search" class="text-none font-weight-bold text-caption">
            <v-icon start size="small">mdi-image-search</v-icon>
            Photo Search
          </v-tab>
          <v-tab value="upload" class="text-none font-weight-bold text-caption">
            <v-icon start size="small">mdi-upload</v-icon>
            Upload Photo
          </v-tab>
        </v-tabs>

        <v-window v-model="creationMode">
          <!-- Tab 1: AI Prompt Generator -->
          <v-window-item value="ai_gen" class="pt-2">
            <label class="text-caption font-weight-bold text-grey-darken-2 d-block mb-1">
              Describe What Picture You Want (Prompt):
            </label>
            <v-textarea
              v-model="scenarioTopic"
              placeholder="e.g. A family having a picnic in the park with a golden retriever and red checkered blanket..."
              variant="outlined"
              rows="3"
              density="comfortable"
              class="mb-2"
              prepend-inner-icon="mdi-pencil-outline"
              hide-details="auto"
              clearable
            />

            <!-- Prompt Sparks / Quick Idea Chips -->
            <div class="mb-3">
              <div class="text-caption font-weight-bold text-grey-darken-2 mb-1 d-flex align-center ga-1">
                <v-icon size="x-small" color="primary">mdi-lightbulb-on-outline</v-icon>
                <span>Quick Prompt Sparks:</span>
              </div>
              <div class="d-flex flex-wrap ga-1">
                <v-chip
                  v-for="spark in promptSparks"
                  :key="spark"
                  size="x-small"
                  variant="outlined"
                  color="primary"
                  class="font-weight-medium cursor-pointer"
                  @click="scenarioTopic = spark"
                >
                  {{ spark }}
                </v-chip>
              </div>
            </div>
          </v-window-item>

          <!-- Tab 2: Real Photo Search -->
          <v-window-item value="search" class="pt-2">
            <label class="text-caption font-weight-bold text-grey-darken-2 d-block mb-1">
              Photo Subject / Search Topic:
            </label>
            <v-text-field
              v-model="searchKeyword"
              placeholder="e.g. Airport Terminal, Hospital Consultation, Modern Classroom, Cafe..."
              variant="outlined"
              density="comfortable"
              class="mb-2"
              prepend-inner-icon="mdi-magnify"
              hide-details="auto"
              clearable
            />

            <div class="d-flex flex-wrap ga-1 mb-3">
              <v-chip
                v-for="cat in quickSearchCategories"
                :key="cat"
                size="x-small"
                variant="tonal"
                color="indigo"
                class="font-weight-bold cursor-pointer"
                @click="searchKeyword = cat"
              >
                {{ cat }}
              </v-chip>
            </div>
          </v-window-item>

          <!-- Tab 3: Custom Upload -->
          <v-window-item value="upload" class="pt-2">
            <div class="mb-3 border-dashed rounded-lg pa-4 text-center bg-grey-lighten-5">
              <input
                ref="fileInputRef"
                type="file"
                accept="image/*"
                class="d-none"
                @change="handleFileUploadChange"
              />

              <div v-if="!uploadedPreviewUrl" class="cursor-pointer" @click="$refs.fileInputRef?.click()">
                <v-avatar color="primary-lighten-5" size="48" class="mb-2">
                  <v-icon color="primary" size="default">mdi-cloud-upload</v-icon>
                </v-avatar>
                <div class="text-subtitle-2 font-weight-bold text-grey-darken-3">Click to select photo</div>
                <div class="text-caption text-grey">Support JPG, PNG, WEBP (textbook questions, exam photos)</div>
              </div>

              <div v-else class="position-relative">
                <v-img :src="uploadedPreviewUrl" height="180" cover class="rounded border mb-2" />
                <v-btn
                  size="x-small"
                  variant="tonal"
                  color="error"
                  prepend-icon="mdi-close"
                  class="text-none font-weight-bold"
                  @click="clearUploadedFile"
                >
                  Remove & Choose Another
                </v-btn>
              </div>
            </div>

            <label class="text-caption font-weight-bold text-grey-darken-2 d-block mb-1">
              Optional Topic / Title Hint:
            </label>
            <v-text-field
              v-model="uploadTitleHint"
              placeholder="e.g. Cambridge PET Exam Picture 3..."
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-tag-outline"
              hide-details="auto"
              class="mb-2"
            />
          </v-window-item>
        </v-window>

        <!-- Common Level Selector -->
        <label class="text-caption font-weight-bold text-grey-darken-2 d-block mb-1">
          Target Speaking Level:
        </label>
        <v-select
          v-model="scenarioLevel"
          :items="['Beginner', 'Intermediate', 'Advanced']"
          variant="outlined"
          density="comfortable"
          hide-details="auto"
          class="mb-3"
        />

        <v-card-actions class="px-0 pb-0 pt-2 border-t">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showCreateModal = false">
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            class="text-none font-weight-bold px-4"
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

const imageReloadKey = ref(0)
const reloadImage = () => {
  imageReloadKey.value++
}

const getImageUrl = (url) => {
  if (!url) return '/logo-augusttrung.png'
  if (url.startsWith('http') || url.startsWith('data:')) return url
  const base = props.backendUrl?.replace(/\/$/, '') || 'https://agrse-fluent-english-backend.hf.space'
  return `${base}${url.startsWith('/') ? '' : '/'}${url}`
}

const currentScenarioImage = computed(() => {
  const rawUrl = currentScenario.value?.image_url
  if (!rawUrl) return '/logo-augusttrung.png'
  const url = getImageUrl(rawUrl)
  if (imageReloadKey.value > 0) {
    const sep = url.includes('?') ? '&' : '?'
    return `${url}${sep}_r=${imageReloadKey.value}`
  }
  return url
})

// Scenarios state
const scenarios = ref([])
const currentScenario = ref(null)
const isLoadingInitial = ref(false)

// Create Scenario Modal State
const showCreateModal = ref(false)
const creationMode = ref('ai_gen')
const scenarioTopic = ref('')
const searchKeyword = ref('')
const uploadTitleHint = ref('')
const scenarioLevel = ref('Intermediate')
const isGeneratingScenario = ref(false)
const showImagePreview = ref(false)

// Custom file upload state
const selectedFile = ref(null)
const uploadedPreviewUrl = ref('')
const fileInputRef = ref(null)

const promptSparks = [
  'A family having a picnic with a golden retriever',
  'Two students conducting a science experiment in chemistry lab',
  'Busy international airport departure hall with passengers',
  'A doctor consulting an elderly patient in modern clinic',
  'Two coworkers having an interview in a sunlit meeting room',
  'A vibrant outdoor street food market in evening with lanterns'
]

const quickSearchCategories = [
  'Airport Terminal', 'University Library', 'Job Interview', 'City Street',
  'Modern Classroom', 'Hospital Clinic', 'Coffee Shop', 'Farmers Market'
]

const openCreateModal = () => {
  showCreateModal.value = true
}

const handleFileUploadChange = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  selectedFile.value = file
  uploadedPreviewUrl.value = URL.createObjectURL(file)
}

const clearUploadedFile = () => {
  selectedFile.value = null
  if (uploadedPreviewUrl.value) {
    URL.revokeObjectURL(uploadedPreviewUrl.value)
    uploadedPreviewUrl.value = ''
  }
  if (fileInputRef.value) fileInputRef.value.value = ''
}


// Recording & Stopwatch State
const isRecording = ref(false)
const elapsedSeconds = ref(0)
let timerInterval = null
let mediaRecorder = null
let recordedAudioChunks = []

const timerColorClass = computed(() => {
  if (!isRecording.value) return 'text-grey-darken-3'
  if (elapsedSeconds.value < 30) return 'text-amber-darken-3'
  if (elapsedSeconds.value <= 65) return 'text-success'
  return 'text-primary'
})

const pacingBadge = computed(() => {
  if (!isRecording.value && elapsedSeconds.value === 0) {
    return {
      label: 'Ready to Record • Aim for 45s – 60s for full score',
      color: 'indigo',
      icon: 'mdi-timer-play-outline'
    }
  }
  if (elapsedSeconds.value < 30) {
    return { label: 'Brief (< 30s) • Aim for 45s – 60s for full score', color: 'amber-darken-2', icon: 'mdi-clock-outline' }
  }
  if (elapsedSeconds.value <= 65) {
    return { label: 'Ideal Speaking Length (45s – 60s)', color: 'success', icon: 'mdi-check-circle' }
  }
  return { label: 'Extended Talk (> 65s)', color: 'primary', icon: 'mdi-timer-outline' }
})

const formatTime = (secs) => {
  const m = Math.floor(secs / 60)
  const s = secs % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

// Evaluation State
const isEvaluating = ref(false)
const candidateTranscription = ref('')
const evaluationResult = ref(null)
const isPlayingSample = ref(false)

const selectScenario = (s) => {
  currentScenario.value = s
  imageReloadKey.value = 0
  resetChallenge()
}

const isKeywordSpoken = (keyword) => {
  if (!candidateTranscription.value || !keyword) return false
  return candidateTranscription.value.toLowerCase().includes(keyword.toLowerCase())
}

const matchedKeywordsCount = computed(() => {
  const kws = currentScenario.value?.keywords || []
  return kws.filter(kw => isKeywordSpoken(kw)).length
})

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
  isGeneratingScenario.value = true
  let finalTopic = ''
  let finalImageUrl = ''
  const mode = creationMode.value

  try {
    if (mode === 'upload' && selectedFile.value) {
      // 1. Upload file first
      const formData = new FormData()
      formData.append('file', selectedFile.value)
      const uploadRes = await fetch(`${props.backendUrl}/api/picture-practice/upload-image`, {
        method: 'POST',
        body: formData
      })
      if (!uploadRes.ok) throw new Error('File upload failed')
      const uploadData = await uploadRes.json()
      finalImageUrl = uploadData.image_url
      finalTopic = uploadTitleHint.value.trim() || selectedFile.value.name.replace(/\.[^/.]+$/, '')
    } else if (mode === 'search') {
      finalTopic = searchKeyword.value.trim() || 'Daily Life'
    } else {
      finalTopic = scenarioTopic.value.trim() || 'A vibrant outdoor scene in the city'
    }

    // 2. Call create scenario endpoint
    const res = await fetch(`${props.backendUrl}/api/picture-practice/create-scenario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: finalTopic,
        level: scenarioLevel.value.toLowerCase(),
        mode: mode,
        image_url: finalImageUrl,
        user_id: props.userId || 1
      })
    })

    if (res.ok) {
      const newScenario = await res.json()
      showCreateModal.value = false
      scenarioTopic.value = ''
      searchKeyword.value = ''
      clearUploadedFile()
      await fetchScenarios()
      currentScenario.value = newScenario
      imageReloadKey.value = 0
      resetChallenge()
    }
  } catch (err) {
    console.error('Scenario creation failed:', err)
    alert('Failed to generate scenario. Please try again.')
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
    elapsedSeconds.value = 0

    timerInterval = setInterval(() => {
      elapsedSeconds.value++
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

const cancelRecording = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  if (isRecording.value) {
    isRecording.value = false
    mediaRecorder?.stop()
    recordedAudioChunks = []
    resetChallenge()
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

const toggleSampleAudio = (text) => {
  if (!text) return
  if (isPlayingSample.value) {
    window.speechSynthesis?.cancel()
    isPlayingSample.value = false
    return
  }
  window.speechSynthesis?.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'en-US'
  utterance.rate = 0.95
  utterance.onend = () => {
    isPlayingSample.value = false
  }
  utterance.onerror = () => {
    isPlayingSample.value = false
  }
  isPlayingSample.value = true
  window.speechSynthesis?.speak(utterance)
}

const resetChallenge = () => {
  if (timerInterval) clearInterval(timerInterval)
  window.speechSynthesis?.cancel()
  isPlayingSample.value = false
  isRecording.value = false
  isEvaluating.value = false
  evaluationResult.value = null
  candidateTranscription.value = ''
  elapsedSeconds.value = 0
}

onMounted(() => {
  fetchScenarios()
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
  window.speechSynthesis?.cancel()
})
</script>

<style scoped>
.max-width-1400 {
  max-width: 1400px;
  margin: 0 auto;
}
.max-width-500 {
  max-width: 500px;
}
.max-width-400 {
  max-width: 400px;
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
  background: rgba(0, 0, 0, 0.35);
  opacity: 0;
  transition: opacity 0.2s ease;
}
.image-wrapper:hover .image-zoom-overlay {
  opacity: 1;
}

.waveform-box {
  height: 36px;
}
.waveform-bar {
  width: 4px;
  height: 24px;
  background-color: #0284C7;
  border-radius: 2px;
  animation: wave 1s infinite ease-in-out;
}
.waveform-bar:nth-child(2n) { animation-delay: 0.2s; height: 30px; }
.waveform-bar:nth-child(3n) { animation-delay: 0.4s; height: 16px; }
.waveform-bar:nth-child(4n) { animation-delay: 0.1s; height: 34px; }

@keyframes wave {
  0%, 100% { transform: scaleY(0.4); }
  50% { transform: scaleY(1); }
}
</style>
