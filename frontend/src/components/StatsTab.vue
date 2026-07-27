<template>
  <div class="space-y-4">
    <!-- HERO STATS HEADER -->
    <v-card flat border rounded="2xl" class="pa-4 pa-md-5 bg-white border-slate-200/80 shadow-sm">
      <div class="d-flex align-center justify-space-between flex-wrap ga-3">
        <div class="d-flex align-center ga-2.5">
          <v-avatar color="indigo-lighten-5" size="40" class="border border-indigo-200">
            <v-icon color="indigo-darken-2" size="22">mdi-chart-timeline-variant</v-icon>
          </v-avatar>
          <div>
            <div class="text-subtitle-1 font-weight-black text-slate-800">Thống Kê Kỹ Năng & Báo Cáo</div>
            <div class="text-caption font-weight-medium text-slate-500" style="font-size: 11px;">Phân tích sự tiến bộ phát âm theo thời gian</div>
          </div>
        </div>
      </div>
    </v-card>

    <!-- 5 CORE SKILLS RADAR & PROGRESS STAGE -->
    <v-card flat border rounded="2xl" class="pa-5 bg-white border-slate-200/80 shadow-sm">
      <div class="text-caption font-weight-black text-slate-400 uppercase tracking-wider mb-3">
        Đánh Giá 5 Kỹ Năng Cốt Lõi:
      </div>

      <v-row density="comfortable" class="ma-0">
        <v-col v-for="skill in skills" :key="skill.name" cols="12" sm="6" md="4" class="pa-1.5">
          <div class="pa-3 bg-slate-50 rounded-xl border border-slate-200">
            <div class="d-flex align-center justify-space-between mb-1.5">
              <span class="text-caption font-weight-black text-slate-800 d-flex align-center ga-1">
                <v-icon size="x-small" :color="skill.color">{{ skill.icon }}</v-icon>
                <span>{{ skill.name }}</span>
              </span>
              <span class="text-caption font-weight-black text-sky-darken-3">{{ skill.score }}/2.0</span>
            </div>
            <v-progress-linear :model-value="(skill.score / 2.0) * 100" :color="skill.color" height="6" rounded />
          </div>
        </v-col>
      </v-row>
    </v-card>

    <!-- 3D HOLOGRAM BADGES SHOWCASE -->
    <v-card flat border rounded="2xl" class="pa-5 bg-white border-slate-200/80 shadow-sm">
      <div class="text-caption font-weight-black text-slate-400 uppercase tracking-wider mb-3">
        Bộ Sưu Tập Danh Hiệu Học Tập (Badges):
      </div>

      <div class="d-flex flex-wrap ga-3">
        <div
          v-for="badge in badges"
          :key="badge.title"
          class="pa-3 bg-sky-lighten-5 rounded-xl border border-sky-200 d-flex align-center ga-3 flex-1"
          style="min-width: 200px;"
        >
          <v-avatar color="sky-darken-2" size="40" class="elevation-2">
            <v-icon color="white" size="22">{{ badge.icon }}</v-icon>
          </v-avatar>
          <div>
            <div class="text-subtitle-2 font-weight-black text-sky-darken-4">{{ badge.title }}</div>
            <div class="text-caption text-slate-500 font-weight-medium" style="font-size: 10.5px;">{{ badge.desc }}</div>
          </div>
        </div>
      </div>
    </v-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const skills = ref([
  { name: 'Phát âm (Pronunciation)', score: 1.8, color: 'sky-darken-2', icon: 'mdi-microphone' },
  { name: 'Trôi chảy (Fluency)', score: 1.7, color: 'emerald-darken-2', icon: 'mdi-waveform' },
  { name: 'Ngữ pháp (Grammar)', score: 1.9, color: 'deep-orange-darken-1', icon: 'mdi-lead-pencil' },
  { name: 'Từ vựng (Vocabulary)', score: 1.8, color: 'purple-darken-2', icon: 'mdi-book-alphabet' },
  { name: 'Giao tiếp (Communication)', score: 1.9, color: 'indigo-darken-2', icon: 'mdi-forum' },
])

const badges = ref([
  { title: 'Học Viên Chăm Chỉ', desc: 'Đạt chuỗi 10 ngày Streak', icon: 'mdi-medal' },
  { title: 'Bậc Thầy Ngữ Điệu', desc: 'Khớp ngữ điệu trên 85%', icon: 'mdi-certificate' },
  { title: 'Chiến Binh Từ Vựng', desc: 'Thuộc trên 50 từ vựng', icon: 'mdi-ribbon' },
])
</script>
