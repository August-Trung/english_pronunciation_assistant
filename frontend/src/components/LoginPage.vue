<template>
  <v-container fluid class="fill-height bg-white pa-4 d-flex align-center justify-center">
    <div class="w-100 pa-2 text-center" style="max-width: 440px;">
      <!-- Logo Header -->
      <div class="mb-4">
        <v-avatar color="indigo-lighten-5" size="64" class="mb-2 border">
          <img src="/logo-augusttrung.png" alt="August Trung Logo" height="42" class="d-inline-block" />
        </v-avatar>
        <h1 class="text-h5 font-weight-black text-indigo-darken-4 tracking-tight">FLUENT</h1>
        <p class="text-caption text-grey-darken-1 font-weight-bold">Academic English Pronunciation Studio</p>
      </div>

      <!-- Role Selector Sub-Tabs -->
      <v-card border flat class="pa-1 mb-4 bg-grey-lighten-5 rounded-lg">
        <v-tabs v-model="selectedRoleTab" color="primary" align-tabs="center" density="comfortable" grow>
          <v-tab value="student" class="font-weight-black text-none" prepend-icon="mdi-account">
            Student
          </v-tab>
          <v-tab value="teacher" class="font-weight-black text-none" prepend-icon="mdi-school">
            Educator
          </v-tab>
          <v-tab value="admin" class="font-weight-black text-none" prepend-icon="mdi-shield-crown">
            Admin
          </v-tab>
        </v-tabs>
      </v-card>

      <!-- TAB 1: Student Login (Google OAuth / Guest) -->
      <v-card v-if="selectedRoleTab === 'student'" border flat class="pa-4 bg-white rounded-lg elevation-1">
        <div class="text-subtitle-2 font-weight-black text-primary mb-3">STUDENT LEARNING STUDIO SIGN IN</div>
        
        <div class="mb-3">
          <v-btn
            color="primary"
            variant="outlined"
            block
            height="44"
            prepend-icon="mdi-google"
            class="font-weight-bold text-none text-grey-darken-3"
            :loading="isGoogleLoading"
            @click="handleGoogleSignIn"
          >
            Sign in with Google
          </v-btn>
        </div>

        <div class="d-flex align-center my-3 ga-2">
          <v-divider />
          <span class="text-caption text-grey font-weight-bold text-no-wrap" style="font-size: 11px;">OR TRY AS GUEST</span>
          <v-divider />
        </div>

        <v-form @submit.prevent="submitGuestLogin">
          <v-text-field
            v-model="studentName"
            label="Full Name:"
            placeholder="Enter your student name..."
            variant="outlined"
            color="primary"
            density="comfortable"
            prepend-inner-icon="mdi-account-outline"
            class="mb-3"
            hide-details
          />
          
          <v-btn
            type="submit"
            color="primary"
            variant="flat"
            block
            height="44"
            class="font-weight-black text-none"
            prepend-icon="mdi-rocket-launch-outline"
            :loading="isLoading"
          >
            Start Guest Session
          </v-btn>
        </v-form>
      </v-card>

      <!-- TAB 2: Educator Login (Teacher Credentials) -->
      <v-card v-else-if="selectedRoleTab === 'teacher'" border flat class="pa-4 bg-white rounded-lg elevation-1 text-left">
        <div class="text-subtitle-2 font-weight-black text-indigo-darken-3 text-center mb-3">EDUCATOR PORTAL SIGN IN</div>
        
        <v-alert v-if="teacherError" type="error" variant="tonal" density="compact" class="mb-3 text-caption font-weight-bold">
          {{ teacherError }}
        </v-alert>

        <v-text-field
          v-model="teacherEmail"
          label="Teacher Email:"
          placeholder="teacher@fluent.edu.vn"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          prepend-inner-icon="mdi-email-outline"
        />

        <v-text-field
          v-model="teacherPassword"
          label="Password:"
          type="password"
          placeholder="••••••••"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          prepend-inner-icon="mdi-lock-outline"
          @keyup.enter="submitTeacherLogin"
        />

        <v-btn
          color="indigo-darken-3"
          variant="flat"
          block
          height="44"
          class="font-weight-black text-none mb-2"
          :loading="isTeacherLoading"
          @click="submitTeacherLogin"
        >
          Sign In as Educator
        </v-btn>

        <v-btn
          color="indigo"
          variant="tonal"
          block
          size="small"
          class="font-weight-bold text-none"
          prepend-icon="mdi-account-key"
          @click="teacherEmail = 'teacher@fluent.edu.vn'; teacherPassword = 'teacher123'; submitTeacherLogin();"
        >
          Quick Demo Educator Login
        </v-btn>
      </v-card>

      <!-- TAB 3: Admin Login (Super Admin Portal) -->
      <v-card v-else-if="selectedRoleTab === 'admin'" border flat class="pa-4 bg-white rounded-lg elevation-1 text-left">
        <div class="text-subtitle-2 font-weight-black text-indigo-darken-4 text-center mb-3">ENTERPRISE ADMIN PORTAL</div>
        
        <v-alert v-if="adminError" type="error" variant="tonal" density="compact" class="mb-3 text-caption font-weight-bold">
          {{ adminError }}
        </v-alert>

        <v-text-field
          v-model="adminEmail"
          label="Admin Email:"
          placeholder="superadmin@fluent.edu.vn"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          prepend-inner-icon="mdi-email-outline"
        />

        <v-text-field
          v-model="adminPassword"
          label="Admin Password:"
          type="password"
          placeholder="••••••••"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          prepend-inner-icon="mdi-lock-outline"
          @keyup.enter="submitAdminLogin"
        />

        <v-btn
          color="indigo-darken-4"
          variant="flat"
          block
          height="44"
          class="font-weight-black text-none"
          :loading="isAdminLoading"
          @click="submitAdminLogin"
        >
          Sign In to Admin Console
        </v-btn>
      </v-card>

      <!-- Footer Attribution -->
      <div class="mt-6 border-t pt-3 text-caption text-grey">
        Developed by <strong>August Trung</strong>
      </div>
    </div>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  backendUrl: String
})

