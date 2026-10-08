<template>
  <v-app class="bg-background">
    <!-- Full Screen Loader while verifying login session -->
    <div v-if="isCheckingAuth" class="fill-height d-flex flex-column align-center justify-center bg-white" style="min-height: 100vh;">
      <v-avatar color="primary-lighten-5" size="64" class="mb-4 elevation-1">
        <img src="/logo-augusttrung.png" alt="August Trung Logo" height="42" class="d-inline-block" />
      </v-avatar>
      <v-progress-circular indeterminate color="primary" size="44" width="4" class="mb-4" />
      <div class="text-subtitle-1 font-weight-bold text-grey-darken-3 tracking-tight">
        {{ authLoadingMessage }}
      </div>
      <div class="text-caption text-grey mt-1">Please wait a moment...</div>
    </div>

    <!-- Standalone Portal Routes (/teacher, /admin, /parent): Render router-view directly! -->
    <template v-else-if="isStandalonePortalRoute">
      <v-app-bar color="white" flat border class="px-4 px-md-8 px-lg-12">
        <div class="d-flex align-center w-100">
          <router-link :to="portalHomeRoute" class="d-flex align-center ga-1 ga-sm-2 text-decoration-none text-grey-darken-4" style="cursor: pointer;">
            <img src="/logo-augusttrung.png" alt="August Trung Logo" height="34" class="mr-1 d-block" />
            <div>
              <span class="text-subtitle-1 font-weight-black text-primary tracking-tight">FLUENT</span>
              <span class="d-none d-md-inline text-caption font-weight-bold text-grey-darken-1 border-s ps-2 ml-2">
                {{ portalSubtitle }}
              </span>
            </div>
          </router-link>
          <v-spacer />
          <v-btn color="primary" variant="outlined" size="small" class="text-none font-weight-bold" prepend-icon="mdi-home" @click="handleReturnToStudio">
            Return to Learning Studio
          </v-btn>
        </div>
      </v-app-bar>

      <v-main class="pt-16">
        <v-container fluid class="px-2 px-sm-4 px-md-8 px-lg-12 py-3">
          <router-view v-slot="{ Component }">
            <component
              :is="Component"
              :backend-url="backendUrl"
              :user-id="currentUserId"
              :user-role="userRole"
            />
          </router-view>
        </v-container>
      </v-main>
    </template>

    <!-- Normal Student Flow: Login Screen when not logged in -->
    <LoginPage v-else-if="!isLoggedIn" :backend-url="backendUrl" @login="handleLogin" />

    <!-- Main Workspace for logged in students -->
    <template v-else>
      <!-- Collapsible Modern Sidebar Navigation Drawer -->
      <v-navigation-drawer
        v-model="drawer"
        :rail="mdAndUp && isRail"
        :permanent="mdAndUp"
        width="240"
        rail-width="68"
        class="fluent-sidebar bg-white border-e elevation-0"
      >
        <!-- Brand Header inside Drawer -->
        <div class="sidebar-brand-header d-flex align-center px-3 py-3 border-b" :class="{ 'justify-center': mdAndUp && isRail }">
          <router-link to="/" class="d-flex align-center text-decoration-none overflow-hidden" :class="{ 'justify-center': mdAndUp && isRail }">
            <img src="/logo-augusttrung.png" alt="August Trung Logo" height="32" class="flex-shrink-0" />
            <div v-if="!mdAndUp || !isRail" class="ml-2 text-truncate">
              <div class="text-subtitle-2 font-weight-black text-primary tracking-tight" style="line-height: 1.2;">FLUENT</div>
              <div class="text-caption font-weight-bold text-grey-darken-1 text-truncate" style="font-size: 10px; line-height: 1;">Academic Studio</div>
            </div>
          </router-link>
        </div>

        <!-- Sidebar Navigation List -->
        <v-list density="comfortable" nav class="px-2 py-2">
          <!-- Section 1: Studio Modes -->
          <div v-if="!mdAndUp || !isRail" class="text-caption font-weight-black text-grey-darken-1 px-3 pt-2 pb-1 text-uppercase" style="font-size: 10px; letter-spacing: 0.5px;">
            Studio Modes
          </div>
          <v-divider v-else class="my-2" />

          <v-list-item
            to="/"
            rounded="lg"
            color="primary"
            active-class="sidebar-item-active"
            prepend-icon="mdi-microphone"
            class="mb-1"
          >
            <v-list-item-title class="font-weight-bold text-body-2">Speaking</v-list-item-title>
            <v-tooltip v-if="mdAndUp && isRail" activator="parent" location="right">Speaking Studio</v-tooltip>
          </v-list-item>

          <v-list-item
            to="/shadowing"
            rounded="lg"
            color="primary"
            active-class="sidebar-item-active"
            prepend-icon="mdi-waveform"
            class="mb-1"
          >
            <v-list-item-title class="font-weight-bold text-body-2">Shadowing</v-list-item-title>
            <v-tooltip v-if="mdAndUp && isRail" activator="parent" location="right">Shadowing Studio</v-tooltip>
          </v-list-item>

          <v-list-item
            v-if="!isMyHanhDomain"
            to="/flashcards"
            rounded="lg"
            color="primary"
            active-class="sidebar-item-active"
            prepend-icon="mdi-cards-variant"
            class="mb-1"
          >
            <v-list-item-title class="font-weight-bold text-body-2">Flashcards</v-list-item-title>
            <v-tooltip v-if="mdAndUp && isRail" activator="parent" location="right">Vocabulary Flashcards</v-tooltip>
          </v-list-item>

          <v-list-item
            v-if="!isMyHanhDomain"
            to="/picture-practice"
            rounded="lg"
            color="primary"
            active-class="sidebar-item-active"
            prepend-icon="mdi-image-filter-frames"
            class="mb-1"
          >
            <v-list-item-title class="font-weight-bold text-body-2">Describe Picture</v-list-item-title>
            <v-tooltip v-if="mdAndUp && isRail" activator="parent" location="right">Describe Picture</v-tooltip>
          </v-list-item>

          <!-- Section 2: Activities & Progress -->
          <div v-if="!mdAndUp || !isRail" class="text-caption font-weight-black text-grey-darken-1 px-3 pt-3 pb-1 text-uppercase" style="font-size: 10px; letter-spacing: 0.5px;">
            Activities & Progress
          </div>
          <v-divider v-else class="my-2" />

          <v-list-item
            to="/homework"
            rounded="lg"
            color="primary"
            active-class="sidebar-item-active"
            prepend-icon="mdi-clipboard-text-outline"
            class="mb-1"
          >
            <v-list-item-title class="font-weight-bold text-body-2">Homework</v-list-item-title>
            <v-tooltip v-if="mdAndUp && isRail" activator="parent" location="right">Homework</v-tooltip>
          </v-list-item>

          <v-list-item
            to="/leaderboard"
            rounded="lg"
            color="primary"
            active-class="sidebar-item-active"
            prepend-icon="mdi-trophy-outline"
            class="mb-1"
          >
            <v-list-item-title class="font-weight-bold text-body-2">Leaderboard</v-list-item-title>
            <v-tooltip v-if="mdAndUp && isRail" activator="parent" location="right">Leaderboard</v-tooltip>
          </v-list-item>

          <v-list-item
            to="/history"
            rounded="lg"
            color="primary"
            active-class="sidebar-item-active"
            prepend-icon="mdi-history"
            class="mb-1"
          >
            <v-list-item-title class="font-weight-bold text-body-2">History Log</v-list-item-title>
            <v-tooltip v-if="mdAndUp && isRail" activator="parent" location="right">History Log</v-tooltip>
          </v-list-item>

          <v-list-item
            v-if="!isMyHanhDomain"
            to="/stats"
            rounded="lg"
            color="primary"
            active-class="sidebar-item-active"
            prepend-icon="mdi-chart-bar"
            class="mb-1"
          >
            <v-list-item-title class="font-weight-bold text-body-2">Analytics</v-list-item-title>
            <v-tooltip v-if="mdAndUp && isRail" activator="parent" location="right">Analytics</v-tooltip>
          </v-list-item>

          <!-- Section 3: Portals (Teacher / Admin) -->
          <template v-if="['teacher', 'admin', 'super_admin'].includes(userRole)">
            <div v-if="!mdAndUp || !isRail" class="text-caption font-weight-black text-indigo px-3 pt-3 pb-1 text-uppercase" style="font-size: 10px; letter-spacing: 0.5px;">
              Portals
            </div>
            <v-divider v-else class="my-2" />

            <v-list-item
              to="/teacher"
              rounded="lg"
              color="indigo-darken-2"
              active-class="sidebar-item-active"
              prepend-icon="mdi-school"
              class="mb-1"
            >
              <v-list-item-title class="font-weight-bold text-body-2 text-indigo-darken-2">Teacher Hub</v-list-item-title>
              <v-tooltip v-if="mdAndUp && isRail" activator="parent" location="right">Teacher Hub</v-tooltip>
            </v-list-item>

            <v-list-item
              v-if="!isMyHanhDomain && ['admin', 'super_admin'].includes(userRole)"
              to="/admin"
              rounded="lg"
              color="purple-darken-3"
              active-class="sidebar-item-active"
              prepend-icon="mdi-shield-crown"
              class="mb-1"
            >
              <v-list-item-title class="font-weight-bold text-body-2 text-purple-darken-3">Admin Console</v-list-item-title>
              <v-tooltip v-if="mdAndUp && isRail" activator="parent" location="right">Admin Console</v-tooltip>
            </v-list-item>
          </template>
        </v-list>

        <!-- Append slot: Sidebar Rail Toggle Button on Desktop -->
        <template #append>
          <div class="pa-2 border-t">
            <v-btn
              v-if="mdAndUp"
              variant="text"
              block
              density="comfortable"
              class="text-caption font-weight-bold text-grey-darken-2 px-2"
              :class="isRail ? 'justify-center' : 'justify-start'"
              @click="toggleSidebar"
            >
              <v-icon :icon="isRail ? 'mdi-chevron-double-right' : 'mdi-chevron-double-left'" size="small" />
              <span v-if="!isRail" class="ml-2 text-none">Collapse Sidebar</span>
              <v-tooltip v-if="isRail" activator="parent" location="right">Expand Sidebar</v-tooltip>
            </v-btn>
          </div>
        </template>
      </v-navigation-drawer>

      <!-- Streamlined Modern App Bar -->
      <v-app-bar color="white" flat border class="px-2 px-md-4">
        <div class="d-flex align-center w-100">
          <!-- Mobile Drawer Toggle -->
          <v-btn
            icon
            variant="text"
            density="comfortable"
            class="d-md-none mr-2"
            @click="drawer = !drawer"
          >
            <v-icon>mdi-menu</v-icon>
          </v-btn>

          <!-- Desktop Quick Rail Toggle Button -->
          <v-btn
            v-if="mdAndUp"
            icon
            variant="text"
            density="comfortable"
            size="small"
            class="mr-2 text-grey-darken-1"
            @click="toggleSidebar"
          >
            <v-icon size="small">{{ isRail ? 'mdi-menu-open' : 'mdi-menu' }}</v-icon>
            <v-tooltip activator="parent" location="bottom">{{ isRail ? 'Expand Sidebar' : 'Collapse Sidebar' }}</v-tooltip>
          </v-btn>

          <!-- Current Page Title / Breadcrumb -->
          <div class="d-flex align-center ga-2">
            <v-icon :color="activePageInfo.color" size="small">{{ activePageInfo.icon }}</v-icon>
            <span class="text-subtitle-2 font-weight-black text-grey-darken-3">{{ activePageInfo.title }}</span>
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
              <span class="d-none d-sm-inline">{{ streak }}-Day Streak</span>
              <span class="d-inline d-sm-none">{{ streak }}d</span>
            </v-chip>
            <v-chip
              v-else
              color="grey-darken-1"
              variant="tonal"
              density="comfortable"
              class="font-weight-bold text-caption text-sm-body-2 px-2 px-sm-3"
              prepend-icon="mdi-fire"
            >
              <span class="d-none d-sm-inline">0-Day Streak</span>
              <span class="d-inline d-sm-none">0d</span>
              <v-tooltip activator="parent" location="bottom">Practice today to ignite your streak!</v-tooltip>
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
                    Role: {{ userRole.toUpperCase() }}
                  </v-list-item-subtitle>
                </v-list-item>

                <!-- Menu Actions -->
                <template v-if="!isMyHanhDomain && ['admin', 'super_admin'].includes(userRole)">
                  <v-list-item class="rounded mb-1 bg-purple-lighten-5" prepend-icon="mdi-shield-crown" color="purple-darken-3" to="/admin">
                    <v-list-item-title class="text-caption font-weight-black text-purple-darken-3">Admin Console</v-list-item-title>
                  </v-list-item>
                </template>
                <template v-if="['teacher', 'admin', 'super_admin'].includes(userRole)">
                  <v-list-item class="rounded mb-1 bg-indigo-lighten-5" prepend-icon="mdi-school" color="indigo-darken-3" to="/teacher">
                    <v-list-item-title class="text-caption font-weight-black text-indigo-darken-3">Teacher Hub</v-list-item-title>
                  </v-list-item>
                </template>

                <v-list-item class="rounded mb-1" prepend-icon="mdi-account-circle-outline" to="/profile">
                  <v-list-item-title class="text-caption font-weight-bold">User Profile</v-list-item-title>
                </v-list-item>

                <v-list-item v-if="!isMyHanhDomain" class="rounded mb-1" prepend-icon="mdi-cards-variant" color="primary" to="/flashcards">
                  <v-list-item-title class="text-caption font-weight-bold">Vocabulary Flashcards</v-list-item-title>
                </v-list-item>

                <v-list-item v-if="!isMyHanhDomain" class="rounded mb-1" prepend-icon="mdi-image-filter-frames" color="primary" to="/picture-practice">
                  <v-list-item-title class="text-caption font-weight-bold">Describe the Picture</v-list-item-title>
                </v-list-item>

                <v-list-item class="rounded mb-1" prepend-icon="mdi-trophy-award" color="amber-darken-3" @click="showAchievements = true">
                  <v-list-item-title class="text-caption font-weight-bold text-amber-darken-4">Achievements & Badges</v-list-item-title>
                </v-list-item>

                <v-list-item class="rounded mb-1" prepend-icon="mdi-theme-light-dark" @click="cycleTheme">
                  <v-list-item-title class="text-caption font-weight-bold">Toggle Theme Mode</v-list-item-title>
                </v-list-item>

                <v-divider class="my-1" />

                <v-list-item class="rounded" prepend-icon="mdi-logout" color="error" @click="confirmLogout">
                  <v-list-item-title class="text-caption font-weight-bold text-error">Sign Out</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </div>
      </v-app-bar>

      <v-main class="pb-16 pb-sm-4">
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
                :user-role="userRole"
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
            <span class="nav-label">Speaking</span>
          </router-link>

          <router-link to="/shadowing" class="nav-item" active-class="nav-item-active">
            <v-icon size="18">mdi-waveform</v-icon>
            <span class="nav-label">Shadowing</span>
          </router-link>

          <router-link to="/homework" class="nav-item" active-class="nav-item-active">
            <v-icon size="18">mdi-clipboard-text-outline</v-icon>
            <span class="nav-label">Homework</span>
          </router-link>

          <router-link to="/leaderboard" class="nav-item" active-class="nav-item-active">
            <v-icon size="18">mdi-trophy-outline</v-icon>
            <span class="nav-label">Leaderboard</span>
          </router-link>

          <router-link to="/history" class="nav-item" active-class="nav-item-active">
            <v-icon size="18">mdi-history</v-icon>
            <span class="nav-label">History</span>
          </router-link>

          <template v-if="!isMyHanhDomain">
            <router-link to="/stats" class="nav-item" active-class="nav-item-active">
              <v-icon size="18">mdi-chart-bar</v-icon>
              <span class="nav-label">Analytics</span>
            </router-link>

            <router-link to="/profile" class="nav-item" active-class="nav-item-active">
              <v-icon size="18">mdi-account-circle-outline</v-icon>
              <span class="nav-label">Profile</span>
            </router-link>
          </template>
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
                <div class="text-subtitle-1 font-weight-black text-secondary">Confirm Sign Out</div>
                <div class="text-caption text-grey-darken-1">Are you sure you want to sign out?</div>
              </div>
            </div>

            <div class="text-caption text-grey-darken-2 mb-4 bg-grey-lighten-4 pa-3 rounded border d-flex align-center ga-1.5" style="line-height: 1.5;">
              <v-icon color="amber-darken-3" size="small" class="flex-shrink-0">mdi-lightbulb-on-outline</v-icon>
              <span>Signing out will pause your current session on this device. You can sign back in anytime!</span>
            </div>

            <div class="d-flex align-center justify-end ga-2">
              <v-btn
                variant="outlined"
                color="grey-darken-1"
                class="font-weight-bold text-none"
                @click="showLogoutDialog = false"
              >
                Cancel
              </v-btn>
              <v-btn
                color="error"
                variant="flat"
                class="font-weight-bold text-none"
                prepend-icon="mdi-logout"
                @click="handleLogout"
              >
                Sign Out
              </v-btn>
            </div>
          </v-card>
        </v-dialog>

        <!-- Admin Secure Login Modal -->
        <v-dialog v-model="showAdminLoginModal" max-width="420">
          <v-card border flat class="pa-4 bg-white" rounded="lg">
            <div class="d-flex align-center ga-3 mb-3">
              <v-avatar color="grey-darken-4" size="40" class="text-white">
                <v-icon size="default">mdi-shield-lock-outline</v-icon>
              </v-avatar>
              <div>
                <div class="text-subtitle-1 font-weight-black text-secondary">System Admin Portal Sign In (/admin)</div>
                <div class="text-caption text-grey-darken-1">Authorized provisioned accounts only</div>
              </div>
            </div>

            <v-text-field
              v-model="adminEmailInput"
              label="Admin Email:"
              placeholder="superadmin@fluent.edu.vn"
              variant="outlined"
              density="comfortable"
              class="mb-2"
              prepend-inner-icon="mdi-email-outline"
            />

            <v-text-field
              v-model="adminPassInput"
              label="Admin Password:"
              type="password"
              placeholder="••••••••"
              variant="outlined"
              density="comfortable"
              class="mb-3"
              prepend-inner-icon="mdi-lock-outline"
              @keyup.enter="handleAdminLogin"
            />

            <div class="d-flex align-center justify-end ga-2">
              <v-btn variant="outlined" color="grey" class="font-weight-bold text-none" @click="showAdminLoginModal = false">
                Cancel
              </v-btn>
              <v-btn color="grey-darken-4" variant="flat" class="font-weight-bold text-none" :loading="isAdminLoggingIn" @click="handleAdminLogin">
                Sign In
              </v-btn>
            </div>
          </v-card>
        </v-dialog>
        <!-- Floating Groq-Powered AI Agent Copilot -->
        <AIAgentWidget
          :backend-url="backendUrl"
          :user-role="userRole"
          :user-id="userId || 1"
        />
      </template>
  </v-app>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useTheme, useDisplay } from 'vuetify'
