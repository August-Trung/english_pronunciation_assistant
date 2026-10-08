<template>
  <v-container fluid class="pa-0 max-width-800">
    <!-- Header Banner -->
    <v-card border flat class="pa-3 pa-sm-4 mb-4 text-white rounded-lg" style="background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);">
      <div class="d-flex align-center justify-space-between flex-wrap ga-2">
        <div class="d-flex align-center ga-2 ga-sm-3">
          <v-avatar color="white" size="44" class="flex-shrink-0 elevation-1">
            <v-icon color="indigo-darken-3" size="default">mdi-cards-variant</v-icon>
          </v-avatar>
          <div>
            <div class="text-subtitle-1 text-sm-h6 font-weight-black tracking-tight leading-tight">
              VOCABULARY FLASHCARDS
            </div>
            <div class="text-caption text-indigo-lighten-4">
              Learn new words faster with picture illustrations and interactive pronunciation practice
            </div>
          </div>
        </div>

        <div class="d-flex align-center ga-2">
          <v-btn
            color="white"
            variant="flat"
            size="small"
            class="text-indigo-darken-3 font-weight-black text-none"
            prepend-icon="mdi-plus-circle"
            @click="showCreateModal = true"
          >
            Create AI Deck
          </v-btn>
        </div>
      </div>
    </v-card>

    <!-- Main Navigation Tabs -->
    <v-tabs v-model="activeTab" color="primary" align-tabs="start" class="mb-4 border-b">
      <v-tab value="ai-decks" class="font-weight-bold text-none">
        <v-icon start>mdi-sparkles</v-icon>
        AI Vocabulary Decks
        <v-chip size="x-small" color="primary" class="ml-2 font-weight-bold" variant="tonal">
          {{ decks.length }}
        </v-chip>
      </v-tab>
      <v-tab value="weak-words" class="font-weight-bold text-none">
        <v-icon start>mdi-alert-decagram-outline</v-icon>
        Weak Words SRS
        <v-chip size="x-small" color="deep-orange" class="ml-2 font-weight-bold" variant="tonal">
          {{ weakWords.length }}
        </v-chip>
      </v-tab>
    </v-tabs>

    <!-- ========================================== -->
    <!-- TAB 1: AI VOCABULARY DECKS -->
    <!-- ========================================== -->
    <div v-if="activeTab === 'ai-decks'">
      <!-- Loading Decks -->
      <div v-if="isLoadingDecks" class="text-center py-8">
        <v-progress-circular indeterminate color="primary" size="40" class="mb-2" />
        <div class="text-caption text-grey">Loading your smart flashcard decks...</div>
      </div>

      <!-- No Decks Empty State -->
      <div v-else-if="decks.length === 0 && !selectedDeck" class="text-center py-10 border rounded-lg bg-white pa-6">
        <v-avatar color="indigo-lighten-5" size="64" class="mb-3">
          <v-icon size="large" color="indigo">mdi-cards-outline</v-icon>
        </v-avatar>
        <div class="text-subtitle-1 font-weight-black text-grey-darken-4 mb-1">No AI Decks Created Yet</div>
        <div class="text-caption text-grey mb-4 max-width-500 mx-auto">
          Generate topic-focused decks instantly with Hugging Face AI. Each card includes native IPA phonetics, Vietnamese meanings, and visual illustrations.
        </div>
        <v-btn color="primary" variant="flat" class="text-none font-weight-bold" prepend-icon="mdi-sparkles" @click="showCreateModal = true">
          Generate Your First Deck
        </v-btn>
      </div>

      <!-- Deck Overview Grid (when not actively studying a deck) -->
      <div v-else-if="!selectedDeck">
        <div class="d-flex align-center justify-space-between mb-3">
          <div class="text-subtitle-2 font-weight-bold text-grey-darken-3">Your Study Decks ({{ decks.length }})</div>
          <v-btn size="x-small" variant="text" color="primary" prepend-icon="mdi-refresh" @click="fetchDecks">
            Refresh
          </v-btn>
        </div>

        <v-row dense>
          <v-col v-for="d in decks" :key="d.id" cols="12" sm="6">
            <v-card border flat class="pa-4 rounded-lg bg-white h-100 d-flex flex-column justify-space-between hover-card">
              <div>
                <div class="d-flex align-center justify-space-between mb-2">
                  <v-chip size="x-small" color="primary" variant="tonal" class="font-weight-bold text-uppercase">
                    {{ d.difficulty || 'Intermediate' }}
                  </v-chip>
                  <span class="text-caption text-grey">{{ formatDate(d.created_at) }}</span>
                </div>
                <div class="text-subtitle-1 font-weight-black text-grey-darken-4 mb-1">{{ d.title }}</div>
                <div class="text-caption text-grey-darken-1 mb-3">
                  <v-icon size="x-small" color="grey">mdi-tag-outline</v-icon> Topic: <strong>{{ d.topic }}</strong> &bull; {{ d.card_count || 0 }} Cards
                </div>
              </div>

              <div class="d-flex align-center justify-space-between pt-2 border-t mt-2">
                <v-btn
                  color="primary"
                  variant="flat"
                  size="small"
                  class="text-none font-weight-bold"
                  prepend-icon="mdi-play"
                  @click="startStudyDeck(d)"
                >
                  Study Deck
                </v-btn>
                <v-btn
                  color="error"
                  variant="text"
                  size="small"
                  icon="mdi-delete-outline"
                  title="Delete Deck"
                  @click="promptDeleteDeck(d)"
                />
              </div>
            </v-card>
          </v-col>
        </v-row>
      </div>

      <!-- Active Deck Study Studio -->
      <div v-else>
        <!-- Deck Header Navigation -->
        <div class="d-flex align-center justify-space-between mb-3">
          <div class="d-flex align-center ga-2">
            <v-btn size="small" variant="text" icon="mdi-arrow-left" @click="selectedDeck = null" />
            <div>
              <div class="text-subtitle-2 font-weight-black text-grey-darken-4 leading-tight">{{ selectedDeck.title }}</div>
              <div class="text-caption text-grey">Card {{ activeCardIndex + 1 }} of {{ activeCards.length }}</div>
            </div>
          </div>

          <div class="d-flex align-center ga-1">
            <v-btn size="x-small" variant="text" color="grey-darken-2" prepend-icon="mdi-shuffle" @click="shuffleDeck">
              Shuffle
            </v-btn>
            <v-btn size="x-small" variant="text" color="primary" prepend-icon="mdi-refresh" @click="activeCardIndex = 0; isAiFlipped = false">
              Restart
            </v-btn>
          </div>
        </div>

        <!-- 3D Multimodal Flip Card -->
        <div v-if="activeCard" class="multimodal-card mb-4" @click="isAiFlipped = !isAiFlipped">
          <div class="card-inner" :class="{ 'is-flipped': isAiFlipped }">
            <!-- Front Side -->
            <div class="card-face card-front pa-4 d-flex flex-column align-center justify-space-between">
              <div class="w-100 d-flex justify-space-between align-center text-caption text-grey mb-1">
                <v-chip size="x-small" color="primary" variant="flat">FRONT SIDE</v-chip>
                <span>Click card to reveal meaning & tips</span>
              </div>

              <!-- AI Visual Illustration -->
              <div class="image-container w-100 my-2 rounded-lg overflow-hidden position-relative border" @click.stop>
                <v-img
                  :src="activeCard.image_url || '/logo-augusttrung.png'"
                  height="200"
                  cover
                  class="bg-grey-lighten-4"
                >
                  <template #placeholder>
                    <div class="d-flex align-center justify-center fill-height">
                      <v-progress-circular indeterminate color="primary" size="32" />
                    </div>
                  </template>
                </v-img>
                <v-btn
                  size="x-small"
                  color="black"
                  variant="flat"
                  class="position-absolute bottom-0 right-0 ma-2 text-none font-weight-bold"
                  style="opacity: 0.85;"
                  prepend-icon="mdi-image-refresh"
                  :loading="isGeneratingImage"
                  @click="generateImageForActiveCard"
                >
                  Regenerate Visual
                </v-btn>
              </div>

              <!-- Word & Pronunciation -->
              <div class="text-center py-2">
                <div class="text-h4 font-weight-black text-grey-darken-4 mb-1">
                  {{ activeCard.word }}
                </div>
                <div class="text-subtitle-1 text-primary font-italic font-weight-bold mb-2">
                  /{{ activeCard.ipa || '...' }}/
                </div>
                <v-btn
                  color="indigo-darken-2"
                  variant="tonal"
                  size="small"
                  class="text-none font-weight-bold"
                  prepend-icon="mdi-volume-high"
                  @click.stop="playAudio(activeCard.word)"
                >
                  Listen Native Audio
                </v-btn>
              </div>

              <div class="text-caption text-grey mt-2">
                <v-icon size="x-small">mdi-swap-horizontal</v-icon> Click anywhere on the card to flip
              </div>
            </div>

            <!-- Back Side -->
            <div class="card-face card-back pa-4 d-flex flex-column justify-space-between" @click.stop>
              <div>
                <div class="d-flex justify-space-between align-center mb-2">
                  <v-chip size="x-small" color="secondary" variant="flat">BACK SIDE (DETAILS)</v-chip>
                  <v-btn size="x-small" variant="text" icon="mdi-close" @click="isAiFlipped = false" />
                </div>

                <div class="d-flex align-center justify-space-between mb-3 border-b pb-2">
                  <div>
                    <span class="text-h5 font-weight-black text-grey-darken-4">{{ activeCard.word }}</span>
                    <span class="text-subtitle-2 text-primary ml-2 font-italic">/{{ activeCard.ipa }}/</span>
                  </div>
                  <v-btn icon="mdi-volume-high" size="small" variant="text" color="primary" @click="playAudio(activeCard.word)" />
                </div>

                <!-- Vietnamese Meaning -->
                <div class="mb-3">
                  <div class="text-caption font-weight-black text-indigo-darken-3 mb-1">VIETNAMESE MEANING</div>
                  <div class="text-body-1 font-weight-bold text-grey-darken-4 bg-indigo-lighten-5 pa-2 rounded">
                    {{ activeCard.meaning || 'No definition available' }}
                  </div>
                </div>

                <!-- Example Sentence -->
                <div class="mb-3">
                  <div class="text-caption font-weight-black text-grey-darken-2 mb-1">PRACTICAL EXAMPLE</div>
                  <div class="text-body-2 text-grey-darken-3 font-italic bg-grey-lighten-4 pa-2 rounded border">
                    "{{ activeCard.example || 'Example context not set.' }}"
                  </div>
                </div>

                <!-- Pronunciation Tip -->
                <div class="mb-3" v-if="activeCard.pronunciation_tip">
                  <div class="text-caption font-weight-black text-deep-orange-darken-3 mb-1">PRONUNCIATION TIP (IPA & MOUTH SHAPE)</div>
                  <div class="text-caption text-grey-darken-4 bg-amber-lighten-5 border border-amber pa-2 rounded">
                    {{ activeCard.pronunciation_tip }}
                  </div>
                </div>
              </div>

              <!-- Quick Audio Practice on Card -->
              <div class="border-t pt-2 mt-2">
                <div class="d-flex align-center justify-space-between">
                  <v-btn
                    :color="isRecordingCard ? 'error' : 'primary'"
                    :variant="isRecordingCard ? 'flat' : 'outlined'"
                    size="small"
                    class="text-none font-weight-bold"
                    :prepend-icon="isRecordingCard ? 'mdi-stop' : 'mdi-microphone'"
                    :loading="isEvaluatingCard"
                    @click="toggleCardRecording"
                  >
                    {{ isRecordingCard ? 'Stop & Grade Speaking' : 'Test Your Pronunciation' }}
                  </v-btn>

                  <div v-if="cardScore !== null" class="d-flex align-center ga-1">
                    <span class="text-caption font-weight-bold">Score:</span>
                    <v-chip :color="cardScore >= 80 ? 'success' : 'warning'" size="small" class="font-weight-black">
                      {{ cardScore }}%
                    </v-chip>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Navigation Controls Below Card -->
        <div class="d-flex align-center justify-space-between ga-2">
          <v-btn
            variant="tonal"
            color="grey-darken-2"
            size="small"
            class="text-none flex-grow-1 font-weight-bold"
            prepend-icon="mdi-chevron-left"
            :disabled="activeCardIndex === 0"
            @click="prevCard"
          >
            Previous Card
          </v-btn>

          <v-btn
            variant="flat"
            color="primary"
            size="small"
            class="text-none flex-grow-1 font-weight-bold"
            append-icon="mdi-chevron-right"
            :disabled="activeCardIndex >= activeCards.length - 1"
            @click="nextCard"
          >
            Next Card
          </v-btn>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- TAB 2: WEAK WORDS SRS (ORIGINAL LOGIC PRESERVED) -->
    <!-- ========================================== -->
    <div v-else-if="activeTab === 'weak-words'">
      <!-- AI Smart Remedial Practice Banner -->
      <v-card border flat class="pa-3 pa-sm-4 mb-4 bg-indigo-lighten-5 border-indigo rounded-lg">
        <div class="d-flex align-center justify-space-between flex-wrap ga-3">
          <div class="d-flex align-center ga-3">
            <v-avatar color="indigo" size="44" class="elevation-1">
              <v-icon color="white">mdi-auto-fix</v-icon>
            </v-avatar>
            <div>
              <div class="text-subtitle-1 font-weight-black text-indigo-darken-3">AI Smart Remedial Practice</div>
              <div class="text-caption text-indigo-darken-2 font-weight-bold">
                1-Click generate custom reading exercises based on your top mispronounced words
              </div>
            </div>
          </div>

          <v-btn
            color="indigo-darken-3"
            variant="flat"
            size="small"
            class="font-weight-black text-none"
            prepend-icon="mdi-flash"
            :loading="isLoadingRemedial"
            @click="startRemedialPractice"
          >
            Start AI Practice Set
          </v-btn>
        </div>
      </v-card>

      <!-- Empty State -->
      <div v-if="weakWords.length === 0" class="text-center py-8 border rounded-lg bg-white pa-4">
        <v-avatar color="green-lighten-5" size="64" class="mb-3">
          <v-icon size="large" color="success">mdi-checkbox-marked-circle-outline</v-icon>
        </v-avatar>
        <div class="text-subtitle-1 font-weight-black text-grey-darken-4 mb-1">Excellent! No Weak Words Found!</div>
        <div class="text-caption text-grey mb-4">Keep up your outstanding pronunciation practice across all speaking lessons.</div>
        <v-btn to="/" color="primary" variant="flat" class="text-none" prepend-icon="mdi-microphone">
          Go to Speaking Studio
        </v-btn>
      </div>

      <!-- Active Weak Words Flashcard -->
      <div v-else>
        <div class="d-flex align-center justify-space-between mb-2">
          <span class="text-caption text-grey-darken-2">Card {{ currentCardIndex + 1 }} / {{ weakWords.length }}</span>
          <v-btn size="x-small" variant="text" color="grey-darken-2" prepend-icon="mdi-refresh" @click="resetIndex">
            Restart Deck
          </v-btn>
        </div>

        <div
          class="flashcard-box pa-6 rounded-lg text-center cursor-pointer border mb-4 position-relative"
          :class="isFlipped ? 'bg-amber-lighten-5 border-amber' : 'bg-white'"
          @click="isFlipped = !isFlipped"
        >
          <div class="text-caption text-grey-darken-1 mb-2">
            {{ isFlipped ? 'BACK SIDE (IPA & NATIVE AUDIO)' : 'FRONT SIDE (CLICK CARD TO FLIP)' }}
          </div>

          <!-- Front Side -->
          <div v-if="!isFlipped" class="py-6">
            <div class="text-h4 font-weight-black text-grey-darken-4 mb-2">
              {{ currentCard.word }}
            </div>
            <div class="text-caption text-deep-orange font-weight-bold">
              Imperfect Attempts: {{ currentCard.error_count || 1 }} times
            </div>
          </div>

          <!-- Back Side -->
          <div v-else class="py-3">
            <div class="text-h4 font-weight-black text-grey-darken-4 mb-1">
              {{ currentCard.word }}
            </div>
            <div class="text-subtitle-2 text-primary font-italic mb-2">
              /{{ currentCard.ipa || '...' }}/
            </div>
            <div class="text-body-2 text-grey-darken-3 mb-4">
              Meaning: {{ currentCard.meaning || 'Practice target word' }}
            </div>

            <v-btn
              color="deep-orange"
              variant="tonal"
              size="small"
              class="text-none mb-2"
              prepend-icon="mdi-volume-high"
              @click.stop="playAudio(currentCard.word)"
            >
              Listen Native Pronunciation
            </v-btn>
          </div>

          <div class="text-caption text-grey position-absolute bottom-0 right-0 pa-2" style="font-size: 10px;">
            <v-icon size="x-small">mdi-swap-horizontal</v-icon> Click card to flip
          </div>
        </div>

        <!-- Action Control Buttons -->
        <div class="d-flex align-center justify-space-between ga-2">
          <v-btn
            color="error"
            variant="tonal"
            size="small"
            class="text-none flex-grow-1 font-weight-bold"
            prepend-icon="mdi-close-circle-outline"
            @click="markRetry"
          >
            Need Practice (Keep)
          </v-btn>

          <v-btn
            color="success"
            variant="tonal"
            size="small"
            class="text-none flex-grow-1 font-weight-bold"
            prepend-icon="mdi-check-circle-outline"
            @click="markMastered"
          >
            Mastered (Remove)
          </v-btn>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- DIALOG: GENERATE AI DECK MODAL -->
    <!-- ========================================== -->
    <v-dialog v-model="showCreateModal" max-width="560">
      <v-card border rounded="lg" class="pa-4 bg-white">
        <div class="d-flex align-center justify-space-between mb-3 border-b pb-2">
          <div class="d-flex align-center ga-2">
            <v-avatar color="primary-lighten-5" size="36">
              <v-icon color="primary">mdi-sparkles</v-icon>
            </v-avatar>
            <div class="text-subtitle-1 font-weight-black text-grey-darken-4">Generate AI Flashcard Deck</div>
          </div>
          <v-btn icon="mdi-close" variant="text" size="small" @click="showCreateModal = false" />
        </div>

        <div class="text-caption text-grey-darken-1 mb-3">
          Enter any topic to automatically create a custom vocabulary study deck with phonetic guide, meanings, and practical sentences.
        </div>

        <v-text-field
          v-model="deckForm.topic"
          label="Deck Topic / Subject"
          placeholder="e.g. IELTS Environment, Airport Travel, Job Interview..."
          variant="outlined"
          density="comfortable"
          class="mb-2"
          prepend-inner-icon="mdi-format-title"
          :error-messages="formError"
        />

        <!-- Quick Topic Chips -->
        <div class="mb-3">
          <div class="text-caption font-weight-bold text-grey mb-1">Quick Suggestions:</div>
          <div class="d-flex flex-wrap ga-1">
            <v-chip
              v-for="s in suggestedTopics"
              :key="s"
              size="x-small"
              variant="tonal"
              color="indigo"
              class="cursor-pointer font-weight-bold"
              @click="deckForm.topic = s"
            >
              {{ s }}
            </v-chip>
          </div>
        </div>

        <v-row dense class="mb-2">
          <v-col cols="6">
            <v-select
              v-model="deckForm.difficulty"
              :items="['Beginner', 'Intermediate', 'Advanced']"
              label="Proficiency Level"
              variant="outlined"
              density="comfortable"
            />
          </v-col>
          <v-col cols="6">
            <v-select
              v-model="deckForm.count"
              :items="[5, 8, 10]"
              label="Number of Cards"
              variant="outlined"
              density="comfortable"
            />
          </v-col>
        </v-row>

        <v-checkbox
          v-model="deckForm.generateImages"
          label="Include illustration pictures for cards"
          color="primary"
          density="compact"
          hide-details
          class="mb-3"
        />

        <v-card-actions class="px-0 pb-0 pt-2 border-t">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showCreateModal = false">Cancel</v-btn>
          <v-btn
            color="primary"
            variant="flat"
            class="text-none font-weight-bold"
            prepend-icon="mdi-auto-fix"
            :loading="isGeneratingDeck"
            @click="handleCreateDeck"
          >
            Generate Deck
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ========================================== -->
    <!-- DIALOG: CONFIRM DELETE DECK (MANDATORY RULE) -->
    <!-- ========================================== -->
    <v-dialog v-model="showDeleteConfirm" max-width="400">
      <v-card border rounded="lg" class="pa-4 bg-white">
        <div class="text-center mb-3">
          <v-avatar color="error-lighten-5" size="56" class="mb-2">
            <v-icon color="error" size="large">mdi-alert-octagon-outline</v-icon>
          </v-avatar>
          <div class="text-subtitle-1 font-weight-black text-grey-darken-4">Delete Flashcard Deck?</div>
          <div class="text-caption text-grey mt-1" v-if="deckToDelete">
            Are you sure you want to delete deck <strong>"{{ deckToDelete.title }}"</strong>? This action cannot be undone.
          </div>
        </div>

        <v-card-actions class="px-0 pb-0 justify-center ga-2">
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showDeleteConfirm = false">Cancel</v-btn>
          <v-btn color="error" variant="flat" class="text-none font-weight-bold" :loading="isDeletingDeck" @click="confirmDeleteDeck">
            Yes, Delete Deck
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Modal: AI Remedial Practice Modal -->
    <v-dialog v-model="showRemedialModal" max-width="550">
      <v-card border rounded="lg" class="pa-4 bg-white" v-if="remedialData">
        <div class="d-flex align-center ga-3 mb-3">
          <v-avatar color="indigo-lighten-5" size="40" class="text-indigo-darken-3 border">
            <v-icon size="default">mdi-brain</v-icon>
          </v-avatar>
          <div>
            <div class="text-subtitle-1 font-weight-black text-primary">{{ remedialData.title }}</div>
            <div class="text-caption text-grey-darken-1">{{ remedialData.reason }}</div>
          </div>
        </div>

        <v-card border flat class="pa-3 mb-3 bg-grey-lighten-4 rounded-lg">
          <div class="text-caption font-weight-black text-secondary mb-1">SMART REMEDIAL SENTENCE:</div>
          <div class="text-body-1 font-weight-black text-grey-darken-4 mb-2">
            "{{ remedialData.topic_sentence }}"
          </div>
          <div class="text-caption text-primary font-weight-bold">
            IPA Target: {{ remedialData.target_ipa }}
          </div>
        </v-card>

        <div class="text-caption font-weight-black text-grey-darken-2 mb-2">FOCUS WEAK WORDS:</div>
        <div class="d-flex align-center flex-wrap ga-1 mb-4">
          <v-chip v-for="w in (remedialData.focus_words || [])" :key="w" color="deep-orange" size="small" variant="flat" class="font-weight-bold">
            {{ w }}
          </v-chip>
        </div>

        <v-card-actions class="px-0 pb-0">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showRemedialModal = false">Close</v-btn>
          <v-btn color="indigo-darken-3" variant="flat" class="text-none font-weight-bold" prepend-icon="mdi-headphones" @click="playAudio(remedialData.topic_sentence)">
            Listen Sample
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

