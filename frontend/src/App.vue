<template>
  <v-app class="bg-background">
    <!-- Render Admin Dashboard if path is /admin -->
    <template v-if="isAdminRoute">
      <v-app-bar color="white" flat border class="px-4 px-md-8 px-lg-12">
        <div class="d-flex align-center w-100">
          <div class="d-flex align-center ga-2">
            <v-avatar color="indigo-lighten-5" size="36" class="text-indigo rounded-lg border">
              <v-icon size="default">mdi-shield-crown-outline</v-icon>
            </v-avatar>
            <div>
              <span class="text-subtitle-1 font-weight-black text-indigo tracking-tight">FLUENT ADMIN</span>
              <span class="text-caption font-weight-bold text-grey-darken-1 border-s ps-2 ml-2">
                Trang cấu hình nhà phát triển
              </span>
            </div>
          </div>
          <v-spacer />
          <v-btn
            color="primary"
            variant="outlined"
            size="small"
            class="text-none font-weight-bold"
            prepend-icon="mdi-home"
            @click="goToHome"
          >
            Quay lại trang học
          </v-btn>
        </div>
      </v-app-bar>

      <v-main class="pt-16">
        <v-container fluid class="px-4 px-md-8 px-lg-12 py-4">
          <v-row class="ma-0 ga-3">
            <!-- Col 1: Server Config -->
            <v-col cols="12" md="6" class="pa-1">
              <v-card border flat class="pa-4 bg-white" rounded="lg">
                <div class="d-flex align-center ga-2 mb-3">
                  <v-avatar color="indigo-lighten-5" size="36" class="text-indigo border">
                    <v-icon size="small">mdi-server-network</v-icon>
                  </v-avatar>
                  <div class="text-subtitle-1 font-weight-black text-secondary">Kết nối Máy chủ (API)</div>
                </div>

                <v-row class="ma-0 align-center ga-2">
                  <v-col cols="12" sm="8" class="pa-1">
                    <v-text-field
                      v-model="backendUrl"
                      label="Đường dẫn API máy chủ:"
                      placeholder="Ví dụ: https://agrse-fluent-english-backend.hf.space"
                      variant="outlined"
                      density="comfortable"
                      hide-details
                      color="primary"
                      prepend-inner-icon="mdi-link-variant"
                    />
                  </v-col>
                  <v-col cols="12" sm="4" class="pa-1">
                    <v-btn
                      color="primary"
                      variant="flat"
                      block
                      height="48"
                      class="font-weight-bold text-caption text-sm-body-2"
                      prepend-icon="mdi-transit-connection-variant"
                      :loading="isTestingConnection"
                      @click="testConnection"
                    >
                      Kiểm tra kết nối
                    </v-btn>
                  </v-col>
                </v-row>

                <v-alert
                  v-if="connectionStatus"
                  :type="connectionStatus.success ? 'success' : 'error'"
                  density="compact"
                  variant="tonal"
                  class="mt-3 py-2 text-caption text-sm-subtitle-2 font-weight-medium"
                  hide-details
                >
                  {{ connectionStatus.message }}
                </v-alert>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </v-main>
    </template>

    <!-- Normal Student Flow (Login / Main Workspace) -->
    <template v-else>
      <!-- Full Screen Loader while verifying login session -->
      <div v-if="isCheckingAuth" class="fill-height d-flex align-center justify-center bg-white" style="min-height: 100vh;">
        <v-progress-circular indeterminate color="teal" size="48" />
      </div>

      <!-- Login Screen when not logged in -->
      <LoginPage v-else-if="!isLoggedIn" @login="handleLogin" />

      <!-- Main Workspace after logging in -->
      <template v-else>
        <!-- Premium Modern App Bar -->
        <v-app-bar color="white" flat border class="px-2 px-md-8 px-lg-12">
          <div class="d-flex align-center w-100">
            <!-- Logo & Title Clickable Link to Home -->
            <router-link to="/" class="d-flex align-center ga-1 ga-sm-2 text-decoration-none text-grey-darken-4" style="cursor: pointer;">
              <img src="/logo-augusttrung.png" alt="August Trung Logo" height="34" class="mr-1 d-block" />
              <div>
                <span class="text-subtitle-1 font-weight-black text-primary tracking-tight">FLUENT</span>
                <span class="d-none d-md-inline text-caption font-weight-bold text-grey-darken-1 border-s ps-2 ml-2">
                  Luyện Phát Âm Tiếng Anh Học Đường
                </span>
              </div>
            </router-link>

            <!-- Desktop Navigation Pills -->
            <div class="d-none d-sm-flex align-center ga-1 ml-4">
              <v-btn to="/" variant="text" rounded="pill" density="comfortable" active-color="primary" prepend-icon="mdi-microphone" class="font-weight-bold text-none text-body-2">
                Luyện nói
              </v-btn>
              <v-btn to="/shadowing" variant="text" rounded="pill" density="comfortable" active-color="primary" prepend-icon="mdi-waveform" class="font-weight-bold text-none text-body-2">
                Luyện ngữ điệu
              </v-btn>
              <v-btn to="/leaderboard" variant="text" rounded="pill" density="comfortable" active-color="primary" prepend-icon="mdi-trophy-variant" class="font-weight-bold text-none text-body-2">
                Đấu trường
              </v-btn>
              <v-btn to="/stats" variant="text" rounded="pill" density="comfortable" active-color="primary" prepend-icon="mdi-chart-bar" class="font-weight-bold text-none text-body-2">
                Thống kê
              </v-btn>
              <v-btn to="/profile" variant="text" rounded="pill" density="comfortable" active-color="primary" prepend-icon="mdi-account-circle-outline" class="font-weight-bold text-none text-body-2">
                Hồ sơ
              </v-btn>
              <v-btn to="/settings" variant="text" rounded="pill" density="comfortable" active-color="primary" prepend-icon="mdi-cog-outline" class="font-weight-bold text-none text-body-2">
                Cài đặt
              </v-btn>
            </div>

            <v-spacer />

            <!-- Ultra Clean Right Actions (Streak + Avatar Dropdown Menu) -->
            <div class="d-flex align-center ga-2">
              <!-- Streak Badge -->
              <v-chip
                v-if="streak > 0"
                color="warning"
                variant="flat"
                density="comfortable"
                class="font-weight-black text-caption text-sm-body-2 px-2 px-sm-3"
                prepend-icon="mdi-fire"
              >
                <span class="d-none d-sm-inline">{{ streak }} ngày liên tiếp</span>
                <span class="d-inline d-sm-none">{{ streak }}d</span>
              </v-chip>

              <!-- Avatar Dropdown Menu -->
              <v-menu location="bottom end" transition="scale-transition">
                <template #activator="{ props: menuProps }">
                  <v-avatar
                    v-bind="menuProps"
                    size="36"
                    color="primary-lighten-4"
                    class="border cursor-pointer elevation-1"
                  >
                    <v-img v-if="userAvatar" :src="userAvatar" alt="Avatar" />
                    <v-icon v-else size="small" color="primary">mdi-account</v-icon>
                  </v-avatar>
                </template>

                <v-list class="pa-1 border rounded-lg shadow-lg" min-width="220">
                  <!-- User Header in Menu -->
                  <v-list-item class="border-b mb-1 pb-2">
                    <template #prepend>
                      <v-avatar size="32" color="primary-lighten-4" class="mr-2">
                        <v-img v-if="userAvatar" :src="userAvatar" />
                        <v-icon v-else size="x-small" color="primary">mdi-account</v-icon>
                      </v-avatar>
                    </template>
                    <v-list-item-title class="font-weight-black text-caption text-sm-subtitle-2">
                      {{ userName }}
                    </v-list-item-title>
                    <v-list-item-subtitle class="text-caption text-grey">
                      {{ equippedBadgeTitle || (userEmail ? 'Đã liên kết Cloud' : 'Học Sinh Khách') }}
                    </v-list-item-subtitle>
                  </v-list-item>

                  <!-- Menu Actions -->
                  <v-list-item class="rounded mb-1" prepend-icon="mdi-account-circle-outline" to="/profile">
                    <v-list-item-title class="text-caption font-weight-bold">Hồ sơ cá nhân</v-list-item-title>
                  </v-list-item>

                  <v-list-item class="rounded mb-1" prepend-icon="mdi-cards-outline" color="error" to="/flashcards">
                    <v-list-item-title class="text-caption font-weight-bold text-error">Ôn từ khó (Flashcard)</v-list-item-title>
                  </v-list-item>

                  <v-list-item class="rounded mb-1" prepend-icon="mdi-trophy-award" color="amber-darken-3" @click="showAchievements = true">
                    <v-list-item-title class="text-caption font-weight-bold text-amber-darken-4">Thành tựu & Danh hiệu</v-list-item-title>
                  </v-list-item>

                  <v-list-item class="rounded mb-1" prepend-icon="mdi-theme-light-dark" @click="cycleTheme">
                    <v-list-item-title class="text-caption font-weight-bold">Đổi giao diện Sáng/Tối</v-list-item-title>
                  </v-list-item>

                  <v-divider class="my-1" />

                  <v-list-item class="rounded" prepend-icon="mdi-logout" color="error" @click="confirmLogout">
                    <v-list-item-title class="text-caption font-weight-bold text-error">Đăng xuất</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </div>
          </div>
        </v-app-bar>

        <v-main class="pt-16 pb-16 pb-sm-4">
          <v-container fluid class="px-2 px-sm-4 px-md-8 px-lg-12 py-3">
            <!-- Dynamic Router View -->
            <router-view v-slot="{ Component }">
              <component
                :is="Component"
                :backend-url="backendUrl"
                :user-id="currentUserId"
                :user-name="userName"
                :user-email="userEmail"
                :user-avatar="userAvatar"
                :equipped-badge-title="equippedBadgeTitle"
                :streak="streak"
                :daily-goal="dailyGoal"
                :history="history"
                @history-updated="fetchUserAllData"
                @clear-history="clearHistory"
                @update-settings="updateSettings"
              />
            </router-view>
          </v-container>
        </v-main>

        <!-- Mobile Bottom Navigation Bar (Custom Pixel-Perfect Mobile Native UX) -->
        <nav class="custom-bottom-nav d-flex d-sm-none border-t bg-white elevation-4">
          <router-link to="/" class="nav-item" exact-active-class="nav-item-active">
            <v-icon size="18">mdi-microphone</v-icon>
            <span class="nav-label">Luyện nói</span>
          </router-link>

          <router-link to="/shadowing" class="nav-item" active-class="nav-item-active">
            <v-icon size="18">mdi-waveform</v-icon>
            <span class="nav-label">Ngữ điệu</span>
          </router-link>

          <router-link to="/leaderboard" class="nav-item" active-class="nav-item-active">
            <v-icon size="18">mdi-trophy-variant</v-icon>
            <span class="nav-label">Đấu trường</span>
          </router-link>

          <router-link to="/stats" class="nav-item" active-class="nav-item-active">
            <v-icon size="18">mdi-chart-bar</v-icon>
            <span class="nav-label">Thống kê</span>
          </router-link>

          <router-link to="/profile" class="nav-item" active-class="nav-item-active">
            <v-icon size="18">mdi-account-circle-outline</v-icon>
            <span class="nav-label">Hồ sơ</span>
          </router-link>
        </nav>

        <!-- Dialogs -->
        <ProfileDialog
          v-model="showProfile"
          :backend-url="backendUrl"
          :user-id="currentUserId"
          :user-name="userName"
          :user-email="userEmail"
          :user-avatar="userAvatar"
          :equipped-badge-title="equippedBadgeTitle"
          :streak="streak"
          :daily-goal="dailyGoal"
          @update-profile="updateSettings"
        />

        <AchievementsDialog
          v-model="showAchievements"
          :backend-url="backendUrl"
          :user-id="currentUserId"
          @badge-updated="fetchUserProfile"
        />

        <WeakWordsDialog
          v-model="showWeakWords"
          :backend-url="backendUrl"
          :user-id="currentUserId"
        />

        <!-- Logout Confirmation Dialog -->
        <v-dialog v-model="showLogoutDialog" max-width="400">
          <v-card border flat class="pa-4 bg-white" rounded="lg">
            <div class="d-flex align-center ga-3 mb-3">
              <v-avatar color="red-lighten-5" size="40" class="text-error border">
                <v-icon size="default">mdi-logout-variant</v-icon>
              </v-avatar>
              <div>
                <div class="text-subtitle-1 font-weight-black text-secondary">Xác nhận đăng xuất</div>
                <div class="text-caption text-grey-darken-1">Em có chắc chắn muốn đăng xuất không?</div>
              </div>
            </div>

            <div class="text-caption text-grey-darken-2 mb-4 bg-grey-lighten-4 pa-3 rounded border" style="line-height: 1.5;">
              💡 Khi đăng xuất, thiết bị của em sẽ tạm ngưng giữ phiên làm việc hiện tại. Em có thể đăng nhập lại bất cứ lúc nào!
            </div>

            <div class="d-flex align-center justify-end ga-2">
              <v-btn
                variant="outlined"
                color="grey-darken-1"
                class="font-weight-bold text-none"
                @click="showLogoutDialog = false"
              >
                Hủy bỏ
              </v-btn>
              <v-btn
                color="error"
                variant="flat"
                class="font-weight-bold text-none"
                prepend-icon="mdi-logout"
                @click="handleLogout"
              >
                Đăng xuất ngay
              </v-btn>
            </div>
          </v-card>
        </v-dialog>
      </template>
    </template>
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTheme } from 'vuetify'
import LoginPage from '@/components/LoginPage.vue'
import PracticeTab from '@/components/PracticeTab.vue'
import LeaderboardTab from '@/components/LeaderboardTab.vue'
import StatsTab from '@/components/StatsTab.vue'
import SettingsTab from '@/components/SettingsTab.vue'
import ProfileDialog from '@/components/ProfileDialog.vue'
import AchievementsDialog from '@/components/AchievementsDialog.vue'
import WeakWordsDialog from '@/components/WeakWordsDialog.vue'

