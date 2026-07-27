<template>
  <v-app class="bg-slate-50 text-slate-800 font-sans selection:bg-sky-200 selection:text-sky-900">
    <!-- TOP ENERGY BAR (THANH NĂNG LƯỢNG ĐỈNH MÀN HÌNH) -->
    <v-app-bar flat border color="white" density="comfortable" class="px-3 px-md-6 border-b border-slate-200/80">
      <div class="d-flex align-center justify-space-between w-100 ga-3">
        <!-- Brand Logo & Title -->
        <div class="d-flex align-center ga-3 cursor-pointer" @click="router.push('/')">
          <v-avatar color="sky-lighten-5" size="42" class="border border-sky-200 shadow-sm">
            <v-icon color="sky-darken-2" size="26">mdi-emoticon-outline</v-icon>
          </v-avatar>
          <div>
            <div class="text-subtitle-1 font-weight-black text-sky-darken-3 tracking-tight leading-none mb-1">
              FLUENT STUDIO
            </div>
            <div class="text-caption font-weight-bold text-slate-500" style="font-size: 10.5px;">
              Luyện Phát Âm & Ngữ Điệu Chuẩn Quốc Tế
            </div>
          </div>
        </div>

        <!-- Central Quick Gamification Stats -->
        <div class="d-none d-md-flex align-center ga-2 bg-slate-100 pa-1.5 px-3 rounded-full border border-slate-200">
          <!-- Level Badge -->
          <v-chip color="indigo-darken-2" size="small" variant="flat" class="font-weight-black">
            <v-icon start size="x-small">mdi-school</v-icon>
            Level {{ userLevel }}
          </v-chip>

          <!-- Streak Fire Badge -->
          <v-chip color="deep-orange-darken-1" size="small" variant="flat" class="font-weight-black">
            <v-icon start size="x-small">mdi-fire</v-icon>
            {{ streakDays }} Ngày Streak
          </v-chip>

          <!-- XP Points Badge -->
          <v-chip color="amber-darken-3" size="small" variant="flat" class="font-weight-black">
            <v-icon start size="x-small">mdi-star</v-icon>
            {{ totalXp }} XP
          </v-chip>
        </div>

        <!-- User Profile & Settings Quick Action -->
        <div class="d-flex align-center ga-2">
          <v-btn
            v-if="!user"
            color="primary"
            variant="flat"
            size="small"
            class="font-weight-black text-none px-4 rounded-lg"
            prepend-icon="mdi-account-circle-outline"
            @click="showLoginModal = true"
          >
            Đăng nhập
          </v-btn>

          <v-menu v-else location="bottom end">
            <template #activator="{ props }">
              <v-avatar
                v-bind="props"
                size="38"
                class="cursor-pointer border border-sky-300 elevation-1"
              >
                <v-img :src="userAvatarUrl" alt="User Avatar" />
              </v-avatar>
            </template>
            <v-list density="compact" rounded="lg" class="pa-2 border elevation-2" style="min-width: 180px;">
              <v-list-item class="px-2 mb-1">
                <div class="text-caption font-weight-black text-slate-800">{{ user.name || user.email }}</div>
                <div class="text-caption text-slate-500 font-weight-medium" style="font-size: 10px;">{{ user.email }}</div>
              </v-list-item>
              <v-divider class="my-1" />
              <v-list-item prepend-icon="mdi-account-outline" title="Hồ sơ cá nhân" value="profile" @click="router.push('/profile')" />
              <v-list-item prepend-icon="mdi-cog-outline" title="Cài đặt hệ thống" value="settings" @click="router.push('/settings')" />
              <v-divider class="my-1" />
              <v-list-item prepend-icon="mdi-logout-variant" title="Đăng xuất" color="error" value="logout" @click="logout" />
            </v-list>
          </v-menu>

          <!-- Toggle Right AI Panel (Mobile/Tablet) -->
          <v-btn
            icon="mdi-robot-outline"
            variant="tonal"
            color="sky-darken-2"
            density="comfortable"
            class="d-lg-none ml-1"
            @click="showAiPanel = !showAiPanel"
          />
        </div>
      </div>
    </v-app-bar>

    <!-- 3-COLUMN STUDIO LAYOUT CONTAINER -->
    <v-main class="bg-slate-50 min-h-screen">
      <v-container fluid class="pa-3 pa-md-5 max-w-7xl mx-auto">
        <v-row density="comfortable" class="ma-0 ga-4 align-start">
          
          <!-- COL 1: LEFT NAVIGATION RAIL (THANH ĐIỀU HƯỚNG DỌC CỐ ĐỊNH) -->
          <v-col cols="12" md="3" lg="2" class="pa-0">
            <v-card flat border rounded="xl" class="pa-3 bg-white border-slate-200/80 shadow-sm sticky top-20">
              <div class="text-caption font-weight-black text-slate-400 uppercase tracking-wider mb-2 px-2">
                Không Gian Học Tập
              </div>
              <div class="d-flex flex-column ga-1.5">
                <v-btn
                  v-for="nav in navItems"
                  :key="nav.route"
                  variant="flat"
                  :color="currentRoute === nav.route ? 'sky-lighten-5' : 'transparent'"
                  :class="currentRoute === nav.route ? 'text-sky-darken-3 font-weight-black border border-sky-200' : 'text-slate-600 font-weight-bold'"
                  class="justify-start text-none py-3 px-3 rounded-lg w-100 transition-all"
                  size="large"
                  @click="router.push(nav.route)"
                >
                  <template #prepend>
                    <v-icon :color="currentRoute === nav.route ? 'sky-darken-2' : 'slate-400'" size="22">
                      {{ nav.icon }}
                    </v-icon>
                  </template>
                  <span style="font-size: 13.5px;">{{ nav.title }}</span>
                </v-btn>
              </div>

              <v-divider class="my-3" />

              <!-- Quick Level Info Card -->
              <div class="pa-3 bg-sky-lighten-5 rounded-lg border border-sky-100">
                <div class="d-flex align-center justify-space-between mb-1">
                  <span class="text-caption font-weight-black text-sky-darken-4">Mục tiêu ngày</span>
                  <v-icon size="x-small" color="sky-darken-2">mdi-bullseye-arrow</v-icon>
                </div>
                <v-progress-linear :model-value="dailyProgressPct" color="sky-darken-2" height="6" rounded class="my-1.5" />
                <div class="d-flex justify-space-between text-caption font-weight-bold text-sky-darken-3" style="font-size: 10px;">
                  <span>Đã đạt {{ dailyCompleted }} bài</span>
                  <span>{{ dailyProgressPct }}%</span>
                </div>
              </div>
            </v-card>
          </v-col>

          <!-- COL 2: CENTER MAIN STUDIO STAGE (KHÔNG GIAN HỌC CHÍNH) -->
          <v-col cols="12" md="9" lg="7" class="pa-0">
            <router-view :backend-url="backendUrl" :user-id="user?.id" @user-updated="fetchUserData" />
          </v-col>

          <!-- COL 3: RIGHT AI CO-PILOT PANEL (TRỢ LÝ AI ĐỒNG HÀNH) -->
          <v-col cols="12" lg="3" class="pa-0 d-none d-lg-block">
            <v-card flat border rounded="xl" class="pa-4 bg-white border-slate-200/80 shadow-sm sticky top-20">
              <div class="d-flex align-center justify-space-between mb-3 border-b border-slate-100 pb-3">
                <div class="d-flex align-center ga-2">
                  <v-avatar color="indigo-lighten-5" size="34" class="border border-indigo-200">
                    <v-icon color="indigo-darken-2" size="20">mdi-robot-outline</v-icon>
                  </v-avatar>
                  <div>
                    <div class="text-subtitle-2 font-weight-black text-slate-800">Trợ Lý AI Đồng Hành</div>
                    <div class="text-caption font-weight-medium text-slate-500" style="font-size: 10px;">Phản hồi real-time</div>
                  </div>
                </div>
                <v-chip size="x-small" color="success" variant="flat" class="font-weight-black">Sẵn sàng</v-chip>
              </div>

              <!-- AI Status Feedback Container -->
              <div class="space-y-3 text-caption">
                <div class="bg-indigo-lighten-5 pa-3 rounded-lg border border-indigo-100">
                  <div class="font-weight-black text-indigo-darken-4 mb-1 d-flex align-center ga-1">
                    <v-icon size="x-small" color="indigo-darken-2">mdi-lightbulb-on-outline</v-icon>
                    <span>Lời Khuyên Sư Phạm:</span>
                  </div>
                  <div class="text-slate-700 leading-relaxed font-weight-medium" style="font-size: 11.5px;">
                    Hãy chú ý mở rộng vòm miệng khi đọc nguyên âm /æ/ trong các từ như "cat", "apple" và bật rõ phụ âm đuôi /t/, /s/!
                  </div>
                </div>

                <!-- Weak Words Box -->
                <div class="bg-amber-lighten-5 pa-3 rounded-lg border border-amber-200">
                  <div class="font-weight-black text-amber-darken-4 mb-1.5 d-flex align-center justify-space-between">
                    <span class="d-flex align-center ga-1">
                      <v-icon size="x-small" color="amber-darken-3">mdi-alert-circle-outline</v-icon>
                      <span>Từ Cần Ôn Lại:</span>
                    </span>
                    <v-btn variant="text" size="x-small" density="compact" class="text-amber-darken-4 font-weight-black text-none" @click="router.push('/flashcards')">
                      Xem hết
                    </v-btn>
                  </div>
                  <div class="d-flex flex-wrap ga-1.5">
                    <v-chip size="x-small" color="amber-darken-4" variant="tonal" class="font-weight-bold">
                      success (/səkˈsɛs/)
                    </v-chip>
                    <v-chip size="x-small" color="amber-darken-4" variant="tonal" class="font-weight-bold">
                      courage (/ˈkɜrɪdʒ/)
                    </v-chip>
                  </div>
                </div>
              </div>
            </v-card>
          </v-col>

        </v-row>
      </v-container>
    </v-main>

    <!-- LOGIN MODAL DIALOG -->
    <v-dialog v-model="showLoginModal" max-width="440">
      <v-card border rounded="2xl" class="pa-5 bg-white">
        <LoginPage :backend-url="backendUrl" @login-success="handleLoginSuccess" @close="showLoginModal = false" />
      </v-card>
    </v-dialog>

  </v-app>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import LoginPage from '@/components/LoginPage.vue'