import LoginPage from '@/components/LoginPage.vue'
import PracticeTab from '@/components/PracticeTab.vue'
import LeaderboardTab from '@/components/LeaderboardTab.vue'
import StatsTab from '@/components/StatsTab.vue'
import SettingsTab from '@/components/SettingsTab.vue'
import ProfileDialog from '@/components/ProfileDialog.vue'
import AchievementsDialog from '@/components/AchievementsDialog.vue'
import WeakWordsDialog from '@/components/WeakWordsDialog.vue'
import AIAgentWidget from '@/components/AIAgentWidget.vue'

const theme = useTheme()
const { mdAndUp } = useDisplay()
const router = useRouter()
const route = useRoute()

// Sidebar State & Rail Mode Toggle
const drawer = ref(true)
const isRail = ref(localStorage.getItem('fluent_sidebar_rail') === 'true')

const toggleSidebar = () => {
  if (mdAndUp.value) {
    isRail.value = !isRail.value
    localStorage.setItem('fluent_sidebar_rail', String(isRail.value))
  } else {
    drawer.value = !drawer.value
  }
}

// Dynamic Active Page Info (Title & Icon Breadcrumb)
const activePageInfo = computed(() => {
  const p = route.path
  if (p === '/' || p === '/practice') return { title: 'Speaking Studio', icon: 'mdi-microphone', color: 'primary' }
  if (p.startsWith('/shadowing')) return { title: 'Shadowing Studio', icon: 'mdi-waveform', color: 'secondary' }
  if (p.startsWith('/flashcards')) return { title: 'Vocabulary Flashcards', icon: 'mdi-cards-variant', color: 'primary' }
  if (p.startsWith('/picture-practice')) return { title: 'Describe Picture', icon: 'mdi-image-filter-frames', color: 'primary' }
  if (p.startsWith('/homework')) return { title: 'Homework Studio', icon: 'mdi-clipboard-text-outline', color: 'info' }
  if (p.startsWith('/leaderboard')) return { title: 'Leaderboard Ranking', icon: 'mdi-trophy-outline', color: 'warning' }
  if (p.startsWith('/history')) return { title: 'History Log', icon: 'mdi-history', color: 'grey-darken-2' }
  if (p.startsWith('/stats')) return { title: 'Learning Analytics', icon: 'mdi-chart-bar', color: 'primary' }
  if (p.startsWith('/profile')) return { title: 'User Profile', icon: 'mdi-account-circle-outline', color: 'primary' }
  if (p.startsWith('/teacher')) return { title: 'Educator Classroom Hub', icon: 'mdi-school', color: 'indigo' }
  if (p.startsWith('/admin')) return { title: 'System Administration', icon: 'mdi-shield-crown', color: 'purple-darken-3' }
  return { title: 'Learning Studio', icon: 'mdi-school', color: 'primary' }
})