const theme = useTheme()

// Routing
const isAdminRoute = ref(false)

const checkRoute = () => {
  isAdminRoute.value = window.location.pathname === '/admin'
}

const goToHome = () => {
  window.history.pushState({}, '', '/')
  checkRoute()
}

// State
const isLoggedIn = ref(false)
const isCheckingAuth = ref(true)
const currentUserId = ref(null)
const userEmail = ref('')
const userName = ref('')
const userAvatar = ref('')
const equippedBadgeTitle = ref('')
const dailyGoal = ref(5)
const streak = ref(0)
const history = ref([])

// Dialog states
const showProfile = ref(false)
const showAchievements = ref(false)
const showWeakWords = ref(false)
const showLogoutDialog = ref(false)

// Dev configurations
const backendUrl = ref('https://agrse-fluent-english-backend.hf.space')
const isTestingConnection = ref(false)
const connectionStatus = ref(null)

// Lifecycle - Load persistent device session
onMounted(async () => {
  checkRoute()
  window.addEventListener('popstate', checkRoute)

  const storedUrl = localStorage.getItem('speak_backend_url')
  if (storedUrl && !storedUrl.includes('august-trung-english-pronunciation-assistant')) {
    backendUrl.value = storedUrl
  } else {
    backendUrl.value = 'https://agrse-fluent-english-backend.hf.space'
  }

  try {
    const storedEmail = localStorage.getItem('speak_user_email')
    if (storedEmail) {
      userEmail.value = storedEmail
      await autoLoginByEmail(storedEmail)
    }
  } finally {
    isCheckingAuth.value = false
  }

  const storedTheme = localStorage.getItem('speak_theme')
  if (storedTheme) {
    theme.global.name.value = storedTheme
  }
})

