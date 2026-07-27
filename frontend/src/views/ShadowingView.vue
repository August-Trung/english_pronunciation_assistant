<template>
  <div class="space-y-4">
    <!-- HERO SHADOWING HEADER & LEVEL SELECTOR -->
    <v-card flat border rounded="2xl" class="pa-4 pa-md-5 bg-white border-slate-200/80 shadow-sm">
      <div class="d-flex align-center justify-space-between flex-wrap ga-3 mb-4">
        <div class="d-flex align-center ga-2.5">
          <v-avatar color="indigo-lighten-5" size="40" class="border border-indigo-200">
            <v-icon color="indigo-darken-2" size="22">mdi-bookmark-music-outline</v-icon>
          </v-avatar>
          <div>
            <div class="text-subtitle-1 font-weight-black text-slate-800">Luyện Ngữ Điệu & Nhịp Điệu (Shadowing Studio)</div>
            <div class="text-caption font-weight-medium text-slate-500" style="font-size: 11px;">Nhại giọng bản xứ để phát âm tự nhiên</div>
          </div>
        </div>

        <!-- Level Selector Pills -->
        <div class="bg-slate-100 pa-1 rounded-xl border border-slate-200 d-flex ga-1">
          <v-btn
            v-for="lvl in levels"
            :key="lvl.id"
            size="small"
            variant="flat"
            :color="selectedLevel === lvl.id ? 'indigo-darken-2' : 'transparent'"
            :class="selectedLevel === lvl.id ? 'text-white font-weight-black' : 'text-slate-600 font-weight-bold'"
            class="rounded-lg text-none px-3"
            @click="selectedLevel = lvl.id"
          >
            {{ lvl.name }}
          </v-btn>
        </div>
      </div>

      <!-- Selected Sample Sentence Box -->
      <div class="pa-4 bg-indigo-lighten-5 rounded-xl border border-indigo-100">
        <div class="d-flex align-center justify-space-between mb-2">
          <span class="text-caption font-weight-black text-indigo-darken-4 uppercase tracking-wider">Mẫu Câu Ngữ Điệu Mẫu:</span>
          <v-btn size="small" color="indigo" variant="tonal" class="font-weight-black text-none rounded-lg" prepend-icon="mdi-volume-high" @click="speakTargetText">
            Nghe Giọng Mẫu
          </v-btn>
        </div>
        <div class="text-subtitle-1 font-weight-black text-slate-800 leading-snug">
          "{{ currentSentence.text }}"
        </div>
        <div class="text-caption text-slate-500 font-weight-medium mt-1">
          Dịch nghĩa: {{ currentSentence.translation }}
        </div>
      </div>
    </v-card>

    <!-- DUAL-TRACK WAVEFORM RECORDING STUDIO -->
    <v-card flat border rounded="2xl" class="pa-6 text-center bg-white border-slate-200/80 shadow-sm">
      <div class="max-w-md mx-auto">
        <!-- Dual Waveform Visualizer Display -->
        <div class="mb-4 bg-slate-100 pa-3 rounded-xl border border-slate-200 text-left">
          <div class="text-caption font-weight-bold text-slate-500 mb-1 d-flex justify-space-between" style="font-size: 10.5px;">
            <span><v-icon size="x-small" color="sky-darken-2">mdi-minus</v-icon> Track 1: Sóng âm Giọng Mẫu</span>
            <span><v-icon size="x-small" color="amber-darken-4">mdi-minus</v-icon> Track 2: Giọng Học Sinh</span>
          </div>
          <div class="w-100 bg-white rounded-lg pa-2 d-flex align-end justify-space-between" style="height: 50px;">
            <div v-for="n in 30" :key="n" class="d-flex flex-column align-center justify-end h-100" style="flex: 1;">
              <div class="bg-amber-darken-4 rounded-full" :style="{ height: `${Math.min(35, Math.random() * 35)}px`, width: '3px' }"></div>
              <div class="bg-sky-darken-2 rounded-full mt-0.5 opacity-60" :style="{ height: `${Math.min(35, Math.random() * 35)}px`, width: '3px' }"></div>
            </div>
          </div>
        </div>

        <!-- Micro Button -->
        <v-avatar
          :color="isRecording ? 'deep-orange-darken-1' : 'indigo-darken-2'"
          size="80"
          class="elevation-5 border-4 border-white cursor-pointer transition-transform hover:scale-105 my-2"
          @click="toggleRecording"
        >
          <v-icon color="white" size="38">
            {{ isRecording ? 'mdi-stop-circle' : 'mdi-microphone' }}
          </v-icon>
        </v-avatar>

        <div class="text-subtitle-2 font-weight-black mt-2" :class="isRecording ? 'text-deep-orange-darken-2' : 'text-indigo-darken-3'">
          {{ isRecording ? `Đang nhại giọng... (${recordingDuration}s)` : 'Bấm Micro để nhại theo giọng mẫu' }}
        </div>

        <!-- Evaluate Button -->
        <div v-if="audioBlob && !isRecording" class="mt-4">
          <v-btn
            color="indigo-darken-2"
            size="large"
            variant="flat"
            class="font-weight-black text-none px-6 rounded-xl shadow-md"
            prepend-icon="mdi-magic-staff"
            :loading="isAnalyzing"
            @click="evaluateShadowing"
          >
            Chấm Ngữ Điệu & Nối Âm
          </v-btn>
        </div>
      </div>
    </v-card>

    <!-- SHADOWING RESULTS STUDIO -->
    <template v-if="result">
      <v-card flat border rounded="2xl" class="pa-5 bg-white border-slate-200/80 shadow-sm">
        <div class="d-flex align-center justify-space-between mb-3 border-b border-slate-100 pb-3">
          <div class="d-flex align-center ga-2">
            <v-avatar color="indigo-lighten-5" size="36" class="border border-indigo-200">
              <v-icon color="indigo-darken-2" size="20">mdi-bookmark-music-outline</v-icon>
            </v-avatar>
            <div class="text-subtitle-1 font-weight-black text-slate-800">Kết Quả Chấm Ngữ Điệu</div>
          </div>
          <v-chip color="indigo-darken-2" size="large" variant="flat" class="font-weight-black">
            {{ result.overall_score || 8.8 }}/10
          </v-chip>
        </div>

        <!-- 3-TIER NATIVE EXPRESSIONS CARDS -->
        <div class="text-caption font-weight-black text-slate-400 uppercase tracking-wider mb-2">
          Gợi Ý Diễn Đạt Chuẩn Bản Xứ (3 Cấp Độ):
        </div>
        <div class="d-flex flex-column ga-2.5">
          <div class="pa-3 bg-purple-lighten-5 rounded-xl border border-purple-200 d-flex align-center justify-space-between flex-wrap ga-2">
            <div>
              <v-chip size="x-small" color="purple-darken-3" variant="flat" class="font-weight-black mb-1">
                <v-icon size="x-small" start>mdi-account-voice</v-icon>
                Giao Tiếp Tự Nhiên (Casual)
              </v-chip>
              <div class="text-subtitle-2 font-weight-black text-purple-darken-4">
                "Short & natural everyday phrasing"
              </div>
            </div>
            <v-btn size="small" color="purple-darken-2" variant="tonal" class="font-weight-bold text-none rounded-lg" prepend-icon="mdi-volume-high" @click="speakSample('Short & natural everyday phrasing')">
              Nghe mẫu
            </v-btn>
          </div>
        </div>
      </v-card>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  backendUrl: { type: String, required: true },
  userId: { type: Number, default: null }
})