// Routing
const isAdminRoute = computed(() => route.path === '/admin')

// Domain identification: check hostname for myhanh or test query param
const isMyHanhDomain = computed(() => {
  return window.location.hostname.includes('myhanh') || window.location.search.includes('mode=myhanh')
})

const isStandalonePortalRoute = computed(() => {
  if (isMyHanhDomain.value) return false
  return ['/teacher', '/admin', '/parent'].includes(route.path)
})

const portalHomeRoute = computed(() => {
  if (route.path.startsWith('/teacher')) return '/teacher'
  if (route.path.startsWith('/admin')) return '/admin'
  if (route.path.startsWith('/parent')) return '/parent'
  return '/'
})

const portalSubtitle = computed(() => {
  if (route.path.startsWith('/teacher')) return 'Educator Classroom Hub'
  if (route.path.startsWith('/admin')) return 'System Administration Portal'
  if (route.path.startsWith('/parent')) return 'Parent Progress Portal'
  return 'Academic English Pronunciation Studio'
})

const handleReturnToStudio = async () => {
  if (isLoggedIn.value) {
    router.push('/')
    return
  }
  const storedRole = localStorage.getItem('user_role')
  const storedEmail = localStorage.getItem('speak_user_email') || (storedRole === 'teacher' ? 'teacher@fluent.edu.vn' : (['admin', 'super_admin'].includes(storedRole) ? 'superadmin@fluent.edu.vn' : ''))
  if (storedEmail) {
    await autoLoginByEmail(storedEmail)
  }
  router.push('/')
}

