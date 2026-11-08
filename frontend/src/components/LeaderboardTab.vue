<template>
  <v-container fluid class="pa-0">
    <!-- Header Card (Kids 3D Champions Banner) -->
    <v-card id="tour-leaderboard-banner" class="pa-4 mb-4 kids-card-hero kids-gradient-gold">
      <div class="d-flex align-center justify-space-between flex-wrap ga-2">
        <div class="d-flex align-center ga-2 ga-sm-3">
          <div class="kids-floating d-flex align-center justify-center" style="width: 52px; height: 52px; background: rgba(255,255,255,0.45); border-radius: 16px;">
            <img src="/assets/kids/icon-leaderboard-duo.svg" alt="Trophy" style="width: 44px; height: 44px; object-fit: contain;" />
          </div>
          <div>
            <div class="text-subtitle-1 text-sm-h6 font-weight-black tracking-tight leading-tight" style="color: #3E2723;">CHAMPIONS LEADERBOARD 🏆</div>
            <div class="text-caption font-weight-bold d-flex align-center ga-1 mt-0.5" style="color: #4E342E;">
              <span>Star Standings & Top Speakers</span>
            </div>
          </div>
        </div>
        <div class="d-flex align-center ga-1">
          <v-btn
            icon="mdi-lightbulb-on-outline"
            size="small"
            variant="flat"
            class="kids-btn-3d kids-btn-white"
            title="Xem hướng dẫn Bảng vinh danh"
            @click="replayLeaderboardTour"
          />
          <button
            class="kids-btn-3d kids-btn-white px-3 py-2 text-caption font-weight-black"
            :disabled="isLoading"
            @click="fetchLeaderboard"
          >
            <v-icon size="small" class="mr-1">mdi-refresh</v-icon> Refresh Standings
          </button>
        </div>
      </div>
    </v-card>

    <div v-if="isLoading" class="d-flex flex-column align-center justify-center py-12">
      <v-progress-circular indeterminate color="primary" size="48" width="4" class="mb-3" />
      <div class="text-caption font-weight-bold text-grey-darken-1">Loading Arena Standings...</div>
    </div>

    <div v-else>
      <p class="text-caption my-3">Ranked by average score, then practice count. Classroom scores include educator adjustments.</p>
      <!-- 3D Champions Podium (Top 2 | Top 1 | Top 3) -->
      <v-row id="tour-leaderboard-podium" class="ma-0 mb-5 align-end justify-center ga-2 ga-sm-4">
        <!-- Top 2 (Silver Pedestal) -->
        <v-col cols="4" sm="3" class="pa-1">
          <div
            class="kids-card pa-3 text-center"
            style="background: linear-gradient(180deg, #F8FAFC 0%, #E2E8F0 100%) !important; border: 3px solid #94A3B8 !important; border-bottom: 6px solid #64748B !important; border-radius: 22px !important;"
          >
            <div class="d-flex align-center justify-center mb-2">
              <span class="kids-badge-bubble badge-white">
                🥈 TOP 2
              </span>
            </div>

            <div class="position-relative d-inline-block mb-2">
              <v-avatar color="grey-lighten-4" size="48" style="border: 2.5px solid #94A3B8;">
                <v-img v-if="!top2.isEmpty && top2.avatar_url" :src="top2.avatar_url" alt="Avatar" />
                <v-icon v-else size="28" color="blue-grey-darken-2">mdi-account-star</v-icon>
              </v-avatar>
            </div>

            <div class="text-caption text-sm-body-2 font-weight-black text-grey-darken-4 text-truncate mb-1">
              {{ top2.isEmpty ? 'Vacant' : formatDisplayName(top2.name) }}
            </div>

            <div class="text-h6 font-weight-black text-blue-grey-darken-4 my-1">
              {{ top2.isEmpty ? '--/10' : `${(top2.avg_score ?? top2.best_score ?? 0).toFixed(1).replace('.', ',')}/10` }}
            </div>

            <div class="kids-pill-badge" style="background: #E2E8F0; color: #334155; font-size: 11px;">
              <v-icon size="x-small" color="deep-orange">mdi-fire</v-icon>
              <span>{{ top2.streak_count ?? top2.streak ?? 0 }}d</span>
            </div>
          </div>
        </v-col>

        <!-- Top 1 (Gold Pedestal - Center & Highest) -->
        <v-col cols="4" sm="4" class="pa-1">
          <div
            class="kids-card pa-3 pa-sm-4 text-center"
            style="background: linear-gradient(180deg, #FFFBEB 0%, #FEF3C7 100%) !important; border: 3.5px solid #F59E0B !important; border-bottom: 8px solid #D97706 !important; border-radius: 26px !important; box-shadow: 0 12px 28px rgba(245, 158, 11, 0.22) !important; transform: translateY(-10px);"
          >
            <div class="d-flex align-center justify-center mb-2">
              <span class="kids-badge-bubble badge-yellow">
                👑 TOP 1
              </span>
            </div>

            <div class="position-relative d-inline-block mb-2">
              <v-avatar color="amber-lighten-4" size="56" style="border: 3.5px solid #F59E0B; box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35);">
                <v-img v-if="!top1.isEmpty && top1.avatar_url" :src="top1.avatar_url" alt="Avatar" />
                <v-icon v-else size="34" color="amber-darken-4">mdi-crown</v-icon>
              </v-avatar>
              <span style="position: absolute; bottom: -5px; right: -5px; font-size: 18px;">⭐</span>
            </div>

            <div class="text-subtitle-2 text-sm-subtitle-1 font-weight-black text-amber-darken-4 text-truncate mb-1">
              {{ top1.isEmpty ? 'Vacant' : formatDisplayName(top1.name) }}
            </div>

            <div class="text-h5 text-sm-h4 font-weight-black text-amber-darken-4 my-1">
              {{ top1.isEmpty ? '--/10' : `${(top1.avg_score ?? top1.best_score ?? 0).toFixed(1).replace('.', ',')}/10` }}
            </div>

            <div class="kids-pill-badge kids-pill-gold mt-1">
              <v-icon size="x-small" color="deep-orange">mdi-fire</v-icon>
              <span>{{ top1.streak_count ?? top1.streak ?? 0 }}d streak</span>
            </div>
          </div>
        </v-col>

        <!-- Top 3 (Bronze Pedestal) -->
        <v-col cols="4" sm="3" class="pa-1">
          <div
            class="kids-card pa-3 text-center"
            style="background: linear-gradient(180deg, #FFF7ED 0%, #FFEDD5 100%) !important; border: 3px solid #D97706 !important; border-bottom: 6px solid #B45309 !important; border-radius: 22px !important;"
          >
            <div class="d-flex align-center justify-center mb-2">
              <span class="kids-badge-bubble badge-yellow">
                🥉 TOP 3
              </span>
            </div>

            <div class="position-relative d-inline-block mb-2">
              <v-avatar color="orange-lighten-5" size="48" style="border: 2.5px solid #D97706;">
                <v-img v-if="!top3.isEmpty && top3.avatar_url" :src="top3.avatar_url" alt="Avatar" />
                <v-icon v-else size="28" color="orange-darken-4">mdi-account-star</v-icon>
              </v-avatar>
            </div>

            <div class="text-caption text-sm-body-2 font-weight-black text-grey-darken-4 text-truncate mb-1">
              {{ top3.isEmpty ? 'Vacant' : formatDisplayName(top3.name) }}
            </div>

            <div class="text-h6 font-weight-black text-deep-orange-darken-4 my-1">
              {{ top3.isEmpty ? '--/10' : `${(top3.avg_score ?? top3.best_score ?? 0).toFixed(1).replace('.', ',')}/10` }}
            </div>

            <div class="kids-pill-badge kids-pill-gold" style="font-size: 11px;">
              <v-icon size="x-small" color="deep-orange">mdi-fire</v-icon>
              <span>{{ top3.streak_count ?? top3.streak ?? 0 }}d</span>
            </div>
          </div>
        </v-col>
      </v-row>

      <!-- Gamified Champions Arena Standings List (Photo 3 Style) -->
      <div id="tour-leaderboard-list" class="kids-card pa-4 bg-white">
        <div class="d-flex align-center justify-space-between mb-3 border-b pb-2">
          <div class="kids-badge-bubble badge-purple">
            <v-icon size="x-small">mdi-trophy-variant</v-icon>
            <span>ARENA STANDINGS</span>
          </div>
          <span class="text-caption font-weight-black text-grey-darken-1">Ranked by Average Score & Streak</span>
        </div>

        <div class="d-flex flex-column ga-2.5">
          <div
            v-for="item in leaderboard"
            :key="item.user_id"
            class="kids-choice-card"
            :class="{ 'is-selected': item.user_id === currentUserId }"
            style="padding: 12px 18px !important; cursor: default;"
          >
            <!-- Rank Badge -->
            <span
              class="kids-choice-num flex-shrink-0"
              :style="item.rank === 1 ? 'background: #FEF08A; border-color: #D97706; color: #92400E;' : item.rank === 2 ? 'background: #E2E8F0; border-color: #64748B; color: #334155;' : item.rank === 3 ? 'background: #FFEDD5; border-color: #B45309; color: #9A3412;' : 'background: #F1F5F9; border-color: #94A3B8; color: #475569;'"
            >
              {{ item.rank }}
            </span>

            <!-- Learner Avatar & Name -->
            <div class="d-flex align-center ga-3 flex-grow-1 overflow-hidden pr-2">
              <v-avatar size="38" color="indigo-lighten-4" class="border flex-shrink-0">
                <v-img v-if="item.avatar_url" :src="item.avatar_url" alt="Avatar" />
                <v-icon v-else size="24" :color="item.rank === 1 ? 'amber-darken-3' : 'indigo-darken-2'">
                  {{ item.rank === 1 ? 'mdi-crown' : 'mdi-account-star' }}
                </v-icon>
              </v-avatar>

              <div class="overflow-hidden">
                <div class="font-weight-black text-body-1 text-slate-800 text-truncate d-flex align-center ga-1">
                  <span>{{ formatDisplayName(item.name) }}</span>
                  <span v-if="item.user_id === currentUserId" class="kids-pill-badge kids-pill-sky" style="font-size: 10px; padding: 2px 8px;">YOU ⭐</span>
                </div>
                <div v-if="item.badge_title" class="text-caption text-grey font-weight-bold" style="font-size: 11px;">
                  {{ item.badge_title }}
                </div>
              </div>
            </div>

            <!-- Score & Streak Badges -->
            <div class="d-flex align-center ga-2 flex-shrink-0 flex-wrap justify-end">
              <span class="kids-pill-badge kids-pill-sky text-body-2 font-weight-black">
                ⭐ {{ (item.avg_score ?? item.best_score ?? 0).toFixed(1).replace('.', ',') }}/10
              </span>
              <span class="kids-pill-badge kids-pill-gold text-caption font-weight-black">
                🔥 {{ item.streak_count ?? item.streak ?? 0 }}d
              </span>
              <span class="text-caption font-weight-black text-grey-darken-1 d-none d-sm-inline">
                🎯 {{ item.total_practices || item.total_sessions || 0 }} sessions
              </span>
            </div>
          </div>

          <div v-if="!leaderboard.length" class="text-center pa-8 text-body-2 text-grey font-weight-bold">
            No rankings recorded yet in this category. Be the first to practice and claim top spot!
          </div>
        </div>
      </div>
    </div>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  runTour,
  TOUR_KEYS,
  STUDENT_LEADERBOARD_TOUR_STEPS
} from '@/utils/tours.js'

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

