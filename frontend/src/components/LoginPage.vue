<template>
  <v-container fluid class="fill-height bg-white pa-4 d-flex align-center justify-center">
    <div class="w-100 pa-2 text-center" style="max-width: 380px;">
      <!-- Logo Header -->
      <div class="mb-8">
        <v-avatar color="teal-lighten-5" size="64" class="mb-3">
          <img src="/logo-augusttrung.png" alt="August Trung Logo" height="42" class="d-inline-block" />
        </v-avatar>
        <h1 class="text-h5 font-weight-black text-teal-darken-4 tracking-tight">FLUENT</h1>
        <p class="text-caption text-grey-darken-1 font-weight-bold">Trợ Lý Luyện Phát Âm Tiếng Anh Học Đường</p>
      </div>

      <!-- Google Sign-In Button -->
      <div class="mb-4">
        <v-btn
          color="teal"
          variant="outlined"
          block
          height="44"
          prepend-icon="mdi-google"
          class="font-weight-bold text-none text-grey-darken-3"
          :loading="isGoogleLoading"
          @click="handleGoogleSignIn"
        >
          Đăng nhập bằng Google
        </v-btn>
      </div>

      <div class="d-flex align-center my-4 ga-2">
        <v-divider />
        <span class="text-caption text-grey font-weight-bold text-no-wrap" style="font-size: 11px;">HOẶC HỌC THỬ</span>
        <v-divider />
      </div>

      <!-- Guest Form -->
      <v-form @submit.prevent="submitGuestLogin">
        <v-text-field
          v-model="studentName"
          label="Họ và tên của em:"
          placeholder="Nhập họ và tên..."
          variant="outlined"
          color="teal"
          density="comfortable"
          prepend-inner-icon="mdi-account-outline"
          class="mb-3"
          hide-details
        />
        
        <v-btn
          type="submit"
          color="teal"
          variant="flat"
          block
          height="44"
          class="font-weight-black text-none"
          prepend-icon="mdi-rocket-launch-outline"
          :loading="isLoading"
        >
          Vào Học Thử Ngay
        </v-btn>
      </v-form>

      <!-- Footer Attribution -->
      <div class="mt-8 border-t pt-4 text-caption text-grey">
        Được phát triển bởi <strong>August Trung</strong>
      </div>
    </div>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const emit = defineEmits(['login'])
const studentName = ref('')
const isLoading = ref(false)
const isGoogleLoading = ref(false)

// Config Google OAuth 2.0 Client ID chính chủ của ứng dụng Fluent English
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '917273250250-9tldfcfues1nhdphcobs4p56i0ge8tvt.apps.googleusercontent.com'

const handleGoogleSignIn = () => {
  isGoogleLoading.value = true
  const redirectUri = window.location.origin
  const scope = 'email profile'
  
  // Chuyển hướng chính xác sang trang "Chọn tài khoản Google" (accounts.google.com)
  const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${GOOGLE_CLIENT_ID}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=token&scope=${encodeURIComponent(scope)}&prompt=select_account`
  
  window.location.href = authUrl
}

const submitGuestLogin = () => {
  if (!studentName.value.trim()) return
  isLoading.value = true
  setTimeout(() => {
    emit('login', {
      user_id: Math.floor(Math.random() * 9000) + 1000,
      email: `guest_${Math.floor(Math.random() * 9000)}@fluent.edu.vn`,
      name: studentName.value.trim(),
      avatar: ''
    })
    isLoading.value = false
  }, 400)
}

// Xử lý dữ liệu trả về từ Google sau khi chọn tài khoản
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
          emit('login', {
            user_id: 1,
            email: googleUser.email,
            name: googleUser.name || googleUser.email.split('@')[0],
            avatar: googleUser.picture || ''
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
