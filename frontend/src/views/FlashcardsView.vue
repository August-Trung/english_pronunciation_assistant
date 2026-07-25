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
            <div class="text-subtitle-1 text-sm-h6 font-weight-black tracking-tight leading-tight">ÔN TỪ KHÓ (FLASHCARD SRS)</div>
            <div class="text-caption text-amber-lighten-4">Luyện tập các từ phát âm thiếu hoặc sai để ghi nhớ lâu dài</div>
          </div>
        </div>

        <v-chip label variant="tonal" color="amber-lighten-4" size="small">
          {{ weakWords.length }} từ cần ôn
        </v-chip>
      </div>
    </v-card>

    <!-- Empty State -->
    <div v-if="weakWords.length === 0" class="text-center py-8 border rounded-lg bg-white pa-4">
      <v-avatar color="green-lighten-5" size="64" class="mb-3">
        <v-icon size="large" color="success">mdi-checkbox-marked-circle-outline</v-icon>
      </v-avatar>
      <div class="text-subtitle-1 font-weight-black text-grey-darken-4 mb-1">Tuyệt vời! Em chưa có từ phát âm sai nào!</div>
      <div class="text-caption text-grey mb-4">Hãy tiếp tục duy trì phong độ qua các bài luyện đọc và phát âm nhé.</div>
      <v-btn to="/" color="primary" variant="flat" class="text-none">
        Đến trang Luyện nói ngay
      </v-btn>
    </div>

    <!-- Active Flashcard Studio -->
    <div v-else>
      <div class="d-flex align-center justify-space-between mb-2">
        <span class="text-caption text-grey-darken-2">Thẻ {{ currentCardIndex + 1 }} / {{ weakWords.length }}</span>
        <v-btn size="x-small" variant="text" color="grey-darken-2" prepend-icon="mdi-refresh" @click="resetIndex">
          Bắt đầu lại
        </v-btn>
      </div>

      <!-- Flashcard Item (Flip Effect) -->
      <div
        class="flashcard-box pa-6 rounded-lg text-center cursor-pointer border mb-4 position-relative"
        :class="isFlipped ? 'bg-amber-lighten-5 border-amber' : 'bg-white'"
        @click="isFlipped = !isFlipped"
      >
        <div class="text-caption text-grey-darken-1 mb-2">
          {{ isFlipped ? 'MẶT SAU (CHI TIẾT & PHÁT ÂM)' : 'MẶT TRƯỚC (BẤM ĐỂ LẬT THẺ)' }}
        </div>

        <!-- Front Side -->
        <div v-if="!isFlipped" class="py-6">
          <div class="text-h4 font-weight-black text-grey-darken-4 mb-2">
            {{ currentCard.word }}
          </div>
          <div class="text-caption text-deep-orange font-weight-bold">
            Số lần đọc chưa chuẩn: {{ currentCard.error_count || 1 }} lần
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
            Nghĩa: {{ currentCard.meaning || 'Từ cần luyện tập lại' }}
          </div>

          <v-btn
            color="deep-orange"
            variant="tonal"
            size="small"
            class="text-none mb-2"
            prepend-icon="mdi-volume-high"
            @click.stop="playAudio(currentCard.word)"
          >
            Nghe phát âm chuẩn
          </v-btn>
        </div>

        <div class="text-caption text-grey position-absolute bottom-0 right-0 pa-2" style="font-size: 10px;">
          <v-icon size="x-small">mdi-swap-horizontal</v-icon> Bấm vào thẻ để lật
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
          Chưa nhớ (Ôn lại)
        </v-btn>

        <v-btn
          color="success"
          variant="tonal"
          size="small"
          class="text-none flex-grow-1"
          prepend-icon="mdi-check-circle-outline"
          @click="markMastered"
        >
          Đã thuộc (Xóa từ)
        </v-btn>
      </div>
    </div>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  backendUrl: String,
  userId: Number
})

const weakWords = ref([
  { word: "Schedule", ipa: "ˈʃɛdjuːl", meaning: "Lịch trình, thời khóa biểu", error_count: 3 },
  { word: "Comfortable", ipa: "ˈkʌmfətəbl", meaning: "Thoải mái, dễ chịu", error_count: 2 },
  { word: "Pronunciation", ipa: "prəˌnʌnsiˈeɪʃn", meaning: "Sự phát âm", error_count: 4 }
])

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
    // Graceful silent fallback without console error
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