const activeTab = ref('ai-decks')
const decks = ref([])
const isLoadingDecks = ref(false)
const selectedDeck = ref(null)
const activeCards = ref([])
const activeCardIndex = ref(0)
const isAiFlipped = ref(false)

const showCreateModal = ref(false)
const isGeneratingDeck = ref(false)
const isGeneratingImage = ref(false)
const formError = ref('')

const showDeleteConfirm = ref(false)
const deckToDelete = ref(null)
const isDeletingDeck = ref(false)

const isRecordingCard = ref(false)
const isEvaluatingCard = ref(false)
const cardScore = ref(null)
let mediaRecorder = null
let audioChunks = []

const suggestedTopics = [
  'IELTS Environment & Climate',
  'Airport & International Travel',
  'Academic Job Interview',
  'Technology & Artificial Intelligence',
  'Business Negotiation'
]

const deckForm = ref({
  topic: '',
  difficulty: 'Intermediate',
  count: 5,
  generateImages: true
})

// Weak words original states
const weakWords = ref([])
const isLoadingRemedial = ref(false)
const showRemedialModal = ref(false)
const remedialData = ref(null)
const currentCardIndex = ref(0)
const isFlipped = ref(false)

const activeCard = computed(() => activeCards.value[activeCardIndex.value] || null)
const currentCard = computed(() => weakWords.value[currentCardIndex.value] || {})

