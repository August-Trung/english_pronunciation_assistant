import { createRouter, createWebHistory } from 'vue-router'
import PracticeView from '@/views/PracticeView.vue'
import ShadowingView from '@/views/ShadowingView.vue'
import FlashcardsView from '@/views/FlashcardsView.vue'
import LeaderboardView from '@/views/LeaderboardView.vue'
import StatsView from '@/views/StatsView.vue'
import SettingsView from '@/views/SettingsView.vue'
import ProfileView from '@/views/ProfileView.vue'
import TeacherView from '@/views/TeacherView.vue'

const routes = [
  { path: '/', name: 'practice', component: PracticeView },
  { path: '/shadowing', name: 'shadowing', component: ShadowingView },
  { path: '/teacher', name: 'teacher', component: TeacherView },
  { path: '/flashcards', name: 'flashcards', component: FlashcardsView },
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

export default router