const emit = defineEmits(['login'])

const selectedRoleTab = ref('student')

const studentName = ref('')
const isLoading = ref(false)
const isGoogleLoading = ref(false)

const teacherEmail = ref('teacher@fluent.edu.vn')
const teacherPassword = ref('teacher123')
const isTeacherLoading = ref(false)
const teacherError = ref('')

const adminEmail = ref('superadmin@fluent.edu.vn')
const adminPassword = ref('superadmin123')
const isAdminLoading = ref(false)
const adminError = ref('')

const submitGuestLogin = () => {
  if (!studentName.value.trim()) {
    studentName.value = `Student ${Math.floor(100 + Math.random() * 900)}`
  }
  isLoading.value = true
  setTimeout(() => {
    localStorage.setItem('user_role', 'student')
    emit('login', {
      user_id: 1,
      name: studentName.value.trim(),
      role: 'student'
    })
    isLoading.value = false
  }, 400)
}

const submitTeacherLogin = async () => {
  if (!teacherEmail.value.trim() || !teacherPassword.value.trim()) return
  isTeacherLoading.value = true
  teacherError.value = ''
  try {
    const res = await fetch(`${props.backendUrl || ''}/api/teacher/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: teacherEmail.value.trim(),
        password: teacherPassword.value.trim()
      })
    })
    if (res.ok) {
      const data = await res.json()
      localStorage.setItem('user_role', data.user.role || 'teacher')
      localStorage.setItem('user_id', data.user.id || 1)
      emit('login', {
        user_id: data.user.id,
        email: data.user.email,
        name: data.user.name,
        role: data.user.role
      })
    } else {
      const err = await res.json()
      teacherError.value = err.detail || 'Invalid Educator Credentials.'
    }
  } catch (e) {
    teacherError.value = 'Sign in error: ' + e.message
  } finally {
    isTeacherLoading.value = false
  }
}

const submitAdminLogin = async () => {
  if (!adminEmail.value.trim() || !adminPassword.value.trim()) return
  isAdminLoading.value = true
  adminError.value = ''
  try {
    const res = await fetch(`${props.backendUrl || ''}/api/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: adminEmail.value.trim(),
        password: adminPassword.value.trim()
      })
    })
    if (res.ok) {
      const data = await res.json()
      localStorage.setItem('user_role', data.user.role || 'super_admin')
      localStorage.setItem('user_id', data.user.id || 1)
      emit('login', {
        user_id: data.user.id,
        email: data.user.email,
        name: data.user.name,
        role: data.user.role
      })
    } else {
      const err = await res.json()
      adminError.value = err.detail || 'Invalid Admin Credentials.'
    }
  } catch (e) {
    adminError.value = 'Sign in error: ' + e.message
  } finally {
    isAdminLoading.value = false
  }
}

const handleGoogleSignIn = () => {
  const CLIENT_ID = '937517173268-l34kbh3mknk02kkhh9r2i67h3s7g8j7j.apps.googleusercontent.com'
  const REDIRECT_URI = window.location.origin
  const SCOPE = 'openid email profile'
  const RESPONSE_TYPE = 'token'
  
  const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&response_type=${RESPONSE_TYPE}&scope=${encodeURIComponent(SCOPE)}&prompt=select_account`
  
  window.location.href = authUrl
}

onMounted(async () => {
  const hash = window.location.hash
  if (hash && hash.includes('access_token=')) {
    isGoogleLoading.value = true
    try {
      const params = new URLSearchParams(hash.substring(1))
      const accessToken = params.get('access_token')
      
      if (accessToken) {
        const res = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
          headers: { Authorization: `Bearer ${accessToken}` }
        })
        
        if (res.ok) {
          const googleUser = await res.json()
          localStorage.setItem('user_role', 'student')
          emit('login', {
            user_id: 1,
            email: googleUser.email,
            name: googleUser.name || googleUser.email.split('@')[0],
            avatar: googleUser.picture || '',
            role: 'student'
          })
        }
      }
    } catch (err) {
      console.error('Google Auth Hash Parsing Error:', err)
    } finally {
      isGoogleLoading.value = false
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }
})
</script>