const formatDate = (isoStr) => {
  if (!isoStr) return 'Recently'
  try {
    const d = new Date(isoStr)
    return d.toLocaleDateString()
  } catch {
    return 'Recently'
  }
}

// Fetch user decks from backend
const fetchDecks = async () => {
  isLoadingDecks.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/flashcards/decks?user_id=${props.userId || 1}`)
    if (res.ok) {
      const data = await res.json()
      decks.value = data.decks || []
    }
  } catch (err) {
    console.error('Failed to fetch decks:', err)
  } finally {
    isLoadingDecks.value = false
  }
}

const startStudyDeck = async (deck) => {
  try {
    const res = await fetch(`${props.backendUrl}/api/flashcards/decks/${deck.id}`)
    if (res.ok) {
      const data = await res.json()
      selectedDeck.value = data.deck
      activeCards.value = data.cards || []
      activeCardIndex.value = 0
      isAiFlipped.value = false
      cardScore.value = null
    }
  } catch (e) {
    console.error('Failed to load deck cards:', e)
  }
}

const shuffleDeck = () => {
  activeCards.value = [...activeCards.value].sort(() => Math.random() - 0.5)
  activeCardIndex.value = 0
  isAiFlipped.value = false
}

const nextCard = () => {
  if (activeCardIndex.value < activeCards.value.length - 1) {
    activeCardIndex.value++
    isAiFlipped.value = false
    cardScore.value = null
  }
}

const prevCard = () => {
  if (activeCardIndex.value > 0) {
    activeCardIndex.value--
    isAiFlipped.value = false
    cardScore.value = null
  }
}

// Generate new AI deck
const handleCreateDeck = async () => {
  if (!deckForm.value.topic.trim()) {
    formError.value = 'Please provide a topic name'
    return
  }
  formError.value = ''
  isGeneratingDeck.value = true

  try {
    // 1. Generate cards from LLM
    const genRes = await fetch(`${props.backendUrl}/api/flashcards/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: deckForm.value.topic,
        difficulty: deckForm.value.difficulty.toLowerCase(),
        count: deckForm.value.count
      })
    })

    if (!genRes.ok) throw new Error('Generation failed')
    const genData = await genRes.json()
    const cards = genData.data || []

    // 2. If generateImages checked, generate image for first card immediately
    if (deckForm.value.generateImages && cards.length > 0) {
      try {
        const imgRes = await fetch(`${props.backendUrl}/api/ai/generate-image`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ word: cards[0].word, context: deckForm.value.topic })
        })
        if (imgRes.ok) {
          const imgData = await imgRes.json()
          cards[0].image_url = imgData.image_url
        }
      } catch (imgErr) {
        console.warn('Initial image generation error:', imgErr)
      }
    }

    // 3. Save deck to DB
    const saveRes = await fetch(`${props.backendUrl}/api/flashcards/decks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: props.userId || 1,
        title: deckForm.value.topic,
        topic: deckForm.value.topic,
        difficulty: deckForm.value.difficulty,
        cards: cards
      })
    })

    if (saveRes.ok) {
      const saveData = await saveRes.json()
      showCreateModal.value = false
      deckForm.value.topic = ''
      await fetchDecks()
      // Open deck directly
      const createdDeck = decks.value.find(d => d.id === saveData.deck_id)
      if (createdDeck) {
        startStudyDeck(createdDeck)
      }
    }
  } catch (err) {
    formError.value = 'Failed to generate deck. Please try again.'
  } finally {
    isGeneratingDeck.value = false
  }
}

// Regenerate visual for active card
const generateImageForActiveCard = async () => {
  if (!activeCard.value) return
  isGeneratingImage.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/ai/generate-image`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        word: activeCard.value.word,
        context: selectedDeck.value?.topic || '',
        card_id: activeCard.value.id
      })
    })
    if (res.ok) {
      const data = await res.json()
      activeCard.value.image_url = data.image_url
    }
  } catch (err) {
    console.error('Image regeneration failed:', err)
  } finally {
    isGeneratingImage.value = false
  }
}

