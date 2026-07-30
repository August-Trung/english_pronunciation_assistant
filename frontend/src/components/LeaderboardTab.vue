<template>
  <v-container fluid class="pa-0">
    <!-- Header Card -->
    <v-card border flat class="pa-3 pa-sm-4 mb-4 bg-gradient-to-r text-white" rounded="lg" style="background: linear-gradient(135deg, #3F51B5 0%, #1A237E 100%);">
      <div class="d-flex align-center justify-space-between flex-wrap ga-2">
        <div class="d-flex align-center ga-2 ga-sm-3">
          <v-avatar color="amber" size="40" class="elevation-3 flex-shrink-0">
            <v-icon size="default" color="white">mdi-trophy-variant</v-icon>
          </v-avatar>
          <div>
            <div class="text-subtitle-1 text-sm-h6 font-weight-black tracking-tight leading-tight">ĐẤU TRƯỜNG PHÁT ÂM</div>
            <div class="text-caption text-indigo-lighten-4 font-weight-bold">Vinh danh Top 10 Học Sinh Xuất Sắc Nhất</div>
          </div>
        </div>
        <v-btn
          color="amber"
          variant="flat"
          size="small"
          class="font-weight-black text-none"
          prepend-icon="mdi-refresh"
          :loading="isLoading"
          @click="fetchLeaderboard"
        >
          Cập nhật thứ hạng
        </v-btn>
      </div>
    </v-card>

    <div v-if="isLoading" class="d-flex flex-column align-center justify-center py-12">
      <v-progress-circular indeterminate color="primary" size="48" width="4" class="mb-3" />
      <div class="text-caption font-weight-bold text-grey-darken-1">Đang tải Bảng Xếp Hạng...</div>
    </div>

    <div v-else>
      <!-- Always Show Top 3 Podium Winners (Top 2 | Top 1 | Top 3) -->
      <v-row class="ma-0 mb-4 align-end justify-center ga-1 ga-sm-3">
        <!-- Top 2 (Silver) -->
        <v-col cols="4" sm="3" class="pa-1">
          <v-card border flat class="pa-2 pa-sm-3 text-center elevation-1 rounded-lg" :class="top2.isEmpty ? 'bg-grey-lighten-4 opacity-70 border-dashed' : 'bg-white'">
            <div class="d-flex align-center justify-center mb-1">
              <v-chip label size="x-small" color="grey-darken-2" variant="tonal" class="px-2">
                <v-icon size="x-small" class="mr-1">mdi-medal-outline</v-icon> Top 2
              </v-chip>
            </div>
            
            <v-avatar color="grey-lighten-3" size="38" class="mb-1 border">
              <v-img v-if="!top2.isEmpty" :src="getAvatarUrl(top2)" alt="Avatar" />
              <v-icon v-else color="grey-darken-1" size="small">mdi-account</v-icon>
            </v-avatar>

            <div class="text-caption font-weight-black name-wrap mb-1" :class="top2.isEmpty ? 'text-grey' : 'text-grey-darken-3'">
              {{ top2.isEmpty ? 'Đang trống' : formatDisplayName(top2.name) }}
            </div>

            <v-chip v-if="top2.badge_title" label size="x-small" color="grey-darken-2" variant="tonal" class="mb-1 px-1" style="font-size: 9px;">
              {{ top2.badge_title }}
            </v-chip>
            <div class="text-caption font-weight-black" :class="top2.isEmpty ? 'text-grey' : 'text-primary'">
              {{ top2.isEmpty ? '--/10' : `${(top2.best_score ?? top2.avg_score ?? 0).toFixed(1).replace('.', ',')}/10` }}
            </div>
            <div class="text-caption text-grey font-weight-bold" style="font-size: 10px;">
              <v-icon size="x-small" color="deep-orange">mdi-fire</v-icon> {{ top2.streak_count || top2.streak || 1 }} ngày
            </div>
          </v-card>
        </v-col>

        <!-- Top 1 (Gold Winner) -->
        <v-col cols="4" sm="4" class="pa-1">
          <v-card border flat class="pa-2 pa-sm-3 text-center elevation-2 rounded-lg" :class="top1.isEmpty ? 'bg-grey-lighten-4 opacity-70 border-dashed' : 'bg-amber-lighten-5 border-amber'">
            <div class="d-flex align-center justify-center mb-1">
              <v-chip label size="x-small" color="amber-darken-3" variant="tonal" class="px-2">
                <v-icon size="x-small" class="mr-1">mdi-crown</v-icon> Top 1
              </v-chip>
            </div>

            <v-avatar color="amber" size="44" class="mb-1 border border-amber border-2 elevation-1">
              <v-img v-if="!top1.isEmpty" :src="getAvatarUrl(top1)" alt="Avatar" />
              <v-icon v-else color="white" size="medium">mdi-account</v-icon>
            </v-avatar>
            
            <div class="text-caption font-weight-black name-wrap mb-1" :class="top1.isEmpty ? 'text-grey' : 'text-amber-darken-4'">
              {{ top1.isEmpty ? 'Đang trống' : formatDisplayName(top1.name) }}
            </div>
            
            <v-chip v-if="top1.badge_title" label size="x-small" color="amber-darken-3" variant="tonal" class="mb-1 px-1" style="font-size: 9px;">
              {{ top1.badge_title }}
            </v-chip>
            
            <div class="text-caption font-weight-black" :class="top1.isEmpty ? 'text-grey' : 'text-amber-darken-4'">
              {{ top1.isEmpty ? '--/10' : `${(top1.best_score ?? top1.avg_score ?? 0).toFixed(1).replace('.', ',')}/10` }}
            </div>
            <div class="text-caption text-amber-darken-3 font-weight-bold" style="font-size: 10px;">
              <v-icon size="x-small" color="deep-orange">mdi-fire</v-icon> {{ top1.streak_count || top1.streak || 1 }} ngày
            </div>
          </v-card>
        </v-col>

        <!-- Top 3 (Bronze) -->
        <v-col cols="4" sm="3" class="pa-1">
          <v-card border flat class="pa-2 pa-sm-3 text-center elevation-1 rounded-lg" :class="top3.isEmpty ? 'bg-grey-lighten-4 opacity-70 border-dashed' : 'bg-white'">
            <div class="d-flex align-center justify-center mb-1">
              <v-chip label size="x-small" color="brown" variant="tonal" class="px-2">
                <v-icon size="x-small" class="mr-1">mdi-medal-outline</v-icon> Top 3
              </v-chip>
            </div>

            <v-avatar color="brown-lighten-4" size="38" class="mb-1 border border-brown">
              <v-img v-if="!top3.isEmpty" :src="getAvatarUrl(top3)" alt="Avatar" />
              <v-icon v-else color="brown-darken-2" size="small">mdi-account</v-icon>
            </v-avatar>

            <div class="text-caption font-weight-black name-wrap mb-1" :class="top3.isEmpty ? 'text-grey' : 'text-grey-darken-3'">
              {{ top3.isEmpty ? 'Đang trống' : formatDisplayName(top3.name) }}
            </div>

            <v-chip v-if="top3.badge_title" label size="x-small" color="brown" variant="tonal" class="mb-1 px-1" style="font-size: 9px;">
              {{ top3.badge_title }}
            </v-chip>
            <div class="text-caption font-weight-black" :class="top3.isEmpty ? 'text-grey' : 'text-primary'">
              {{ top3.isEmpty ? '--/10' : `${(top3.best_score ?? top3.avg_score ?? 0).toFixed(1).replace('.', ',')}/10` }}
            </div>
            <div class="text-caption text-grey font-weight-bold" style="font-size: 10px;">
              <v-icon size="x-small" color="deep-orange">mdi-fire</v-icon> {{ top3.streak_count || top3.streak || 1 }} ngày
            </div>
          </v-card>
        </v-col>
      </v-row>

      <!-- Full Top 10 Ranking Table -->
      <v-card border flat class="pa-2 pa-sm-3 bg-white" rounded="lg">
        <div class="text-subtitle-2 font-weight-black text-secondary mb-2 d-flex align-center ga-1">
          <v-icon color="secondary" size="small">mdi-format-list-numbered</v-icon>
          <span>Danh sách Bảng Vàng (Top 10)</span>
        </div>

        <v-card v-if="leaderboard.length === 0" border flat class="pa-6 pa-sm-8 text-center bg-white" rounded="lg">
          <v-avatar color="amber-lighten-5" size="64" class="mb-3 text-amber-darken-3 border border-amber">
            <v-icon size="large">mdi-trophy-award</v-icon>
          </v-avatar>
          <div class="text-subtitle-1 font-weight-black text-secondary mb-1">
            Đấu Trường Chưa Có Bài Luyện Tập Nào!
          </div>
          <div class="text-caption text-grey-darken-1 mb-4" style="max-width: 480px; margin: 0 auto; line-height: 1.5;">
            Em hãy hoàn thành bài luyện nói đầu tiên để vinh danh tên mình đứng vị trí Top 1 Bảng Vàng nhé!
          </div>
          <v-btn color="primary" variant="flat" to="/" prepend-icon="mdi-microphone" class="font-weight-black text-none">
            Bắt đầu Luyện Nói Ngay
          </v-btn>
        </v-card>

        <v-list v-else class="pa-0 border rounded-lg overflow-hidden">
          <v-list-item
            v-for="(user, idx) in leaderboard"
            :key="user.user_id"
            :class="{'bg-blue-lighten-5': user.user_id === currentUserId}"
            class="border-b py-2 px-2 px-sm-3"
          >
            <template #prepend>
              <div class="d-flex align-center justify-center mr-2 font-weight-black flex-shrink-0" style="width: 28px;">
                <v-icon v-if="idx === 0" color="amber-darken-2" size="medium">mdi-crown</v-icon>
                <v-icon v-else-if="idx === 1" color="grey-darken-1" size="medium">mdi-medal-outline</v-icon>
                <v-icon v-else-if="idx === 2" color="brown-darken-2" size="medium">mdi-medal-outline</v-icon>
                <span v-else class="text-caption font-weight-black text-grey-darken-1">#{{ idx + 1 }}</span>
              </div>

              <v-avatar size="36" color="grey-lighten-3" class="mr-3 border flex-shrink-0">
                <v-img :src="getAvatarUrl(user)" alt="Avatar" />
              </v-avatar>
            </template>

            <v-list-item-title class="font-weight-black text-caption text-sm-subtitle-2 text-grey-darken-4 text-truncate">
              {{ formatDisplayName(user.name) }}
            </v-list-item-title>

            <v-list-item-subtitle class="text-caption text-grey d-flex align-center flex-wrap ga-1 mt-1" style="font-size: 11px;">
              <v-chip v-if="user.user_id === currentUserId" label size="x-small" color="success" variant="flat" class="mr-1 font-weight-bold" style="font-size: 9px; height: 18px;">
                Bạn
              </v-chip>
              <v-chip v-if="user.badge_title" label size="x-small" color="primary" variant="tonal" style="font-size: 9px; height: 18px;">
                {{ user.badge_title }}
              </v-chip>
              <span class="font-weight-bold text-grey-darken-2">{{ user.total_sessions || user.total_practices || 0 }} bài tập</span>
              <span>•</span>
              <span class="font-weight-bold text-deep-orange"><v-icon size="x-small" color="deep-orange">mdi-fire</v-icon>{{ user.streak_count || user.streak || 1 }} ngày</span>
            </v-list-item-subtitle>

            <template #append>
              <div class="text-right flex-shrink-0 pl-2">
                <div class="text-subtitle-2 font-weight-black text-primary">
                  {{ (user.best_score || user.avg_score || 0).toFixed(1).replace('.', ',') }}/10
                </div>
                <div class="text-caption text-grey font-weight-bold" style="font-size: 10px;">
                  TB: {{ (user.avg_score || 0).toFixed(1).replace('.', ',') }}
                </div>
              </div>
            </template>
          </v-list-item>
        </v-list>
      </v-card>
    </div>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  backendUrl: {
    type: String,
    required: true
  },
  currentUserId: {
    type: Number,
    default: null
  }
})

