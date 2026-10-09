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
          label="Custom Topic or Speaking Scenario"
          placeholder="e.g. Modern Airport Terminal, Hospital Emergency Hallway, High-Tech Lab..."
          variant="outlined"
          density="comfortable"
          class="mb-2"
          prepend-inner-icon="mdi-image-search-outline"
          clearable
        />

        <!-- Category & AI Spark Topics -->
        <div class="mb-3">
          <div class="d-flex align-center justify-space-between mb-1">
            <span class="text-caption font-weight-black text-secondary d-flex align-center ga-1">
              <v-icon size="x-small" color="secondary">mdi-sparkles</v-icon>
              <span>AI TOPIC SPARK (IELTS & TOEIC THEMES)</span>
            </span>
            <v-btn
              variant="text"
              size="x-small"
              color="primary"
              class="text-none font-weight-bold"
              :loading="isLoadingTopics"
              prepend-icon="mdi-refresh"
              @click="fetchSuggestedTopics"
            >
              Refresh Ideas
            </v-btn>
          </div>

          <div class="d-flex flex-wrap ga-1 mb-2">
            <v-chip
              v-for="cat in topicCategories"
              :key="cat"
              :color="selectedCategory === cat ? 'primary' : 'grey-lighten-3'"
              :variant="selectedCategory === cat ? 'flat' : 'tonal'"
              size="x-small"
              class="font-weight-bold cursor-pointer"
              @click="selectCategory(cat)"
            >
              {{ cat }}
            </v-chip>
          </div>

          <!-- Suggested Topics Grid -->
          <div class="d-flex flex-column ga-1 overflow-y-auto" style="max-height: 180px;">
            <div
              v-for="item in filteredSuggestedTopics"
              :key="item.id"
              class="pa-2 border rounded cursor-pointer d-flex align-center justify-space-between transition-all"
              :class="scenarioTopic === item.title ? 'bg-blue-lighten-5 border-blue' : 'bg-grey-lighten-5'"
              @click="selectTopicItem(item)"
            >
              <div class="d-flex align-center ga-2 text-truncate mr-2">
                <v-icon size="small" :color="scenarioTopic === item.title ? 'primary' : 'grey-darken-1'">
                  {{ item.icon || 'mdi-image-outline' }}
                </v-icon>
                <div class="text-truncate">
                  <div class="text-caption font-weight-black text-grey-darken-4 text-truncate">
                    {{ item.title }}
                  </div>
                  <div class="text-caption text-grey text-truncate" style="font-size: 11px;">
                    {{ item.description }}
                  </div>
                </div>
              </div>
              <v-chip size="x-small" color="indigo" variant="tonal" class="font-weight-bold flex-shrink-0">
                {{ item.category }}
              </v-chip>
            </div>
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

