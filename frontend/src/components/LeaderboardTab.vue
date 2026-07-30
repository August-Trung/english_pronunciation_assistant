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
            <div class="text-subtitle-1 text-sm-h6 font-weight-black tracking-tight leading-tight">PRONUNCIATION ARENA LEADERBOARD</div>
            <div class="text-caption text-indigo-lighten-4 font-weight-bold">
              {{ activeCategory === 'classroom' ? 'Classroom Enrolled Honor Roll' : 'Global Independent Learners Standings' }}
            </div>
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
          Refresh Standings
        </v-btn>
      </div>
    </v-card>

    <!-- Leaderboard Category Sub-Tabs (Auto-selected by Account Type) -->
    <v-card border flat class="pa-2 mb-4 bg-white rounded-lg">
      <v-tabs v-model="activeCategory" color="indigo-darken-3" align-tabs="center" density="comfortable" @update:model-value="fetchLeaderboard">
        <v-tab value="freemium" class="font-weight-black text-none" prepend-icon="mdi-account-star-outline">
          Independent Learners
        </v-tab>
        <v-tab value="classroom" class="font-weight-black text-none" prepend-icon="mdi-google-classroom">
          Classroom Enrolled
        </v-tab>
      </v-tabs>
    </v-card>

    <div v-if="isLoading" class="d-flex flex-column align-center justify-center py-12">
      <v-progress-circular indeterminate color="primary" size="48" width="4" class="mb-3" />
      <div class="text-caption font-weight-bold text-grey-darken-1">Loading Arena Standings...</div>
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
              {{ top2.isEmpty ? 'Vacant' : formatDisplayName(top2.name) }}
            </div>

            <v-chip v-if="top2.badge_title" label size="x-small" color="grey-darken-2" variant="tonal" class="mb-1 px-1" style="font-size: 9px;">
              {{ top2.badge_title }}
            </v-chip>
            <div class="text-caption font-weight-black" :class="top2.isEmpty ? 'text-grey' : 'text-primary'">
              {{ top2.isEmpty ? '--/10' : `${(top2.best_score ?? top2.avg_score ?? 0).toFixed(1).replace('.', ',')}/10` }}
            </div>
            <div class="text-caption text-grey font-weight-bold" style="font-size: 10px;">
              <v-icon size="x-small" color="deep-orange">mdi-fire</v-icon> {{ top2.streak_count || top2.streak || 1 }}d
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

            <div class="text-subtitle-2 font-weight-black name-wrap mb-1" :class="top1.isEmpty ? 'text-grey' : 'text-amber-darken-4'">
              {{ top1.isEmpty ? 'Vacant' : formatDisplayName(top1.name) }}
            </div>

            <v-chip v-if="top1.badge_title" label size="x-small" color="amber-darken-3" variant="flat" class="mb-1 px-1" style="font-size: 9px;">
              {{ top1.badge_title }}
            </v-chip>
            <div class="text-subtitle-2 font-weight-black text-amber-darken-4">
              {{ top1.isEmpty ? '--/10' : `${(top1.best_score ?? top1.avg_score ?? 0).toFixed(1).replace('.', ',')}/10` }}
            </div>
            <div class="text-caption text-grey-darken-2 font-weight-bold" style="font-size: 11px;">
              <v-icon size="x-small" color="deep-orange">mdi-fire</v-icon> {{ top1.streak_count || top1.streak || 1 }}d streak
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

            <v-avatar color="brown-lighten-4" size="38" class="mb-1 border">
              <v-img v-if="!top3.isEmpty" :src="getAvatarUrl(top3)" alt="Avatar" />
              <v-icon v-else color="brown" size="small">mdi-account</v-icon>
            </v-avatar>

            <div class="text-caption font-weight-black name-wrap mb-1" :class="top3.isEmpty ? 'text-grey' : 'text-grey-darken-3'">
              {{ top3.isEmpty ? 'Vacant' : formatDisplayName(top3.name) }}
            </div>

            <v-chip v-if="top3.badge_title" label size="x-small" color="brown" variant="tonal" class="mb-1 px-1" style="font-size: 9px;">
              {{ top3.badge_title }}
            </v-chip>
            <div class="text-caption font-weight-black" :class="top3.isEmpty ? 'text-grey' : 'text-primary'">
              {{ top3.isEmpty ? '--/10' : `${(top3.best_score ?? top3.avg_score ?? 0).toFixed(1).replace('.', ',')}/10` }}
            </div>
            <div class="text-caption text-grey font-weight-bold" style="font-size: 10px;">
              <v-icon size="x-small" color="deep-orange">mdi-fire</v-icon> {{ top3.streak_count || top3.streak || 1 }}d
            </div>
          </v-card>
        </v-col>
      </v-row>

      <!-- Remaining Rankings Table (Ranks 4 - 10) -->
      <v-card border flat class="bg-white elevation-1 rounded-lg">
        <v-table density="comfortable" hover>
          <thead>
            <tr class="bg-grey-lighten-4">
              <th class="text-center font-weight-black text-caption text-secondary" style="width: 50px;">RANK</th>
              <th class="font-weight-black text-caption text-secondary">LEARNER</th>
              <th class="text-center font-weight-black text-caption text-secondary">BEST SCORE</th>
              <th class="text-center font-weight-black text-caption text-secondary">STREAK</th>
              <th class="text-center font-weight-black text-caption text-secondary">PRACTICES</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in leaderboard"
              :key="item.user_id"
              :class="{ 'bg-amber-lighten-5': item.user_id === currentUserId }"
            >
              <td class="text-center font-weight-black text-caption">
                <v-chip size="x-small" :color="item.rank <= 3 ? 'amber-darken-3' : 'grey'" variant="flat" class="font-weight-black">
                  #{{ item.rank }}
                </v-chip>
              </td>
              <td>
                <div class="d-flex align-center ga-2">
                  <v-avatar size="32" color="indigo-lighten-5" class="border">
                    <v-img :src="getAvatarUrl(item)" alt="Avatar" />
                  </v-avatar>
                  <div>
                    <div class="font-weight-black text-body-2 text-secondary">
                      {{ formatDisplayName(item.name) }}
                      <v-chip v-if="item.user_id === currentUserId" color="primary" size="x-small" class="ml-1 font-weight-bold">YOU</v-chip>
                    </div>
                    <div v-if="item.badge_title" class="text-caption text-grey">
                      {{ item.badge_title }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="text-center font-weight-black text-primary">
                {{ (item.best_score ?? item.avg_score ?? 0).toFixed(1).replace('.', ',') }}/10
              </td>
              <td class="text-center text-caption font-weight-bold">
                <v-chip size="x-small" color="deep-orange" variant="tonal" class="font-weight-black">
                  🔥 {{ item.streak_count || item.streak || 1 }}d
                </v-chip>
              </td>
              <td class="text-center text-caption font-weight-bold text-grey-darken-2">
                {{ item.total_practices || item.total_sessions || 0 }} sessions
              </td>
            </tr>
            <tr v-if="!leaderboard.length">
              <td colspan="5" class="text-center pa-8 text-caption text-grey font-weight-bold">
                No rankings recorded yet in this category. Be the first to practice and claim top spot!
              </td>
            </tr>
          </tbody>
        </v-table>
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