const leaderboard = ref([])
const isLoading = ref(false)

const top1 = computed(() => leaderboard.value[0] || { name: 'Đang trống', best_score: '--', streak_count: 0, isEmpty: true })
const top2 = computed(() => leaderboard.value[1] || { name: 'Đang trống', best_score: '--', streak_count: 0, isEmpty: true })
const top3 = computed(() => leaderboard.value[2] || { name: 'Đang trống', best_score: '--', streak_count: 0, isEmpty: true })

const formatDisplayName = (nameStr) => {
  if (!nameStr) return 'Học sinh'
  if (nameStr.startsWith('guest_')) {
    const parts = nameStr.split('@')[0].split('_')
    const subId = parts[1] ? parts[1].slice(-4) : ''
    return `Học Sinh Khách #${subId}`
  }
  return nameStr
}

const getAvatarUrl = (user) => {
  if (!user || user.isEmpty) return ''
  const avatar = user.avatar_url || user.avatar
  if (avatar && typeof avatar === 'string' && avatar.trim() !== '') {
    return avatar
  }
  const name = user.name || 'Học Sinh'
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=673AB7&color=fff&bold=true`
}

const fetchLeaderboard = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/leaderboard`)
    if (res.ok) {
      const data = await res.json()
      leaderboard.value = Array.isArray(data) ? data : (data.leaderboard || [])
    }
  } catch (err) {
    console.error('Error fetching leaderboard:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchLeaderboard()
})
</script>

<style scoped>
.name-wrap {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
  line-height: 1.2;
  min-height: 26px;
  font-size: 11px;
}
</style>