// Prompt & Confirm Delete Deck
const promptDeleteDeck = (deck) => {
  deckToDelete.value = deck
  showDeleteConfirm.value = true
}

const confirmDeleteDeck = async () => {
  if (!deckToDelete.value) return
  isDeletingDeck.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/flashcards/decks/${deckToDelete.value.id}`, {
      method: 'DELETE'
    })
    if (res.ok) {
      showDeleteConfirm.value = false
      if (selectedDeck.value?.id === deckToDelete.value.id) {
        selectedDeck.value = null
      }
      deckToDelete.value = null
      await fetchDecks()
    }
  } catch (err) {
    console.error('Failed to delete deck:', err)
  } finally {
    isDeletingDeck.value = false
  }
}

// Pronunciation test directly on card
const toggleCardRecording = async () => {
  if (isRecordingCard.value) {
    // Stop recording
    mediaRecorder?.stop()
    isRecordingCard.value = false
  } else {
    // Start recording
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      audioChunks = []
      mediaRecorder = new MediaRecorder(stream)
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.push(e.data)
      }
      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop())
        await evaluateCardAudio()
      }
      mediaRecorder.start()
      isRecordingCard.value = true
    } catch (e) {
      alert('Microphone access denied or unavailable.')
    }
  }
}

const evaluateCardAudio = async () => {
  if (audioChunks.length === 0 || !activeCard.value) return
  isEvaluatingCard.value = true
  try {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.webm')
    formData.append('topic_sentence', activeCard.value.word)
    formData.append('user_id', props.userId || 1)

    const res = await fetch(`${props.backendUrl}/api/assess_pronunciation`, {
      method: 'POST',
      body: formData
    })
    if (res.ok) {
      const data = await res.json()
      cardScore.value = Math.round(data.overall_score || data.score || 85)
    }
  } catch (err) {
    console.error('Evaluation error:', err)
  } finally {
    isEvaluatingCard.value = false
  }
}

// Audio Player via Web Speech API
const playAudio = (text) => {
  if (!text) return
  window.speechSynthesis?.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'en-US'
  window.speechSynthesis?.speak(utterance)
}

// Weak Words Methods (Preserved)
const fetchWeakWords = async () => {
  try {
    const res = await fetch(`${props.backendUrl}/api/weak-words?user_id=${props.userId || 1}`)
    if (res.ok) {
      const data = await res.json()
      weakWords.value = data.weak_words ?? []
    }
  } catch {}
}

const startRemedialPractice = async () => {
  isLoadingRemedial.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/practice/recommended/${props.userId || 1}`)
    if (res.ok) {
      const data = await res.json()
      if (data.recommendations?.[0]) {
        remedialData.value = data.recommendations[0]
        showRemedialModal.value = true
      }
    }
  } catch (e) {
    console.error('Fetch remedial practice error:', e)
  } finally {
    isLoadingRemedial.value = false
  }
}