const goToHome = () => {
  router.push('/')
}

// State
const isLoggedIn = ref(false)
const isCheckingAuth = ref(true)
const authLoadingMessage = ref('Loading Fluent Studio...')
const currentUserId = ref(null)
const userEmail = ref('')
const userName = ref('')
const userAvatar = ref('')
const userRole = ref(localStorage.getItem('user_role') || 'student')
const equippedBadgeTitle = ref('')
const dailyGoal = ref(5)
const streak = ref(0)
const history = ref([])

// Dialog states
const showProfile = ref(false)
const showAchievements = ref(false)
const showWeakWords = ref(false)
const showLogoutDialog = ref(false)
const showAdminLoginModal = ref(false)

const adminEmailInput = ref('')
const adminPassInput = ref('')
const isAdminLoggingIn = ref(false)

const switchToTeacherRole = () => {
  userRole.value = 'teacher'
  localStorage.setItem('user_role', 'teacher')
  alert('Switched to Educator Mode! Teacher Hub is now unlocked in navigation menu.')
}

const handleAdminLogin = async () => {
  if (!adminEmailInput.value.trim() || !adminPassInput.value.trim()) return
  isAdminLoggingIn.value = true
  try {
    const res = await fetch(`${backendUrl.value}/api/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: adminEmailInput.value.trim(),
        password: adminPassInput.value.trim()
      })
    })
    if (res.ok) {
      const data = await res.json()
      userRole.value = data.user.role
      localStorage.setItem('user_role', data.user.role)
      showAdminLoginModal.value = false
      alert(`Sign in successful! Access granted as ${data.user.role.toUpperCase()}`)
      window.location.href = '/admin'
    } else {
      const err = await res.json()
      alert(err.detail || 'Invalid Admin Email or Password.')
    }
  } catch (e) {
    alert('Admin Login Error: ' + e.message)
  } finally {
    isAdminLoggingIn.value = false
  }
}

// Dev configurations
const backendUrl = ref(import.meta.env.VITE_BACKEND_URL || 'https://agrse-fluent-english-backend.hf.space')
const isTestingConnection = ref(false)
const connectionStatus = ref(null)

// Lifecycle - Load persistent device session & handle OAuth redirects
onMounted(async () => {
  const storedUrl = localStorage.getItem('speak_backend_url')
  if (storedUrl && storedUrl.startsWith('http') && !storedUrl.includes('august-trung-english-pronunciation-assistant')) {
    backendUrl.value = storedUrl
  } else {
    backendUrl.value = import.meta.env.VITE_BACKEND_URL || 'https://agrse-fluent-english-backend.hf.space'
  }

  const hash = window.location.hash
  if (hash && hash.includes('access_token=')) {
    // Seamless Google OAuth callback at top-level
    authLoadingMessage.value = 'Signing in with Google... Preparing your learning studio...'
    try {
      const params = new URLSearchParams(hash.substring(1))
      const accessToken = params.get('access_token')
      if (accessToken) {
        const gRes = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
          headers: { Authorization: `Bearer ${accessToken}` }
        })
        if (gRes.ok) {
          const googleUser = await gRes.json()
          await handleLogin({
            email: googleUser.email,
            name: googleUser.name || googleUser.email.split('@')[0],
            avatar: googleUser.picture || ''
          })
        }
      }
    } catch (authErr) {
      console.error('Google Auth Hash Parsing Error in App.vue:', authErr)
    } finally {
      window.history.replaceState({}, document.title, window.location.pathname)
      isCheckingAuth.value = false
      if (!isLoggedIn.value && !isStandalonePortalRoute.value && route.path !== '/') {
        router.replace('/')
      }
    }
  } else {
    // Normal auto login check by stored email or educator role
    try {
      const storedEmail = localStorage.getItem('speak_user_email')
      if (storedEmail) {
        userEmail.value = storedEmail
        await autoLoginByEmail(storedEmail)
      } else {
        const storedRole = localStorage.getItem('user_role')
        if (storedRole === 'teacher') {
          await autoLoginByEmail('teacher@fluent.edu.vn')
        } else if (storedRole === 'admin' || storedRole === 'super_admin') {
          await autoLoginByEmail('superadmin@fluent.edu.vn')
        }
      }
    } finally {
      isCheckingAuth.value = false
      if (!isLoggedIn.value && !isStandalonePortalRoute.value && route.path !== '/') {
        router.replace('/')
      }
    }
  }

  const storedTheme = localStorage.getItem('speak_theme')
  if (storedTheme) {
    theme.global.name.value = storedTheme
  }
})

watch(
  () => route.path,
  (newPath) => {
    if (!isCheckingAuth.value && !isLoggedIn.value && !isStandalonePortalRoute.value && newPath !== '/') {
      router.replace('/')
    }
  }
)

// Calculate user learning streak accurately from practice history dates
const calculateStreakFromHistory = (histList) => {
  if (!histList || histList.length === 0) return 0
  const uniqueDates = [...new Set(histList.map(item => item.date || item.timestamp?.split(' ')[0]))]
    .filter(Boolean)
    .sort((a, b) => new Date(b) - new Date(a))
  
  if (uniqueDates.length === 0) return 0
  
  const todayStr = new Date().toISOString().split('T')[0]
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  const yesterdayStr = yesterday.toISOString().split('T')[0]
  
  // If user didn't practice today or yesterday, streak is broken
  if (uniqueDates[0] !== todayStr && uniqueDates[0] !== yesterdayStr) {
    return 0
  }
  
  let count = 1
  for (let i = 0; i < uniqueDates.length - 1; i++) {
    const cur = new Date(uniqueDates[i])
    const prev = new Date(uniqueDates[i + 1])
    const diffDays = Math.round((cur - prev) / (1000 * 60 * 60 * 24))
    if (diffDays === 1) {
      count++
    } else if (diffDays > 1) {
      break
    }
  }
  return count
}

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
        streak.value = data.user.streak_count ?? 0

        const effectiveRole = data.user.role || localStorage.getItem('user_role') || 'student'
        userRole.value = effectiveRole
        localStorage.setItem('user_role', effectiveRole)

        const userToken = data.user.token || data.token
        if (userToken) {
          localStorage.setItem('token', userToken)
          if (['admin', 'super_admin'].includes(effectiveRole)) {
            localStorage.setItem('admin_token', userToken)
            localStorage.setItem('admin_auth_token', userToken)
          }
          if (['teacher', 'admin', 'super_admin'].includes(effectiveRole)) {
            localStorage.setItem('teacher_token', userToken)
            localStorage.setItem('teacher_auth_token', userToken)
          }
        }

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
    // If incoming userData already authenticated from Universal Login on LoginPage
    if (userData.token && userData.role) {
      currentUserId.value = userData.id || userData.user_id
      userName.value = userData.name || userData.email.split('@')[0]
      userEmail.value = userData.email
      userAvatar.value = userData.avatar || ''
      userRole.value = userData.role
      dailyGoal.value = userData.daily_goal || 5
      streak.value = userData.streak ?? 0

      localStorage.setItem('user_role', userData.role)
      localStorage.setItem('speak_user_email', userData.email)
      if (userData.name) localStorage.setItem('speak_user_name', userData.name)
      if (userData.avatar) localStorage.setItem('speak_user_avatar', userData.avatar)

      localStorage.setItem('token', userData.token)
      if (['admin', 'super_admin'].includes(userData.role)) {
        localStorage.setItem('admin_token', userData.token)
        localStorage.setItem('admin_auth_token', userData.token)
      }
      if (['teacher', 'admin', 'super_admin'].includes(userData.role)) {
        localStorage.setItem('teacher_token', userData.token)
        localStorage.setItem('teacher_auth_token', userData.token)
      }

      isLoggedIn.value = true
      await fetchUserAllData()
      if (route.path === '/') {
        if (['admin', 'super_admin'].includes(userData.role)) {
          router.push('/admin')
        } else if (userData.role === 'teacher') {
          router.push('/teacher')
        }
      }
      return
    }

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
        streak.value = data.user.streak_count ?? 0

        const effectiveRole = data.user.role || userData.role || 'student'
        userRole.value = effectiveRole
        localStorage.setItem('user_role', effectiveRole)

        const userToken = data.user.token || data.token
        if (userToken) {
          localStorage.setItem('token', userToken)
          if (['admin', 'super_admin'].includes(effectiveRole)) {
            localStorage.setItem('admin_token', userToken)
            localStorage.setItem('admin_auth_token', userToken)
          }
          if (['teacher', 'admin', 'super_admin'].includes(effectiveRole)) {
            localStorage.setItem('teacher_token', userToken)
            localStorage.setItem('teacher_auth_token', userToken)
          }
        }
        
        localStorage.setItem('speak_user_email', data.user.email)
        if (userAvatar.value) localStorage.setItem('speak_user_avatar', userAvatar.value)
        if (userName.value) localStorage.setItem('speak_user_name', userName.value)
        
        isLoggedIn.value = true
        
        await fetchUserAllData()
        if (route.path === '/') {
          if (['admin', 'super_admin'].includes(effectiveRole)) {
            router.push('/admin')
          } else if (effectiveRole === 'teacher') {
            router.push('/teacher')
          }
        }
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
      if (data.streak_count !== undefined && data.streak_count !== null) {
        streak.value = data.streak_count
      }
      
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
      // Dynamically calculate and update streak from actual history
      const calcStreak = calculateStreakFromHistory(history.value)
      if (calcStreak > 0 || streak.value === 0) {
        streak.value = calcStreak
      }
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
      streak.value = 0
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
  localStorage.removeItem('user_role')
  localStorage.removeItem('user_id')
  localStorage.removeItem('token')
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_auth_token')
  localStorage.removeItem('teacher_token')
  localStorage.removeItem('teacher_auth_token')
  try {
    sessionStorage.clear()
  } catch (e) {}
  isLoggedIn.value = false
  userRole.value = 'student'
  currentUserId.value = null
  userEmail.value = ''
  userName.value = ''
  userAvatar.value = ''
  history.value = []
  showLogoutDialog.value = false
  router.replace('/')
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
        message: `API Connection successful! Status: ${data.status}`
      }
    } else {
      connectionStatus.value = {
        success: false,
        message: `Server connection error! Response code: ${res.status}`
      }
    }
  } catch (e) {
    connectionStatus.value = {
      success: false,
      message: `Unable to access API URL! ${e.message}`
    }
  } finally {
    isTestingConnection.value = false
  }
}
</script>

<style scoped>
.fluent-sidebar :deep(.v-list-item) {
  min-height: 40px;
}

.fluent-sidebar :deep(.sidebar-item-active) {
  background-color: rgba(3, 169, 244, 0.12) !important;
  color: #0288D1 !important;
  font-weight: 700 !important;
}

.sidebar-brand-header {
  height: 60px;
}

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