// Auto login device session from Cloud DB
const autoLoginByEmail = async (emailVal) => {
  try {
    const cachedAvatar = localStorage.getItem('speak_user_avatar') || ''
    const cachedName = localStorage.getItem('speak_user_name') || ''
    const res = await fetch(`${backendUrl.value}/api/users/google-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: emailVal, name: cachedName, avatar: cachedAvatar })
    })
    if (res.ok) {
      const data = await res.json()
      if (data.success && data.user) {
        currentUserId.value = data.user.id
        userName.value = data.user.name || cachedName
        userEmail.value = data.user.email
        userAvatar.value = data.user.avatar || data.user.avatar_url || cachedAvatar
        dailyGoal.value = data.user.daily_goal || 5
        streak.value = data.user.streak_count || 1
        isLoggedIn.value = true
        
        if (data.user.avatar) localStorage.setItem('speak_user_avatar', data.user.avatar)
        if (data.user.name) localStorage.setItem('speak_user_name', data.user.name)
        
        await fetchUserAllData()
      }
    }
  } catch (err) {
    console.error('Auto login error:', err)
  }
}

// User Google / Email Login
const handleLogin = async (userData) => {
  try {
    const res = await fetch(`${backendUrl.value}/api/users/google-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    })
    if (res.ok) {
      const data = await res.json()
      if (data.success && data.user) {
        currentUserId.value = data.user.id
        userName.value = data.user.name || userData.name
        userEmail.value = data.user.email
        userAvatar.value = userData.avatar || data.user.avatar || data.user.avatar_url || ''
        dailyGoal.value = data.user.daily_goal || 5
        streak.value = data.user.streak_count || 1
        
        localStorage.setItem('speak_user_email', data.user.email)
        if (userAvatar.value) localStorage.setItem('speak_user_avatar', userAvatar.value)
        if (userName.value) localStorage.setItem('speak_user_name', userName.value)
        
        isLoggedIn.value = true
        
        await fetchUserAllData()
      }
    }
  } catch (err) {
    console.error('Login error:', err)
  }
}

