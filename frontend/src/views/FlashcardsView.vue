<template>
  <div class="space-y-4">
    <!-- HERO FLASHCARD HEADER -->
    <v-card flat border rounded="2xl" class="pa-4 pa-md-5 bg-white border-slate-200/80 shadow-sm">
      <div class="d-flex align-center justify-space-between flex-wrap ga-3">
        <div class="d-flex align-center ga-2.5">
          <v-avatar color="amber-lighten-5" size="40" class="border border-amber-200">
            <v-icon color="amber-darken-3" size="22">mdi-cards-outline</v-icon>
          </v-avatar>
          <div>
            <div class="text-subtitle-1 font-weight-black text-slate-800">Bộ Thẻ Bài Từ Vựng 3D Studio</div>
            <div class="text-caption font-weight-medium text-slate-500" style="font-size: 11px;">Lật thẻ và ôn tập phát âm từ vựng</div>
          </div>
        </div>

        <div class="d-flex align-center ga-2">
          <v-chip color="amber-darken-3" size="small" variant="flat" class="font-weight-black">
            <v-icon start size="x-small">mdi-cards-sharp</v-icon>
            {{ currentIndex + 1 }}/{{ cards.length }} Thẻ
          </v-chip>
        </div>
      </div>
    </v-card>

    <!-- 3D FLIP CARD STUDIO STAGE -->
    <v-card flat border rounded="2xl" class="pa-6 text-center bg-white border-slate-200/80 shadow-sm relative overflow-hidden">
      <div class="max-w-sm mx-auto">
        <!-- 3D Card Container -->
        <div
          class="relative w-100 cursor-pointer perspective-1000 my-4"
          style="min-height: 280px;"
          @click="isFlipped = !isFlipped"
        >
          <!-- CARD FRONT -->
          <div
            v-if="!isFlipped"
            class="pa-6 bg-slate-50 rounded-2xl border-2 border-sky-200 shadow-md d-flex flex-column align-center justify-center h-100 transition-all hover:scale-102"
          >
            <v-chip size="x-small" color="sky-darken-2" variant="tonal" class="font-weight-black mb-3">
              {{ currentCard.type || 'Noun' }}
            </v-chip>
            <div class="text-h4 font-weight-black text-slate-800 mb-2">
              {{ currentCard.word }}
            </div>
            <div class="text-subtitle-2 font-weight-bold text-sky-darken-3 font-mono mb-4">
              {{ currentCard.ipa }}
            </div>
            <div class="text-caption text-slate-400 font-weight-bold d-flex align-center ga-1" style="font-size: 10.5px;">
              <v-icon size="x-small" color="slate-400">mdi-gesture-tap</v-icon>
              Chạm để lật mặt sau
            </div>
          </div>

          <!-- CARD BACK -->
          <div
            v-else
            class="pa-6 bg-sky-lighten-5 rounded-2xl border-2 border-sky-300 shadow-md d-flex flex-column align-center justify-center h-100 transition-all"
          >
            <div class="text-caption font-weight-black text-sky-darken-4 uppercase tracking-wider mb-1">Nghĩa Tiếng Việt:</div>
            <div class="text-h5 font-weight-black text-sky-darken-4 mb-3">
              {{ currentCard.meaning }}
            </div>
            <div class="text-caption font-weight-medium text-slate-700 pa-2 bg-white rounded-lg border border-sky-100 mb-4" style="font-size: 11.5px;">
              "{{ currentCard.example }}"
            </div>
            <v-btn size="small" color="sky-darken-2" variant="flat" class="font-weight-black text-none rounded-lg" prepend-icon="mdi-volume-high" @click.stop="speakWord(currentCard.word)">
              Nghe phát âm
            </v-btn>
          </div>
        </div>

        <!-- SWIPE ACTION BUTTONS -->
        <div class="d-flex justify-center ga-4 mt-4">
          <v-btn
            color="error"
            size="large"
            variant="tonal"
            class="font-weight-black text-none px-5 rounded-xl"
            prepend-icon="mdi-refresh"
            @click="prevCard"
          >
            Chưa Thuộc
          </v-btn>

          <v-btn
            color="success"
            size="large"
            variant="flat"
            class="font-weight-black text-none px-6 rounded-xl shadow-md"
            prepend-icon="mdi-check-circle"
            @click="nextCard"
          >
            Đã Thuộc
          </v-btn>
        </div>
      </div>
    </v-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const currentIndex = ref(0)
const isFlipped = ref(false)

const cards = ref([
  { word: 'Perfection', ipa: '/pərˈfɛkʃən/', type: 'Noun', meaning: 'Sự hoàn hảo, sự hoàn thiện', example: 'Practice makes perfection.' },
  { word: 'Courage', ipa: '/ˈkɜrɪdʒ/', type: 'Noun', meaning: 'Dũng khí, sự can đảm', example: 'It takes courage to continue.' },
  { word: 'Success', ipa: '/səkˈsɛs/', type: 'Noun', meaning: 'Sự thành công', example: 'Success is a continuous journey.' },
  { word: 'Fluency', ipa: '/ˈfluənsi/', type: 'Noun', meaning: 'Sự trôi chảy, sự mượt mà', example: 'Aim for fluency in speaking.' },
])

const currentCard = computed(() => cards.value[currentIndex.value] || cards.value[0])

const nextCard = () => {
  isFlipped.value = false
  currentIndex.value = (currentIndex.value + 1) % cards.value.length
}

const prevCard = () => {
  isFlipped.value = false
  currentIndex.value = (currentIndex.value - 1 + cards.value.length) % cards.value.length
}

const speakWord = (word) => {
  if (!('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(word)
  u.lang = 'en-US'
  window.speechSynthesis.speak(u)
}
</script>
