<template>
  <div class="space-y-4">
    <!-- HERO TOPIC SELECTION & PRACTICE MODE CARD -->
    <v-card flat border rounded="2xl" class="pa-4 pa-md-5 bg-white border-slate-200/80 shadow-sm">
      <div class="d-flex align-center justify-space-between flex-wrap ga-3 mb-4">
        <div class="d-flex align-center ga-2.5">
          <v-avatar color="sky-lighten-5" size="40" class="border border-sky-200">
            <v-icon color="sky-darken-2" size="22">mdi-target-account</v-icon>
          </v-avatar>
          <div>
            <div class="text-subtitle-1 font-weight-black text-slate-800">Phòng Luyện Phát Âm Studio</div>
            <div class="text-caption font-weight-medium text-slate-500" style="font-size: 11px;">Chọn chủ đề và bắt đầu nói</div>
          </div>
        </div>

        <!-- Mode Toggle (Speaking vs Reading) -->
        <div class="bg-slate-100 pa-1 rounded-xl border border-slate-200 d-flex ga-1">
          <v-btn
            size="small"
            variant="flat"
            :color="practiceMode === 'speaking' ? 'sky-darken-2' : 'transparent'"
            :class="practiceMode === 'speaking' ? 'text-white font-weight-black' : 'text-slate-600 font-weight-bold'"
            class="rounded-lg text-none px-3"
            prepend-icon="mdi-forum-outline"
            @click="practiceMode = 'speaking'"
          >
            Tự Do Nói
          </v-btn>
          <v-btn
            size="small"
            variant="flat"
            :color="practiceMode === 'reading' ? 'sky-darken-2' : 'transparent'"
            :class="practiceMode === 'reading' ? 'text-white font-weight-black' : 'text-slate-600 font-weight-bold'"
            class="rounded-lg text-none px-3"
            prepend-icon="mdi-book-open-page-variant-outline"
            @click="practiceMode = 'reading'"
          >
            Đọc Đoạn Mẫu
          </v-btn>
        </div>
      </div>

      <!-- Topic Carousel / Selection Cards -->
      <template v-if="practiceMode === 'speaking'">
        <div class="text-caption font-weight-black text-slate-400 uppercase tracking-wider mb-2">
          Gợi Ý Chủ Đề Giao Tiếp:
        </div>
        <div class="d-flex ga-2 overflow-x-auto pb-2 scrollbar-thin">
          <v-chip
            v-for="(t, idx) in availableTopics"
            :key="idx"
            variant="flat"
            :color="selectedTopic === t ? 'sky-darken-2' : 'slate-100'"
            :class="selectedTopic === t ? 'text-white font-weight-black shadow-sm' : 'text-slate-700 font-weight-bold border border-slate-200'"
            class="px-3.5 py-4 rounded-xl cursor-pointer flex-shrink-0 transition-all"
            @click="selectedTopic = t"
          >
            <v-icon start size="small" :color="selectedTopic === t ? 'white' : 'sky-darken-2'">
              mdi-chat-processing-outline
            </v-icon>
            {{ t }}
          </v-chip>
        </div>
      </template>
    </v-card>

    <!-- INTERACTIVE ACOUSTIC MICRO RECORDING STUDIO -->
    <v-card flat border rounded="2xl" class="pa-6 text-center bg-white border-slate-200/80 shadow-sm relative overflow-hidden">
      <div class="max-w-md mx-auto">
        <!-- Topic Goal Header -->
        <div class="text-subtitle-2 font-weight-black text-slate-700 mb-1">
          {{ practiceMode === 'speaking' ? (selectedTopic || 'Tự do nói câu bất kỳ...') : 'Đọc lại đoạn văn mẫu bên dưới' }}
        </div>
        <div class="text-caption text-slate-500 mb-6 font-weight-medium" style="font-size: 11.5px;">
          Bấm Micro để ghi âm giọng nói. Hệ thống AI sẽ phân tích âm tiết IPA, ngữ điệu F0 và nối âm.
        </div>

        <!-- 3D Fluid Micro Pulse Sphere -->
        <div class="d-flex justify-center align-center my-4">
          <div
            class="relative d-flex align-center justify-center transition-all cursor-pointer"
            :class="isRecording ? 'animate-pulse' : ''"
            @click="toggleRecording"
          >
            <!-- Glowing Outer Pulse Ring -->
            <div
              v-if="isRecording"
              class="absolute inset-0 rounded-full bg-sky-400/30 animate-ping"
              style="width: 110px; height: 110px; margin: -15px;"
            ></div>

            <!-- Central Recording Sphere -->
            <v-avatar
              :color="isRecording ? 'deep-orange-darken-1' : 'sky-darken-2'"
              size="88"
              class="elevation-6 border-4 border-white transition-transform hover:scale-105"
            >
              <v-icon color="white" size="44">
                {{ isRecording ? 'mdi-stop-circle' : 'mdi-microphone' }}
              </v-icon>
            </v-avatar>
          </div>
        </div>

        <!-- Status Text & Recording Timer -->
        <div class="mt-3">
          <div class="text-subtitle-2 font-weight-black" :class="isRecording ? 'text-deep-orange-darken-2' : 'text-sky-darken-3'">
            {{ isRecording ? `Đang thu âm... (${recordingDuration}s)` : 'Bấm vào Micro để bắt đầu' }}
          </div>
          <div class="text-caption text-slate-400 font-weight-bold" style="font-size: 10px;">
            {{ isRecording ? 'Nói rõ ràng vào Micro' : 'Giữ khoảng cách micro gần miệng 10-15cm' }}
          </div>
        </div>

        <!-- Submit Evaluation Button -->
        <div v-if="audioBlob && !isRecording" class="mt-5 d-flex justify-center ga-3">
          <v-btn
            color="primary"
            size="large"
            variant="flat"
            class="font-weight-black text-none px-6 rounded-xl shadow-md"
            prepend-icon="mdi-magic-staff"
            :loading="isAnalyzing"
            @click="evaluateSpeech"
          >
            Chấm Điểm & Phân Tích IPA
          </v-btn>
          <v-btn
            color="slate"
            variant="outlined"
            size="large"
            class="font-weight-bold text-none rounded-xl"
            icon="mdi-refresh"
            @click="clearRecording"
          />
        </div>
      </div>
    </v-card>

    <!-- EVALUATION RESULTS STUDIO SECTION -->
    <template v-if="results">
      <!-- 1. OVERALL SCORES INFOGRAPHIC -->
      <v-card flat border rounded="2xl" class="pa-5 bg-white border-slate-200/80 shadow-sm">
        <div class="d-flex align-center justify-space-between border-b border-slate-100 pb-3 mb-4">
          <div class="d-flex align-center ga-2">
            <v-avatar color="amber-lighten-5" size="36" class="border border-amber-200">
              <v-icon color="amber-darken-3" size="20">mdi-trophy-award</v-icon>
            </v-avatar>
            <div class="text-subtitle-1 font-weight-black text-slate-800">Kết Quả Phân Tích Tổng Thể</div>
          </div>
          <v-chip color="sky-darken-2" size="large" variant="flat" class="font-weight-black text-h6">
            {{ results.total_score || 8.5 }}/10
          </v-chip>
        </div>

        <!-- 5 Core Skill Progress Bars -->
        <v-row density="comfortable" class="ma-0">
          <v-col v-for="(val, name) in (results.breakdown || defaultBreakdown)" :key="name" cols="6" sm="4" md="2.4" class="pa-1">
            <div class="pa-3 bg-slate-50 rounded-xl border border-slate-200 text-center">
              <div class="text-caption font-weight-bold text-slate-500 mb-1" style="font-size: 11px;">{{ name }}</div>
              <div class="text-subtitle-1 font-weight-black text-sky-darken-3">{{ val }}/2</div>
            </div>
          </v-col>
        </v-row>
      </v-card>

      <!-- 2. INTERACTIVE PHONETIC IPA INFOGRAPHIC MAP -->
      <v-card v-if="results.ipa_analysis" flat border rounded="2xl" class="pa-5 bg-white border-slate-200/80 shadow-sm">
        <div class="d-flex align-center justify-space-between mb-3">
          <div class="d-flex align-center ga-2">
            <v-avatar color="teal-lighten-5" size="36" class="border border-teal-200">
              <v-icon color="teal-darken-3" size="20">mdi-phonetics</v-icon>
            </v-avatar>
            <div>
              <div class="text-subtitle-1 font-weight-black text-teal-darken-4">Bản Đồ Phiên Âm IPA & Âm Tiết</div>
              <div class="text-caption font-weight-medium text-slate-500" style="font-size: 10.5px;">Đối chiếu chi tiết từng từ</div>
            </div>
          </div>
          <v-chip color="teal-darken-3" size="small" variant="flat" class="font-weight-black">
            Khớp IPA {{ results.ipa_analysis.ipa_accuracy }}%
          </v-chip>
        </div>

        <!-- Connected Speech Liaisons Banner -->
        <div v-if="results.ipa_analysis.linking_pairs?.length" class="bg-amber-lighten-5 pa-3 rounded-xl border border-amber-200 mb-4">
          <div class="text-caption font-weight-black text-amber-darken-4 mb-1.5 d-flex align-center ga-1.5">
            <v-icon color="amber-darken-3" size="small">mdi-link-variant</v-icon>
            <span>Gợi Ý Nối Âm Tự Nhiên Bản Xứ (Connected Speech):</span>
          </div>
          <div class="d-flex flex-wrap ga-2">
            <v-chip
              v-for="(pair, l_idx) in results.ipa_analysis.linking_pairs"
              :key="l_idx"
              size="small"
              color="amber-darken-4"
              variant="flat"
              class="font-weight-black"
            >
              {{ pair.word1 }} <v-icon size="x-small" class="mx-0.5">mdi-link-variant</v-icon> {{ pair.word2 }} ({{ pair.ipa_link }})
            </v-chip>
          </div>
        </div>

        <!-- Word by Word IPA Micro-Cards -->
        <div class="d-flex flex-wrap ga-2.5">
          <div
            v-for="(w_ipa, idx) in (results.ipa_analysis.words_ipa || [])"
            :key="idx"
            class="pa-3 bg-slate-50 rounded-xl border border-slate-200 d-flex flex-column align-center flex-grow-1"
            style="min-width: 105px;"
          >
            <div class="text-subtitle-2 font-weight-black text-slate-800 d-flex align-center ga-1">
              <span>{{ w_ipa.word }}</span>
              <v-icon v-if="w_ipa.stress_note" size="x-small" color="deep-orange">mdi-fire</v-icon>
            </div>

            <v-chip
              size="x-small"
              variant="flat"
              :color="w_ipa.status === 'correct' ? 'success' : w_ipa.status === 'partial' ? 'warning' : 'error'"
              class="font-weight-black mt-1"
              style="font-size: 10.5px;"
            >
              {{ w_ipa.target_ipa }}
            </v-chip>

            <div v-if="w_ipa.spoken_ipa && w_ipa.status !== 'correct'" class="text-caption font-weight-bold text-error mt-1" style="font-size: 9.5px;">
              Đọc: {{ w_ipa.spoken_ipa }}
            </div>

            <div v-if="w_ipa.note" class="text-caption text-error font-weight-bold text-center mt-1" style="font-size: 9.5px; line-height: 1.2;">
              {{ w_ipa.note }}
            </div>

            <!-- Button Xem Khẩu Hình 2D/3D -->
            <v-btn
              size="x-small"
              variant="tonal"
              color="teal-darken-3"
              class="mt-2 font-weight-bold text-none px-2 rounded-lg"
              style="font-size: 9px; height: 22px;"
              prepend-icon="mdi-lips"
              @click="openArticulationGuide(w_ipa.word, w_ipa.target_ipa)"
            >
              Khẩu hình
            </v-btn>
          </div>
        </div>
      </v-card>

      <!-- 3. INTONATION PITCH CURVE CHART (F0 OVERLAY) -->
      <v-card v-if="results.ipa_analysis?.pitch_analysis?.pitch_points?.length" flat border rounded="2xl" class="pa-5 bg-white border-slate-200/80 shadow-sm">
        <div class="d-flex align-center justify-space-between mb-3">
          <div class="d-flex align-center ga-2">
            <v-avatar color="indigo-lighten-5" size="36" class="border border-indigo-200">
              <v-icon color="indigo-darken-2" size="20">mdi-chart-bell-curve-cumulative</v-icon>
            </v-avatar>
            <div class="text-subtitle-1 font-weight-black text-slate-800">Biểu Đồ Ngữ Điệu F0 Pitch Contour</div>
          </div>
          <v-chip size="small" color="indigo" variant="flat" class="font-weight-black">
            Khớp ngữ điệu {{ results.ipa_analysis.pitch_analysis.pitch_accuracy }}%
          </v-chip>
        </div>

        <!-- SVG / Bar Pitch Curve Chart Container -->
        <div class="w-100 bg-slate-100 rounded-xl pa-4 d-flex align-end justify-space-between" style="height: 90px;">
          <div
            v-for="(pt, p_idx) in results.ipa_analysis.pitch_analysis.pitch_points"
            :key="p_idx"
            class="d-flex flex-column align-center justify-end h-100"
            style="flex: 1;"
          >
            <div
              v-if="pt.student_f0"
              class="bg-amber-darken-3 rounded-full"
              :style="{ height: `${Math.min(70, Math.max(8, (pt.student_f0 - 70) / 3))}px`, width: '5px' }"
            ></div>
            <div
              class="bg-sky-darken-2 rounded-full mt-1 opacity-60"
              :style="{ height: `${Math.min(70, Math.max(8, (pt.native_f0 - 70) / 3))}px`, width: '4px' }"
            ></div>
          </div>
        </div>
      </v-card>
    </template>

    <!-- ARTICULATION ANATOMICAL MODAL DIALOG -->
    <v-dialog v-model="showArticulationModal" max-width="480">
      <v-card v-if="selectedArticulation" border rounded="2xl" class="pa-5 bg-white">
        <div class="d-flex align-center justify-space-between mb-4 border-b border-slate-100 pb-3">
          <div class="d-flex align-center ga-2.5">
            <v-avatar color="teal-lighten-5" size="42" class="border border-teal-200">
              <v-icon color="teal-darken-3" size="24">mdi-lips</v-icon>
            </v-avatar>
            <div>
              <div class="text-subtitle-1 font-weight-black text-slate-800">{{ selectedArticulation.title }}</div>
              <div class="text-caption font-weight-bold text-sky-darken-3 font-mono">Phiên âm: {{ selectedArticulation.ipa }}</div>
            </div>
          </div>
          <v-btn icon="mdi-close" variant="text" density="comfortable" @click="showArticulationModal = false" />
        </div>

        <div class="space-y-3 text-caption">
          <div class="bg-slate-50 pa-3 rounded-xl border border-slate-200">
            <div class="font-weight-black text-slate-800 mb-1 d-flex align-center ga-1">
              <v-icon color="pink" size="x-small">mdi-lips</v-icon>
              <span>1. Khẩu Hình Môi & Răng:</span>
            </div>
            <div class="text-slate-600 font-weight-medium">{{ selectedArticulation.mouth_position }}</div>
          </div>

          <div class="bg-slate-50 pa-3 rounded-xl border border-slate-200">
            <div class="font-weight-black text-slate-800 mb-1 d-flex align-center ga-1">
              <v-icon color="deep-orange" size="x-small">mdi-emoticon-tongue-outline</v-icon>
              <span>2. Vị Trí Đầu Lưỡi:</span>
            </div>
            <div class="text-slate-600 font-weight-medium">{{ selectedArticulation.tongue_position }}</div>
          </div>

          <div class="bg-slate-50 pa-3 rounded-xl border border-slate-200">
            <div class="font-weight-black text-slate-800 mb-1 d-flex align-center ga-1">
              <v-icon color="sky-darken-2" size="x-small">mdi-weather-windy</v-icon>
              <span>3. Luồng Hơi & Thanh Quản:</span>
            </div>
            <div class="text-slate-600 font-weight-medium">{{ selectedArticulation.airflow }}</div>
          </div>

          <div class="bg-amber-lighten-5 pa-3 rounded-xl border border-amber-200">
            <div class="font-weight-black text-amber-darken-4 mb-1 d-flex align-center ga-1">
              <v-icon color="amber-darken-3" size="x-small">mdi-lightbulb-on-outline</v-icon>
              <span>Mẹo Luyện Tập Nhanh:</span>
            </div>
            <div class="text-amber-darken-4 font-weight-bold">{{ selectedArticulation.tip }}</div>
          </div>
        </div>

        <v-card-actions class="px-0 pt-4 pb-0">
          <v-spacer />
          <v-btn color="primary" variant="flat" class="font-weight-black text-none rounded-xl" @click="speakSample(selectedArticulation.ipa)">
            <v-icon start>mdi-volume-high</v-icon> Nghe Âm Mẫu
          </v-btn>
          <v-btn color="slate" variant="outlined" class="font-weight-bold text-none rounded-xl" @click="showArticulationModal = false">
            Đóng
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  backendUrl: { type: String, required: true },
  userId: { type: Number, default: null }
})

