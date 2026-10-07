<template>
  <v-container fluid class="fill-height bg-white pa-4 d-flex align-center justify-center">
    <div class="w-100 pa-2 text-center" style="max-width: 400px;">
      <!-- Logo Header -->
      <div class="mb-5">
        <v-avatar color="purple-lighten-5" size="64" class="mb-3 border border-purple">
          <img src="/logo-augusttrung.png" alt="August Trung Logo" height="42" class="d-inline-block" />
        </v-avatar>
        <h1 class="text-h5 font-weight-black text-purple-darken-3 tracking-tight">FLUENT</h1>
        <p class="text-caption text-grey-darken-1 font-weight-bold">Academic English Pronunciation Studio</p>
      </div>

      <!-- Universal Sign-In Card -->
      <v-card border flat class="pa-4 pa-sm-5 bg-white rounded-lg elevation-1 text-left">
        <div class="text-subtitle-2 font-weight-black text-purple-darken-3 mb-3 text-center">
          SIGN IN TO YOUR ACCOUNT
        </div>

        <v-alert
          v-if="loginError"
          type="error"
          variant="tonal"
          density="compact"
          class="mb-3 text-caption"
          closable
          @click:close="loginError = ''"
        >
          {{ loginError }}
        </v-alert>

        <!-- Google OAuth Button -->
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
          <span class="text-caption text-grey font-weight-bold text-no-wrap" style="font-size: 11px;">OR USE EMAIL & PASSWORD</span>
          <v-divider />
        </div>

        <!-- Universal Email & Password Form -->
        <v-form @submit.prevent="submitEmailPasswordLogin">
          <v-text-field
            v-model="emailInput"
            label="Email Address:"
            placeholder="e.g. name@fluent.edu.vn"
            type="email"
            variant="outlined"
            color="purple-darken-3"
            density="comfortable"
            prepend-inner-icon="mdi-email-outline"
            class="mb-2"
            hide-details="auto"
          />

          <v-text-field
            v-model="passwordInput"
            label="Password:"
            placeholder="Enter password..."
            type="password"
            variant="outlined"
            color="purple-darken-3"
            density="comfortable"
            prepend-inner-icon="mdi-lock-outline"
            class="mb-3"
            hide-details="auto"
          />

          <v-btn
            type="submit"
            color="purple-darken-3"
            variant="flat"
            block
            height="44"
            class="font-weight-black text-none mb-3"
            prepend-icon="mdi-login"
            :loading="isEmailLoading"
          >
            Sign In
          </v-btn>
        </v-form>

        <div class="d-flex align-center my-2 ga-2">
          <v-divider />
          <span class="text-caption text-grey font-weight-bold text-no-wrap" style="font-size: 11px;">OR TRY AS GUEST</span>
          <v-divider />
        </div>

        <!-- Guest Session Form -->
        <v-form @submit.prevent="submitGuestLogin">
          <v-text-field
            v-model="studentName"
            label="Guest Display Name:"
            placeholder="Enter temporary student name..."
            variant="outlined"
            color="purple-darken-3"
            density="comfortable"
            prepend-inner-icon="mdi-account-outline"
            class="mb-2"
            hide-details
          />

          <v-btn
            type="submit"
            color="grey-darken-3"
            variant="tonal"
            block
            height="38"
            class="font-weight-bold text-none text-caption"
            prepend-icon="mdi-rocket-launch-outline"
            :loading="isGuestLoading"
          >
            Start Guest Session
          </v-btn>
        </v-form>
      </v-card>

      <!-- Footer Attribution -->
      <div class="mt-6 border-t pt-4 text-caption text-grey">
        Developed by <strong>August Trung</strong>
      </div>
    </div>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  backendUrl: String
})

const emit = defineEmits(['login'])

const emailInput = ref('')
const passwordInput = ref('')
const loginError = ref('')
const isEmailLoading = ref(false)

const studentName = ref('')
const isGuestLoading = ref(false)
const isGoogleLoading = ref(false)

const submitEmailPasswordLogin = async () => {
  if (!emailInput.value.trim() || !passwordInput.value.trim()) {
    loginError.value = 'Please enter both email and password.'
    return
  }
  isEmailLoading.value = true
  loginError.value = ''
  try {
    const res = await fetch(`${props.backendUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: emailInput.value.trim(),
        password: passwordInput.value.trim()
      })
    })
    if (res.ok) {
      const data = await res.json()
      emit('login', {
        id: data.user.id,
        user_id: data.user.id,
        email: data.user.email,
        name: data.user.name,
        role: data.user.role,
        tenant_id: data.user.tenant_id,
        token: data.token
      })
    } else {
      const err = await res.json()
      loginError.value = err.detail || 'Invalid email or password.'
    }
  } catch (e) {
    loginError.value = 'Login error: ' + e.message
  } finally {
    isEmailLoading.value = false
  }
}

const submitGuestLogin = () => {
  if (!studentName.value.trim()) {
    studentName.value = `Student ${Math.floor(100 + Math.random() * 900)}`
  }
  isGuestLoading.value = true
  setTimeout(() => {
    emit('login', {
      user_id: 1,
      name: studentName.value.trim(),
      role: 'student'
    })
    isGuestLoading.value = false
  }, 300)
}

const handleGoogleSignIn = () => {
  const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID
  const REDIRECT_URI = window.location.origin
  const SCOPE = 'openid email profile'
  const RESPONSE_TYPE = 'token'

  if (!CLIENT_ID) {
    loginError.value = 'Google Client ID not configured.'
    return
  }

  isGoogleLoading.value = true
  const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&response_type=${RESPONSE_TYPE}&scope=${encodeURIComponent(SCOPE)}&prompt=select_account`
  window.location.href = authUrl
}
</script>
