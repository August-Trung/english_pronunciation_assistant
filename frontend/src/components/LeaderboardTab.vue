<template>
  <div class="space-y-4">
    <!-- HERO LEADERBOARD HEADER -->
    <v-card flat border rounded="2xl" class="pa-4 pa-md-5 bg-white border-slate-200/80 shadow-sm">
      <div class="d-flex align-center justify-space-between flex-wrap ga-3">
        <div class="d-flex align-center ga-2.5">
          <v-avatar color="amber-lighten-5" size="40" class="border border-amber-200">
            <v-icon color="amber-darken-3" size="22">mdi-trophy</v-icon>
          </v-avatar>
          <div>
            <div class="text-subtitle-1 font-weight-black text-slate-800">Đấu Trường Vinh Quang Học Viên</div>
            <div class="text-caption font-weight-medium text-slate-500" style="font-size: 11px;">Bảng xếp hạng cày Streak & XP tuần</div>
          </div>
        </div>
      </div>
    </v-card>

    <!-- TOP 3 PODIUM ARENA STAGE -->
    <v-card flat border rounded="2xl" class="pa-6 bg-white border-slate-200/80 shadow-sm">
      <div class="text-caption font-weight-black text-slate-400 uppercase tracking-wider mb-4 text-center">
        TOP 3 HỌC VIÊN DẪN ĐẦU TUẦN NÀY
      </div>

      <!-- Top 3 Podium Visualizer -->
      <div class="d-flex align-end justify-center ga-3 ga-md-6 mb-6 px-2">
        <!-- TOP 2 SILVER PODIUM -->
        <div class="d-flex flex-column align-center flex-1" style="max-width: 110px;">
          <v-avatar size="52" class="border-2 border-slate-300 shadow-sm mb-2">
            <v-img :src="getAvatar('Minh Anh')" />
          </v-avatar>
          <div class="text-caption font-weight-black text-slate-800 text-truncate w-100 text-center">Minh Anh</div>
          <div class="text-caption text-slate-500 font-weight-bold" style="font-size: 10px;">1,280 XP</div>
          <div class="w-100 bg-slate-200 rounded-t-xl pa-3 text-center mt-2 border-t-4 border-slate-400" style="height: 70px;">
            <v-icon color="slate-600" size="24">mdi-numeric-2-circle</v-icon>
          </div>
        </div>

        <!-- TOP 1 GOLD PODIUM (HERO CENTER) -->
        <div class="d-flex flex-column align-center flex-1 relative" style="max-width: 130px;">
          <!-- Floating Crown -->
          <v-icon color="amber-darken-3" size="32" class="absolute -top-6 animate-bounce">
            mdi-trophy-crown
          </v-icon>
          <v-avatar size="68" class="border-4 border-amber-300 shadow-md mb-2">
            <v-img :src="getAvatar('Bảo Nam')" />
          </v-avatar>
          <div class="text-subtitle-2 font-weight-black text-slate-800 text-truncate w-100 text-center">Bảo Nam</div>
          <div class="text-caption text-amber-darken-4 font-weight-black" style="font-size: 11px;">1,850 XP</div>
          <div class="w-100 bg-amber-lighten-4 rounded-t-2xl pa-4 text-center mt-2 border-t-4 border-amber-500 shadow-sm" style="height: 95px;">
            <v-icon color="amber-darken-3" size="32">mdi-numeric-1-circle</v-icon>
          </div>
        </div>

        <!-- TOP 3 BRONZE PODIUM -->
        <div class="d-flex flex-column align-center flex-1" style="max-width: 110px;">
          <v-avatar size="52" class="border-2 border-amber-700 shadow-sm mb-2">
            <v-img :src="getAvatar('Thu Trang')" />
          </v-avatar>
          <div class="text-caption font-weight-black text-slate-800 text-truncate w-100 text-center">Thu Trang</div>
          <div class="text-caption text-slate-500 font-weight-bold" style="font-size: 10px;">1,120 XP</div>
          <div class="w-100 bg-amber-lighten-5 rounded-t-xl pa-3 text-center mt-2 border-t-4 border-amber-700" style="height: 55px;">
            <v-icon color="amber-darken-4" size="24">mdi-numeric-3-circle</v-icon>
          </div>
        </div>
      </div>

      <!-- LEADERBOARD RANKINGS LIST -->
      <div class="space-y-2">
        <div
          v-for="(user, idx) in leaderboardList"
          :key="idx"
          class="pa-3 bg-slate-50 rounded-xl border border-slate-200 d-flex align-center justify-space-between"
        >
          <div class="d-flex align-center ga-3">
            <div class="font-weight-black text-slate-400 w-6 text-center">{{ idx + 4 }}</div>
            <v-avatar size="36" class="border">
              <v-img :src="getAvatar(user.name)" />
            </v-avatar>
            <div>
              <div class="text-subtitle-2 font-weight-black text-slate-800">{{ user.name }}</div>
              <div class="text-caption text-slate-500 font-weight-medium" style="font-size: 10.5px;">Level {{ user.level }}</div>
            </div>
          </div>

          <div class="d-flex align-center ga-3">
            <v-chip size="x-small" color="deep-orange-darken-1" variant="flat" class="font-weight-black">
              <v-icon start size="x-small">mdi-fire</v-icon>
              {{ user.streak }} Ngày
            </v-chip>
            <v-chip size="small" color="amber-darken-3" variant="flat" class="font-weight-black">
              <v-icon start size="x-small">mdi-star</v-icon>
              {{ user.xp }} XP
            </v-chip>
          </div>
        </div>
      </div>
    </v-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const leaderboardList = ref([
  { name: 'Khánh Linh', level: 'B1', streak: 10, xp: 980 },
  { name: 'Đức Huy', level: 'A2', streak: 8, xp: 870 },
  { name: 'Phương Thảo', level: 'A1', streak: 6, xp: 750 },
  { name: 'Hoàng Long', level: 'B2', streak: 5, xp: 640 },
])

const getAvatar = (name) => {
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=0288D1&color=fff&bold=true`
}
</script>