const activeCategory = ref('freemium')
const leaderboard = ref([])
const isLoading = ref(false)

const top1 = computed(() => leaderboard.value[0] || { name: 'Empty Slot', best_score: '--', streak_count: 0, isEmpty: true })
const top2 = computed(() => leaderboard.value[1] || { name: 'Empty Slot', best_score: '--', streak_count: 0, isEmpty: true })
const top3 = computed(() => leaderboard.value[2] || { name: 'Empty Slot', best_score: '--', streak_count: 0, isEmpty: true })

const formatDisplayName = (nameStr) => {
  if (!nameStr) return 'Learner'
  if (nameStr.startsWith('Học Sinh Khách #') || nameStr.startsWith('Guest Learner #')) {
    const subId = nameStr.split('#')[1]
    return `Guest Learner #${subId}`
  }
  if (nameStr.startsWith('guest_')) {
    const parts = nameStr.split('@')[0].split('_')
    const subId = parts[1] ? parts[1].slice(-4) : ''
    return `Guest Learner #${subId}`
  }
  return nameStr
}

const getAvatarUrl = (user) => {
  if (!user || user.isEmpty) return ''
  const avatar = user.avatar_url || user.avatar
  if (avatar && typeof avatar === 'string' && avatar.trim() !== '') {
    return avatar
  }
  const name = user.name || 'Learner'
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=673AB7&color=fff&bold=true`
}

const checkAccountTypeAndSetTab = async () => {
  if (!props.currentUserId) return
  try {
    const res = await fetch(`${props.backendUrl}/api/assignments/student/${props.currentUserId}`)
    if (res.ok) {
      const data = await res.json()
      if (data.assignments && data.assignments.length > 0) {
        activeCategory.value = 'classroom'
      }
    }
  } catch (e) {
    console.error('Check student enrollment error:', e)
  }
}

const fetchLeaderboard = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/leaderboard?mode=${activeCategory.value}`)
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

onMounted(async () => {
  await checkAccountTypeAndSetTab()
  fetchLeaderboard()
  setTimeout(() => {
    runTour(TOUR_KEYS.STUDENT_LEADERBOARD, STUDENT_LEADERBOARD_TOUR_STEPS)
  }, 1000)
})

const replayLeaderboardTour = () => {
  runTour(TOUR_KEYS.STUDENT_LEADERBOARD, STUDENT_LEADERBOARD_TOUR_STEPS, true)
}
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