const practiceMode = ref('speaking')
const selectedTopic = ref('Tự giới thiệu bản thân')
const isRecording = ref(false)
const recordingDuration = ref(0)
const isAnalyzing = ref(false)
const audioBlob = ref(null)
const results = ref(null)

const showArticulationModal = ref(false)
const selectedArticulation = ref(null)

let mediaRecorder = null
let audioChunks = []
let timer = null

const availableTopics = [
  'Tự giới thiệu bản thân',
  'Sở thích & Đam mê',
  'Công việc hàng ngày',
  'Chủ đề Ăn uống & Ẩm thực',
  'Du lịch & Khám phá'
]

const defaultBreakdown = {
  Pronunciation: 1.8,
  Fluency: 1.7,
  Grammar: 1.9,
  Vocabulary: 1.8,
  Communication: 1.9
}

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
    mediaRecorder.onstop = () => {
      audioBlob.value = new Blob(audioChunks, { type: 'audio/webm' })
    }

    mediaRecorder.start()
    isRecording.value = true
    recordingDuration.value = 0
    timer = setInterval(() => recordingDuration.value++, 1000)
  } catch (err) {
    alert("Không thể truy cập Microphone trên thiết bị.")
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

const clearRecording = () => {
  audioBlob.value = null
  results.value = null
}

const evaluateSpeech = async () => {
  if (!audioBlob.value) return
  isAnalyzing.value = true

  try {
    const formData = new FormData()
    formData.append('audio', audioBlob.value, 'recorded_audio.webm')
    formData.append('topic', selectedTopic.value)
    if (props.userId) formData.append('user_id', props.userId)

    const res = await fetch(`${props.backendUrl}/api/analyze-audio`, {
      method: 'POST',
      body: formData
    })

    if (!res.ok) throw new Error("Lỗi máy chủ phân tích")
    const data = await res.json()
    results.value = data
  } catch (err) {
    console.error(err)
    alert("Lỗi phân tích âm thanh từ máy chủ.")
  } finally {
    isAnalyzing.value = false
  }
}

const ARTICULATION_GUIDES = {
  's': {
    title: 'Phụ Âm Xì /s/ (Fricative)',
    ipa: '/s/',
    mouth_position: 'Hai hàm răng khép nhẹ, hai mép môi hơi kéo sang 2 bên như đang mỉm cười nhẹ.',
    tongue_position: 'Đầu lưỡi nâng gần sát nướu răng cửa trên (không chạm vào răng), tạo khe hẹp.',
    airflow: 'Đẩy luồng hơi xì xát liên tục qua khe giữa đầu lưỡi và nướu răng. Không rung dây thanh quản (Voiceless).',
    tip: 'Hãy giữ luồng hơi kéo dài 1-2 giây để tạo tiếng xì giòn giã.'
  },
  't': {
    title: 'Phụ Âm Bật /t/ (Plosive)',
    ipa: '/t/',
    mouth_position: 'Môi hơi mở tự nhiên.',
    tongue_position: 'Đầu lưỡi áp chặt vào nướu răng cửa trên để chặn hoàn toàn luồng khí.',
    airflow: 'Bật nhẹ đầu lưỡi xuống nhanh để giải phóng luồng khí nén tạo tiếng bật dứt khoát.',
    tip: 'Đặt bàn tay trước miệng, bạn phải cảm nhận được một luồng hơi bật mạnh ra.'
  }
}

const openArticulationGuide = (word, ipaStr) => {
  selectedArticulation.value = ARTICULATION_GUIDES['s']
  showArticulationModal.value = true
}

const speakSample = (text) => {
  if (!('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'en-US'
  window.speechSynthesis.speak(u)
}
</script>