const fetchUserAllData = async () => {
  await fetchUserProfile()
  await fetchUserHistory()
}

const fetchUserProfile = async () => {
  if (!currentUserId.value) return
  try {
    const res = await fetch(`${backendUrl.value}/api/users/${currentUserId.value}/profile`)
    if (res.ok) {
      const data = await res.json()
      userName.value = data.name || userName.value
      dailyGoal.value = data.daily_goal || 5
      streak.value = data.streak_count || 1
      
      // Fetch badge title if equipped
      if (data.equipped_badge) {
        const achRes = await fetch(`${backendUrl.value}/api/users/${currentUserId.value}/achievements`)
        if (achRes.ok) {
          const achs = await achRes.json()
          const eq = achs.find(a => a.code === data.equipped_badge)
          equippedBadgeTitle.value = eq ? eq.title : ''
        }
      } else {
        equippedBadgeTitle.value = ''
      }
    }
  } catch (err) {
    console.error('Fetch profile error:', err)
  }
}

const fetchUserHistory = async () => {
  if (!currentUserId.value) return
  try {
    const res = await fetch(`${backendUrl.value}/api/users/${currentUserId.value}/history`)
    if (res.ok) {
      const data = await res.json()
      history.value = Array.isArray(data) ? data : (data.history || [])
    }
  } catch (err) {
    console.error('Fetch history error:', err)
  }
}

