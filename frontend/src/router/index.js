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
  { path: '/teacher', name: 'teacher', component: TeacherView, meta: { requiresAuth: true, roles: ['teacher', 'admin', 'super_admin'] } },
  { path: '/admin', name: 'admin', component: AdminView, meta: { requiresAuth: true, roles: ['admin', 'super_admin'] } },
  { path: '/parent', name: 'parent', component: ParentView },
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

router.beforeEach((to, from, next) => {
  const userRole = localStorage.getItem('user_role') || 'student'
  if (to.meta.requiresAuth) {
    if (!to.meta.roles.includes(userRole)) {
      alert(`Truy cập bị từ chối: Quyền ${userRole.toUpperCase()} không thể vào đường dẫn ${to.path}.`)
      return next('/')
    }
  }
  next()
})

export default router