const router = useRouter()
const route = useRoute()

const backendUrl = ref(localStorage.getItem('fluent_backend_url') || 'http://127.0.0.1:8000')
const user = ref(JSON.parse(localStorage.getItem('fluent_user') || 'null'))
const showLoginModal = ref(false)
const showAiPanel = ref(false)

const streakDays = ref(12)
const totalXp = ref(1450)
const userLevel = ref('A2')
const dailyCompleted = ref(3)
const dailyProgressPct = ref(60)

const navItems = [
  { route: '/', title: 'Luyện Nói', icon: 'mdi-microphone-outline' },
  { route: '/shadowing', title: 'Luyện Ngữ Điệu', icon: 'mdi-bookmark-music-outline' },
  { route: '/flashcards', title: 'Thẻ Từ Vựng', icon: 'mdi-cards-outline' },
  { route: '/leaderboard', title: 'Bảng Xếp Hạng', icon: 'mdi-trophy-outline' },
  { route: '/stats', title: 'Thống Kê & Báo Cáo', icon: 'mdi-chart-timeline-variant' },
]

const currentRoute = computed(() => route.path)

const userAvatarUrl = computed(() => {
  if (user.value?.avatar_url) return user.value.avatar_url
  const name = encodeURIComponent(user.value?.name || user.value?.email || 'Học Viên')
  return `https://ui-avatars.com/api/?name=${name}&background=0288D1&color=fff&bold=true`
})

const handleLoginSuccess = (userData) => {
  user.value = userData
  localStorage.setItem('fluent_user', JSON.stringify(userData))
  showLoginModal.value = false
}

const logout = () => {
  user.value = null
  localStorage.removeItem('fluent_user')
  localStorage.removeItem('fluent_token')
  router.push('/')
}

const fetchUserData = () => {
  const saved = localStorage.getItem('fluent_user')
  if (saved) {
    user.value = JSON.parse(saved)
  }
}

onMounted(() => {
  fetchUserData()
})
</script>