const resetIndex = () => {
  currentCardIndex.value = 0
  isFlipped.value = false
}

const markRetry = () => {
  isFlipped.value = false
  currentCardIndex.value = (currentCardIndex.value + 1) % weakWords.value.length
}

const markMastered = async () => {
  const wordToRemove = currentCard.value.word
  weakWords.value = weakWords.value.filter(w => w.word !== wordToRemove)
  isFlipped.value = false
  if (currentCardIndex.value >= weakWords.value.length) {
    currentCardIndex.value = 0
  }

  try {
    await fetch(`${props.backendUrl}/api/weak-words/remove`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: props.userId || 1, word: wordToRemove })
    })
  } catch {}
}

onMounted(() => {
  fetchDecks()
  fetchWeakWords()
})
</script>

<style scoped>
.max-width-800 {
  max-width: 800px;
  margin: 0 auto;
}

.max-width-500 {
  max-width: 500px;
}

.hover-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.hover-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* 3D Flip Card Styles */
.multimodal-card {
  perspective: 1000px;
  min-height: 480px;
  cursor: pointer;
}

.card-inner {
  position: relative;
  width: 100%;
  min-height: 480px;
  text-align: left;
  transition: transform 0.6s cubic-bezier(0.4, 0.2, 0.2, 1);
  transform-style: preserve-3d;
}

.card-inner.is-flipped {
  transform: rotateY(180deg);
}

.card-face {
  position: absolute;
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  background: white;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
}

.card-front {
  background: #FFFFFF;
}

.card-back {
  background: #FAFAFA;
  transform: rotateY(180deg);
}

.image-container {
  max-height: 220px;
}

.flashcard-box {
  min-height: 160px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style>