const updateSettings = async (newSettings) => {
  if (newSettings.userName) userName.value = newSettings.userName
  if (newSettings.dailyGoal) dailyGoal.value = newSettings.dailyGoal

  if (currentUserId.value) {
    try {
      await fetch(`${backendUrl.value}/api/users/${currentUserId.value}/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newSettings.userName,
          daily_goal: newSettings.dailyGoal
        })
      })
    } catch (err) {
      console.error('Update settings error:', err)
    }
  }
}

const clearHistory = async () => {
  if (currentUserId.value) {
    try {
      await fetch(`${backendUrl.value}/api/users/${currentUserId.value}/history`, {
        method: 'DELETE'
      })
      history.value = []
    } catch (err) {
      console.error('Clear history error:', err)
    }
  }
}

const confirmLogout = () => {
  showLogoutDialog.value = true
}

const handleLogout = () => {
  localStorage.removeItem('speak_user_email')
  localStorage.removeItem('speak_user_avatar')
  localStorage.removeItem('speak_user_name')
  isLoggedIn.value = false
  currentUserId.value = null
  userEmail.value = ''
  userName.value = ''
  userAvatar.value = ''
  history.value = []
  showLogoutDialog.value = false
}

const cycleTheme = () => {
  theme.global.name.value = theme.global.name.value === 'light' ? 'dark' : 'light'
  localStorage.setItem('speak_theme', theme.global.name.value)
}

const testConnection = async () => {
  isTestingConnection.value = true
  connectionStatus.value = null
  try {
    const res = await fetch(`${backendUrl.value}/api/health`)
    if (res.ok) {
      const data = await res.json()
      connectionStatus.value = {
        success: true,
        message: `Kết nối thành công! Trạng thái: ${data.status}`
      }
    } else {
      connectionStatus.value = {
        success: false,
        message: `Lỗi kết nối máy chủ! Mã phản hồi: ${res.status}`
      }
    }
  } catch (e) {
    connectionStatus.value = {
      success: false,
      message: `Không thể truy cập đường dẫn API! ${e.message}`
    }
  } finally {
    isTestingConnection.value = false
  }
}
</script>

<style scoped>
.custom-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 56px;
  z-index: 1000;
  background: #ffffff;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: #64748b;
  padding: 4px 1px;
  transition: all 0.15s ease;
}

.nav-item-active {
  color: #1867c0 !important;
  font-weight: 800;
}

.nav-label {
  white-space: nowrap;
  font-size: 10px;
  line-height: 1;
  margin-top: 3px;
  letter-spacing: -0.3px;
}
</style>