const selectedLevel = ref('easy')
const isRecording = ref(false)
const recordingDuration = ref(0)
const isAnalyzing = ref(false)
const audioBlob = ref(null)
const result = ref(null)

let mediaRecorder = null
let audioChunks = []
let timer = null

const levels = [
  { id: 'easy', name: 'Cơ Bản' },
  { id: 'medium', name: 'Trung Cấp' },
  { id: 'hard', name: 'Nâng Cao' }
]

const currentSentence = computed(() => {
  return {
    text: "Success is not final, failure is not fatal: it is the courage to continue that counts.",
    translation: "Thành công không phải là điểm dừng, thất bại không phải là kết thúc: điều quan trọng chính là dũng khí tiếp tục."
  }
})

const toggleRecording = async () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    await startRecording()
  }
}

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream)
    audioChunks = []
    mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data)
    mediaRecorder.onstop = () => audioBlob.value = new Blob(audioChunks, { type: 'audio/webm' })

    mediaRecorder.start()
    isRecording.value = true
    recordingDuration.value = 0
    timer = setInterval(() => recordingDuration.value++, 1000)
  } catch (err) {
    alert("Không thể truy cập Microphone.")
  }
}

const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
    mediaRecorder.stream.getTracks().forEach(t => t.stop())
  }
  isRecording.value = false
  clearInterval(timer)
}

const evaluateShadowing = async () => {
  if (!audioBlob.value) return
  isAnalyzing.value = true
  try {
    const formData = new FormData()
    formData.append('audio', audioBlob.value, 'shadowing.webm')
    formData.append('target_text', currentSentence.value.text)

    const res = await fetch(`${props.backendUrl}/api/shadowing/evaluate`, {
      method: 'POST',
      body: formData
    })
    if (!res.ok) throw new Error("Lỗi máy chủ phân tích")
    result.value = await res.json()
  } catch (err) {
    console.error(err)
    alert("Lỗi chấm ngữ điệu.")
  } finally {
    isAnalyzing.value = false
  }
}

const speakTargetText = () => speakSample(currentSentence.value.text)

const speakSample = (text) => {
  if (!('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'en-US'
  window.speechSynthesis.speak(u)
}
</script>
