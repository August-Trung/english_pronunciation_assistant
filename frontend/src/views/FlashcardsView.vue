<template>
  <v-container fluid class="pa-0 max-width-700">
    <!-- Header Banner -->
    <v-card border flat class="pa-3 pa-sm-4 mb-4 text-white rounded-lg" style="background: linear-gradient(135deg, #FF6F00 0%, #E65100 100%);">
      <div class="d-flex align-center justify-space-between flex-wrap ga-2">
        <div class="d-flex align-center ga-2 ga-sm-3">
          <v-avatar color="amber-lighten-4" size="40" class="flex-shrink-0">
            <v-icon color="deep-orange-darken-4" size="default">mdi-cards-outline</v-icon>
          </v-avatar>
          <div>
            <div class="text-subtitle-1 text-sm-h6 font-weight-black tracking-tight leading-tight">WEAK WORDS FLASHCARDS</div>
            <div class="text-caption text-amber-lighten-4">Review words with dropped consonants or mispronounced phonetics for SRS retention</div>
          </div>
        </div>

        <v-chip label variant="tonal" color="amber-lighten-4" size="small">
          {{ weakWords.length }} Review Words
        </v-chip>
      </div>
    </v-card>

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

    <!-- Active Flashcard Studio -->
    <div v-else>
      <div class="d-flex align-center justify-space-between mb-2">
        <span class="text-caption text-grey-darken-2">Card {{ currentCardIndex + 1 }} / {{ weakWords.length }}</span>
        <v-btn size="x-small" variant="text" color="grey-darken-2" prepend-icon="mdi-refresh" @click="resetIndex">
          Restart Deck
        </v-btn>
      </div>

      <!-- Flashcard Item (Flip Effect) -->
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
          class="text-none flex-grow-1"
          prepend-icon="mdi-close-circle-outline"
          @click="markRetry"
        >
          Need Practice (Keep)
        </v-btn>

        <v-btn
          color="success"
          variant="tonal"
          size="small"
          class="text-none flex-grow-1"
          prepend-icon="mdi-check-circle-outline"
          @click="markMastered"
        >
          Mastered (Remove)
        </v-btn>
      </div>
    </div>
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

const weakWords = ref([])
const isLoadingRemedial = ref(false)
const showRemedialModal = ref(false)
const remedialData = ref(null)

const currentCardIndex = ref(0)
const isFlipped = ref(false)

const currentCard = computed(() => weakWords.value[currentCardIndex.value] || {})

const fetchWeakWords = async () => {
  try {
    const res = await fetch(`${props.backendUrl}/api/weak-words?user_id=${props.userId || 1}`)
    if (res.ok) {
      const data = await res.json()
      if (data.weak_words && Array.isArray(data.weak_words) && data.weak_words.length > 0) {
        weakWords.value = data.weak_words
      }
    }
  } catch (e) {
    // Graceful silent fallback
  }
}

const startRemedialPractice = async () => {
  isLoadingRemedial.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/practice/recommended/${props.userId || 1}`)
    if (res.ok) {
      const data = await res.json()
      if (data.recommendations && data.recommendations.length > 0) {
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

const playAudio = (word) => {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(word)
    utterance.lang = 'en-US'
    window.speechSynthesis.speak(utterance)
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
  } catch (e) {}
}

onMounted(() => {
  fetchWeakWords()
})
</script>

<style scoped>
.max-width-700 {
  max-width: 700px;
  margin: 0 auto;
}

.flashcard-box {
  min-height: 140px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: all 0.2s ease;
}
</style>