const PHOTO_CATALOG = {
  science: [
    'https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1579154204601-01588f351e67?auto=format&fit=crop&w=1000&q=80'
  ],
  cafe: [
    'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1442512595331-e89e73853f31?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1000&q=80'
  ],
  airport: [
    'https://images.unsplash.com/photo-1530521954074-e64f6810b32d?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1520437358207-323b43b50729?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1517400508447-f8dd518b86db?auto=format&fit=crop&w=1000&q=80'
  ],
  office: [
    'https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=1000&q=80'
  ],
  interview: [
    'https://images.unsplash.com/photo-1521791136064-7986c2920216?auto=format&fit=crop&w=1000&q=80'
  ],
  portrait: [
    'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=1000&q=80'
  ],
  market: [
    'https://images.unsplash.com/photo-1488459716781-31db52582fe9?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1534723452862-4c874018d66d?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1578916171728-46686eac8d58?auto=format&fit=crop&w=1000&q=80'
  ],
  library: [
    'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1541829070764-84a7d30dd3f3?auto=format&fit=crop&w=1000&q=80'
  ],
  hospital: [
    'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=1000&q=80'
  ],
  city: [
    'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?auto=format&fit=crop&w=1000&q=80'
  ],
  park: [
    'https://images.unsplash.com/photo-1496347646636-ea47f7d6b37b?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1519331379826-f10be5486c6f?auto=format&fit=crop&w=1000&q=80'
  ],
  classroom: [
    'https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=1000&q=80'
  ],
  restaurant: [
    'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?auto=format&fit=crop&w=1000&q=80'
  ],
  hotel: [
    'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1000&q=80'
  ],
  technology: [
    'https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1000&q=80'
  ],
  kitchen: [
    'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1507048331197-7d4ac70811cf?auto=format&fit=crop&w=1000&q=80'
  ],
  nature: [
    'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80'
  ],
  fitness: [
    'https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=1000&q=80'
  ],
  art: [
    'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=1000&q=80'
  ],
  zoo: [
    'https://images.unsplash.com/photo-1543372742-e7d0b9947a2b?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=1000&q=80'
  ],
  beach: [
    'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80'
  ],
  sports: [
    'https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&w=1000&q=80'
  ],
  traffic: [
    'https://images.unsplash.com/photo-1506521781263-d8422e82f27a?auto=format&fit=crop&w=1000&q=80'
  ],
  camping: [
    'https://images.unsplash.com/photo-1510312305653-8ed496efae75?auto=format&fit=crop&w=1000&q=80'
  ],
  family: [
    'https://images.unsplash.com/photo-1543353071-10c8ba85a904?auto=format&fit=crop&w=1000&q=80'
  ],
  shopping: [
    'https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1000&q=80'
  ],
  music: [
    'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=1000&q=80'
  ],
  farm: [
    'https://images.unsplash.com/photo-1500595046743-cd271d694d30?auto=format&fit=crop&w=1000&q=80'
  ]
}

const resolveScenePhoto = (topic, title) => {
  const combined = `${topic || ''} ${title || ''}`.toLowerCase()
  let pool = PHOTO_CATALOG.nature
  if (/zoo|animal|safari|wildlife|giraffe|elephant|zebra|lion|tiger|bear|sở thú|thảo cầm viên|động vật/.test(combined)) {
    pool = PHOTO_CATALOG.zoo
  } else if (/beach|sea|ocean|coast|shore|island|sand|summer|biển|bãi biển/.test(combined)) {
    pool = PHOTO_CATALOG.beach
  } else if (/sport|football|soccer|basketball|tennis|stadium|athlete|thể thao|bóng đá/.test(combined)) {
    pool = PHOTO_CATALOG.sports
  } else if (/traffic|commute|subway|transit|road congestion|giao thông|kẹt xe|xe buýt/.test(combined)) {
    pool = PHOTO_CATALOG.traffic
  } else if (/camp|camping|tent|campfire|hiking|picnic|cắm trại|dã ngoại/.test(combined)) {
    pool = PHOTO_CATALOG.camping
  } else if (/family|parents|children|dining table|living room|gia đình|bữa cơm/.test(combined)) {
    pool = PHOTO_CATALOG.family
  } else if (/shopping|mall|boutique|fashion|retail|clothing rack|mua sắm/.test(combined)) {
    pool = PHOTO_CATALOG.shopping
  } else if (/concert|festival|musical|singing|music stage|âm nhạc|hòa nhạc/.test(combined)) {
    pool = PHOTO_CATALOG.music
  } else if (/farm|farmer|agriculture|cattle|pasture|rural|countryside|nông trại/.test(combined)) {
    pool = PHOTO_CATALOG.farm
  } else if (/science|chemist|biolog|physics|experiment|research lab|thí nghiệm/.test(combined)) {
    pool = PHOTO_CATALOG.science
  } else if (/cafe|coffee|latte|espresso|barista|quán cafe|cà phê/.test(combined)) {
    pool = PHOTO_CATALOG.cafe
  } else if (/airport|flight|airplane|terminal|boarding|departure|sân bay/.test(combined)) {
    pool = PHOTO_CATALOG.airport
  } else if (/portrait|businesswoman|executive|blazer|headshot|chân dung/.test(combined)) {
    pool = PHOTO_CATALOG.portrait
  } else if (/interview|candidate|hire|resume|cv|recruitment|phỏng vấn/.test(combined)) {
    pool = PHOTO_CATALOG.interview
  } else if (/meeting|coworking|colleague|workplace|corporat|văn phòng/.test(combined)) {
    pool = PHOTO_CATALOG.office
  } else if (/supermarket|grocery|market vendor|chợ|siêu thị/.test(combined)) {
    pool = PHOTO_CATALOG.market
  } else if (/library|hardcover book|reading hall|bookshelf|thư viện/.test(combined)) {
    pool = PHOTO_CATALOG.library
  } else if (/hospital|doctor|nurse|clinic|medical|patient|bệnh viện/.test(combined)) {
    pool = PHOTO_CATALOG.hospital
  } else if (/park pathway|garden lawn|botanical|công viên|vườn/.test(combined)) {
    pool = PHOTO_CATALOG.park
  } else if (/classroom|school|teach|student|lecture|lớp học|trường học/.test(combined)) {
    pool = PHOTO_CATALOG.classroom
  } else if (/restaurant|dining room|fine dining|meal course|nhà hàng/.test(combined)) {
    pool = PHOTO_CATALOG.restaurant
  } else if (/hotel resort|resort pool|hotel lobby|check-in|khách sạn/.test(combined)) {
    pool = PHOTO_CATALOG.hotel
  } else if (/technology|computer|software|coding|developer|artificial intelligence|công nghệ/.test(combined)) {
    pool = PHOTO_CATALOG.technology
  } else if (/kitchen|cooking|baking|chef|recipe|nhà bếp|nấu ăn/.test(combined)) {
    pool = PHOTO_CATALOG.kitchen
  } else if (/mountain|hiking trail|wilderness|thiên nhiên|núi rừng/.test(combined)) {
    pool = PHOTO_CATALOG.nature
  } else if (/fitness|gym|workout|weight training|tập gym/.test(combined)) {
    pool = PHOTO_CATALOG.fitness
  } else if (/artwork|art gallery|fine art|museum hall|triển lãm|bảo tàng/.test(combined)) {
    pool = PHOTO_CATALOG.art
  } else if (/city skyline|downtown skyscrapers|urban street|thành phố/.test(combined)) {
    pool = PHOTO_CATALOG.city
  }
  let hash = 0
  const str = `${topic}_${title}`
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i)
    hash |= 0
  }
  const idx = Math.abs(hash) % pool.length
  return pool[idx]
}

