import { createRouter, createWebHistory } from 'vue-router'
import PracticeView from '@/views/PracticeView.vue'
import ShadowingView from '@/views/ShadowingView.vue'
import FlashcardsView from '@/views/FlashcardsView.vue'
import LeaderboardView from '@/views/LeaderboardView.vue'
import StatsView from '@/views/StatsView.vue'
import SettingsView from '@/views/SettingsView.vue'
import ProfileView from '@/views/ProfileView.vue'
import TeacherView from '@/views/TeacherView.vue'
import AdminView from '@/views/AdminView.vue'
import ParentView from '@/views/ParentView.vue'
import StudentHomeworkView from '@/views/StudentHomeworkView.vue'

const routes = [
  { path: '/', name: 'practice', component: PracticeView },
  { path: '/shadowing', name: 'shadowing', component: ShadowingView },
  { path: '/homework', name: 'homework', component: StudentHomeworkView },
  { path: '/history', name: 'history', component: () => import('@/views/HistoryView.vue') },
  { path: '/teacher', name: 'teacher', component: TeacherView },
  { path: '/admin', name: 'admin', component: AdminView },
  { path: '/parent', name: 'parent', component: ParentView },
  { path: '/flashcards', name: 'flashcards', component: FlashcardsView },
  { path: '/picture-practice', name: 'picture-practice', component: () => import('@/views/PicturePracticeView.vue') },
  { path: '/leaderboard', name: 'leaderboard', component: LeaderboardView },
  { path: '/stats', name: 'stats', component: StatsView },
  { path: '/settings', name: 'settings', component: SettingsView },
  { path: '/profile', name: 'profile', component: ProfileView },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard for myhanh domain: limit access to core routes
router.beforeEach((to, from, next) => {
  const isMyHanh = window.location.hostname.includes('myhanh') || window.location.search.includes('mode=myhanh')
  if (isMyHanh) {
    const allowed = ['/', '/shadowing', '/homework', '/leaderboard', '/history', '/profile', '/teacher']
    if (!allowed.includes(to.path)) {
      return next('/')
    }
  }
  next()
})

export default router
