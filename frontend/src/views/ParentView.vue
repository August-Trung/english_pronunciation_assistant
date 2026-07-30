<template>
  <v-container fluid class="pa-4 pa-md-6" style="max-width: 900px;">
    <!-- Parent Portal Header -->
    <v-card border flat class="pa-4 mb-4 bg-gradient-teal text-white rounded-lg elevation-1">
      <div class="d-flex align-center ga-3">
        <v-avatar color="white" size="48" class="elevation-1">
          <v-icon color="teal-darken-3" size="large">mdi-human-female-boy</v-icon>
        </v-avatar>
        <div>
          <div class="text-h6 font-weight-black tracking-tight">CỔNG PHỤ HUYNH & TIẾN ĐỘ HỌC TẬP</div>
          <div class="text-caption opacity-90 font-weight-medium">
            Theo dõi điểm số phát âm IPA, nghe lại bài thu âm và xem nhận xét từ Giáo viên dành cho con
          </div>
        </div>
      </div>
    </v-card>

    <!-- Tracking Code Input Form -->
    <v-card border flat class="pa-4 mb-4 bg-white rounded-lg">
      <div class="text-subtitle-2 font-weight-black text-secondary mb-2">NHẬP MÃ THEO DÕI CỦA CON</div>
      <div class="d-flex align-center ga-2">
        <v-text-field
          v-model="parentCode"
          placeholder="Ví dụ: PA-9842 (Xem mã trong Hồ sơ cá nhân của con)"
          variant="outlined"
          density="comfortable"
          hide-details
          prepend-inner-icon="mdi-qrcode"
          class="bg-grey-lighten-5"
          @keyup.enter="fetchReport"
        />
        <v-btn
          color="teal-darken-2"
          variant="flat"
          height="44"
          class="font-weight-black text-none px-6"
          prepend-icon="mdi-magnify"
          :loading="isLoading"
          @click="fetchReport"
        >
          Tra Cứu Tiến Độ
        </v-btn>
      </div>
    </v-card>

    <!-- Student Progress Report Display -->
    <div v-if="report">
      <v-card border flat class="pa-4 mb-4 bg-white rounded-lg">
        <div class="d-flex align-center justify-space-between flex-wrap ga-3 border-b pb-3 mb-3">
          <div class="d-flex align-center ga-3">
            <v-avatar color="teal-lighten-5" size="48" class="text-teal-darken-3 font-weight-black text-h6 border">
              {{ report.student.name.slice(0, 1).toUpperCase() }}
            </v-avatar>
            <div>
              <div class="text-h6 font-weight-black text-primary">{{ report.student.name }}</div>
              <div class="text-caption text-grey">Mã Phụ Huynh: <strong>{{ report.student.parent_code }}</strong></div>
            </div>
          </div>

          <div class="d-flex align-center ga-3">
            <v-chip color="teal" variant="flat" size="large" class="font-weight-black">
              Điểm Trung Bình: {{ report.avg_score }}/10
            </v-chip>
            <v-chip color="indigo" variant="tonal" size="large" class="font-weight-black">
              Đã Hoàn Thành: {{ report.total_completed }} Bài
            </v-chip>
          </div>
        </div>

        <div class="text-subtitle-2 font-weight-black text-secondary mb-3">DANH SÁCH BÀI ĐỌC THU ÂM CỦA CON</div>

        <div class="d-flex flex-column ga-3">
          <v-card
            v-for="sub in report.submissions"
            :key="sub.id"
            border
            flat
            class="pa-3 bg-grey-lighten-5 rounded-lg"
          >
            <div class="d-flex align-center justify-space-between flex-wrap ga-2 mb-2">
              <span class="text-subtitle-2 font-weight-black text-indigo">{{ sub.title }}</span>
              <v-chip color="success" size="small" variant="flat" class="font-weight-black">
                Điểm bài đọc: {{ sub.score.toFixed(1) }}/10
              </v-chip>
            </div>

            <div class="text-caption font-italic text-grey-darken-3 bg-white pa-2 rounded border mb-2">
              "{{ sub.transcribed_text }}"
            </div>

            <!-- Supabase Audio Stream Player -->
            <div v-if="sub.audio_url" class="bg-white pa-2 rounded border d-flex align-center ga-2 mb-2">
              <v-icon color="teal-darken-2">mdi-volume-high</v-icon>
              <audio controls :src="sub.audio_url" class="w-100" style="height: 32px;" />
            </div>

            <!-- Teacher Feedback -->
            <div v-if="sub.teacher_feedback" class="bg-indigo-lighten-5 pa-2 rounded border border-indigo text-caption">
              <strong class="text-indigo-darken-3">Lời nhận xét của Giáo viên:</strong> {{ sub.teacher_feedback }}
            </div>
          </v-card>

          <div v-if="!report.submissions?.length" class="text-center pa-6 text-caption text-grey border rounded-lg">
            Con chưa nộp bài đọc nào. Vui lòng nhắc con hoàn thành bài tập về nhà trên ứng dụng!
          </div>
        </div>
      </v-card>
    </div>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  backendUrl: String
})

const parentCode = ref('')
const isLoading = ref(false)
const report = ref(null)

const fetchReport = async () => {
  if (!parentCode.value.trim()) return
  isLoading.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/parent/student/${parentCode.value.trim()}`)
    if (res.ok) {
      report.value = await res.json()
    } else {
      const err = await res.json()
      alert(err.detail || 'Không tìm thấy thông tin của con.')
      report.value = null
    }
  } catch (e) {
    alert('Lỗi tra cứu: ' + e.message)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.bg-gradient-teal {
  background: linear-gradient(135deg, #00897b 0%, #004d40 100%);
}
</style>