const getImageUrl = (url) => {
  if (!url) return '/logo-augusttrung.png'
  if (url.startsWith('http') || url.startsWith('data:')) return url
  const base = props.backendUrl?.replace(/\/$/, '') || 'https://agrse-fluent-english-backend.hf.space'
  return `${base}${url.startsWith('/') ? '' : '/'}${url}`
}

const currentScenarioImage = computed(() => {
  const rawUrl = currentScenario.value?.image_url
  if (imageFailed.value || !rawUrl || rawUrl.includes('pollinations.ai') || rawUrl.startsWith('data:image/svg')) {
    return resolveScenePhoto(currentScenario.value?.topic || '', currentScenario.value?.title || '')
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

const topicCategories = ['All', 'Workplace & Career', 'Healthcare & Services', 'Daily Life & Leisure', 'Travel & Transportation', 'Education & Science', 'Technology & Computing', 'Sports & Wellness', 'Arts & Culture']
const selectedCategory = ref('All')
const aiSuggestedTopics = ref([
  {
    id: 'zoo-wildlife',
    title: 'A Visit to the Zoo Wildlife Habitat',
    category: 'Daily Life & Leisure',
    level: 'Beginner',
    description: 'Observe tall giraffes, savanna enclosures, animal behaviors, and visitor interactions.',
    icon: 'mdi-paw'
  },
  {
    id: 'hospital-hallway',
    title: 'A Quiet Hospital Reception and Emergency Hallway',
    category: 'Healthcare & Services',
    level: 'Intermediate',
    description: 'Analyze medical facility architecture, emergency intake counters, and clinical atmosphere.',
    icon: 'mdi-hospital-building'
  },
  {
    id: 'medical-consult',
    title: 'A Medical Consultation in a Clinic Room',
    category: 'Healthcare & Services',
    level: 'Intermediate',
    description: 'Describe caring doctor-patient communication, clinical instruments, and healthcare dialogue.',
    icon: 'mdi-doctor'
  },
  {
    id: 'science-lab',
    title: 'A University Science Research Laboratory',
    category: 'Education & Science',
    level: 'Advanced',
    description: 'Explain experimental procedures, laboratory equipment, protective gear, and scientific inquiry.',
    icon: 'mdi-flask'
  },
  {
    id: 'job-interview',
    title: 'A Professional Job Interview Discussion',
    category: 'Workplace & Career',
    level: 'Intermediate',
    description: 'Describe candidate and interviewer interactions, corporate setting, and professional attire.',
    icon: 'mdi-account-tie'
  },
  {
    id: 'open-office',
    title: 'A Collaborative Team Meeting in an Open-Plan Office',
    category: 'Workplace & Career',
    level: 'Intermediate',
    description: 'Discuss project collaboration, modern open-plan workplace design, and team dynamics.',
    icon: 'mdi-briefcase-account'
  },
  {
    id: 'airport-terminal',
    title: 'A Modern International Airport Terminal',
    category: 'Travel & Transportation',
    level: 'Intermediate',
    description: 'Observe travelers with luggage, boarding gate procedures, and expansive glass architecture.',
    icon: 'mdi-airplane'
  },
  {
    id: 'urban-cafe',
    title: 'A Bustling Urban Coffee Shop',
    category: 'Daily Life & Leisure',
    level: 'Beginner',
    description: 'Describe cafe patrons, barista activities, cozy interior lighting, and social routines.',
    icon: 'mdi-coffee'
  },
  {
    id: 'farmers-market',
    title: 'A Vibrant Outdoor Farmers Market',
    category: 'Daily Life & Leisure',
    level: 'Beginner',
    description: 'Detail colorful fresh produce displays, vendor-customer transactions, and market atmosphere.',
    icon: 'mdi-storefront'
  },
  {
    id: 'university-library',
    title: 'A Grand University Library Study Hall',
    category: 'Education & Science',
    level: 'Intermediate',
    description: 'Focus on quiet academic study spaces, towering bookshelves, and focused learning habits.',
    icon: 'mdi-bookshelf'
  },
  {
    id: 'coding-workspace',
    title: 'A Software Developer Workspace with Code on Screen',
    category: 'Technology & Computing',
    level: 'Advanced',
    description: 'Discuss tech workstation setup, digital programming tasks, and focused workplace productivity.',
    icon: 'mdi-laptop'
  }
])
const isLoadingTopics = ref(false)

const selectCategory = (cat) => {
  selectedCategory.value = cat
}

const selectTopicItem = (item) => {
  scenarioTopic.value = item.title
  if (item.level) {
    if (item.level.toLowerCase().includes('upper') || item.level.toLowerCase().includes('advanced')) {
      scenarioLevel.value = 'Advanced'
    } else if (item.level.toLowerCase().includes('pre') || item.level.toLowerCase().includes('beginner')) {
      scenarioLevel.value = 'Beginner'
    } else {
      scenarioLevel.value = 'Intermediate'
    }
  }
}

const filteredSuggestedTopics = computed(() => {
  if (selectedCategory.value === 'All') return aiSuggestedTopics.value
  return aiSuggestedTopics.value.filter(t => t.category === selectedCategory.value)
})

const fetchSuggestedTopics = async () => {
  isLoadingTopics.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/picture-practice/suggest-topics`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category: selectedCategory.value === 'All' ? 'all' : selectedCategory.value, count: 12 })
    })
    if (res.ok) {
      const data = await res.json()
      if (data.topics && data.topics.length > 0) {
        aiSuggestedTopics.value = data.topics
      }
    }
  } catch (err) {
    console.warn('Failed to fetch suggested topics:', err)
  } finally {
    isLoadingTopics.value = false
  }
}

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
  fetchSuggestedTopics()
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
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
