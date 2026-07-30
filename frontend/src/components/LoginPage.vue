<template>
  <v-container fluid class="fill-height bg-white pa-4 d-flex align-center justify-center">
    <div class="w-100 pa-2 text-center" style="max-width: 380px;">
      <!-- Logo Header -->
      <div class="mb-6">
        <v-avatar color="purple-lighten-5" size="64" class="mb-3 border border-purple">
          <img src="/logo-augusttrung.png" alt="August Trung Logo" height="42" class="d-inline-block" />
        </v-avatar>
        <h1 class="text-h5 font-weight-black text-purple-darken-3 tracking-tight">FLUENT</h1>
        <p class="text-caption text-grey-darken-1 font-weight-bold">Academic English Pronunciation Studio</p>
      </div>

      <!-- Pure Student Sign-In Card (Zero Teacher/Admin Role Tabs) -->
      <v-card border flat class="pa-4 bg-white rounded-lg elevation-1">
        <div class="text-subtitle-2 font-weight-black text-purple-darken-3 mb-3">STUDENT LEARNING STUDIO SIGN IN</div>
        
        <div class="mb-3">
          <v-btn
            color="purple-darken-3"
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
            color="purple-darken-3"
            density="comfortable"
            prepend-inner-icon="mdi-account-outline"
            class="mb-3"
            hide-details
          />
          
          <v-btn
            type="submit"
            color="purple-darken-3"
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

      <!-- Footer Attribution -->
      <div class="mt-8 border-t pt-4 text-caption text-grey">
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

const studentName = ref('')
const isLoading = ref(false)
const isGoogleLoading = ref(false)

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

const handleGoogleSignIn = () => {
  const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID
  const REDIRECT_URI = window.location.origin
  const SCOPE = 'openid email profile'
  const RESPONSE_TYPE = 'token'
  
  if (!CLIENT_ID) {
    console.error('Missing VITE_GOOGLE_CLIENT_ID environment variable.')
    return
  }

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
