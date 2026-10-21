<template>
  <v-main class="d-flex align-center justify-center pa-4" style="min-height:100vh">
    <v-card max-width="520" width="100%" class="pa-5" rounded="xl">
      <v-card-title class="text-wrap">{{ classroom ? 'Join ' + classroom.class_name : 'Student Sign In' }}</v-card-title>
      <v-card-subtitle class="text-wrap mb-4">Use a username and password. No email or Google account required.</v-card-subtitle>
      <v-alert v-if="error" type="error" variant="tonal" class="mb-3">{{ error }}</v-alert>
      <v-progress-linear v-if="loading" indeterminate class="mb-3" />
      <template v-if="!$route.query.join_code">
        <v-text-field v-model="code" label="Class Code (for a new class)" @keyup.enter="loadClass" />
        <v-btn v-if="code && !classroom" variant="tonal" class="mb-3" :disabled="loading" @click="loadClass">Find Class</v-btn>
      </template>
      <template v-if="userId && userRole === 'student'">
        <p class="mb-4">Continue as <strong>{{ userName || 'your student account' }}</strong>.</p>
        <v-btn color="primary" block size="large" :loading="loading" @click="joinExisting">{{ classroom ? 'Enter Class' : 'Open My Classes' }}</v-btn>
      </template>
      <v-alert v-else-if="userId" type="info" variant="tonal">You are signed in as an educator. Open this link on the student's device.</v-alert>
      <template v-else-if="classroom || !$route.query.join_code">
        <v-btn-toggle v-model="mode" mandatory divided class="w-100 mb-4">
          <v-btn value="register" :disabled="!classroom" class="flex-grow-1">Create Account</v-btn>
          <v-btn value="login" class="flex-grow-1">Sign In</v-btn>
        </v-btn-toggle>
        <v-form @submit.prevent="authenticate">
          <v-text-field v-model="username" label="Username" autocomplete="username" autocapitalize="none" :spellcheck="false" maxlength="30" hint="3–30 letters, numbers, dots, underscores or hyphens." persistent-hint />
          <v-text-field v-model="password" label="Password" :type="showPassword ? 'text' : 'password'" :autocomplete="mode === 'register' ? 'new-password' : 'current-password'" :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'" @click:append-inner="showPassword = !showPassword" hint="At least 8 characters." persistent-hint />
          <v-text-field v-if="mode === 'register'" v-model="name" label="Full Name (Optional)" maxlength="80" hint="Your teacher will see this name. You can add it later." persistent-hint />
          <v-btn type="submit" color="primary" block size="large" class="mt-4" :loading="loading" :disabled="!canSubmit">{{ mode === 'register' ? 'Register and Join Class' : (classroom ? 'Sign In and Join Class' : 'Sign In') }}</v-btn>
        </v-form>
        <p class="text-caption mt-4">This browser remembers your sign-in. Use your username and password on another device. Sign out on shared devices.</p>
      </template>
      <v-btn variant="text" block class="mt-3" @click="router.push({path:'/',query:{signin:'1'}})">Use an Email or Google Account</v-btn>
    </v-card>
  </v-main>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
const props = defineProps({ backendUrl: String, userId: Number, userName: String, userRole: String })
const emit = defineEmits(['login'])
const route = useRoute()
const router = useRouter()
const code = ref(String(route.query.join_code || localStorage.getItem('pending_join_code') || ''))
const classroom = ref(null)
const loading = ref(false)
const error = ref('')
const mode = ref(route.query.join_code ? 'register' : 'login')
const username = ref('')
const password = ref('')
const name = ref('')
const showPassword = ref(false)
const canSubmit = computed(() => !loading.value && /^[a-z0-9][a-z0-9._-]{2,29}$/i.test(username.value.trim()) && password.value.length >= 8 && password.value.length <= 128 && (mode.value !== 'register' || Boolean(classroom.value)))
async function readResponse(response) {
  const data = await response.json()
  if (!response.ok) throw new Error(data.detail || 'Unable to continue. Please try again.')
  return data
}
async function loadClass() {
  error.value = ''; loading.value = true; classroom.value = null
  try {
    classroom.value = await readResponse(await fetch(`${props.backendUrl}/api/class-invites/${encodeURIComponent(code.value.trim())}`))
    localStorage.setItem('pending_join_code', code.value.trim())
  } catch(e) { error.value = e.message } finally { loading.value = false }
}
async function enroll(user, token) {
  if (classroom.value) {
    await readResponse(await fetch(`${props.backendUrl}/api/classes/join`, {method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${token}`},body:JSON.stringify({student_id:user.id,join_code:code.value.trim()})}))
    localStorage.removeItem('pending_join_code')
  }
  router.replace('/homework')
}
async function authenticate() {
  if (!canSubmit.value) return
  loading.value = true; error.value = ''
  let signedIn = false
  try {
    // Detect unavailable persistent storage before creating a new account.
    localStorage.setItem('student_storage_check','1'); localStorage.removeItem('student_storage_check')
    const data = await readResponse(await fetch(`${props.backendUrl}/api/learners/${mode.value}`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:username.value.trim(),password:password.value,name:name.value,join_code:code.value.trim()})}))
    localStorage.setItem('token', data.user.token)
    localStorage.setItem('speak_user_email', data.user.email)
    localStorage.setItem('speak_user_name', data.user.name)
    localStorage.setItem('user_role','student')
    password.value = ''; signedIn = true
    emit('login',data.user)
    await enroll(data.user,data.user.token)
  } catch(e) { error.value = signedIn ? 'You are signed in, but the class could not be joined. ' + e.message : e.message } finally { loading.value = false }
}
async function joinExisting() {
  if (loading.value) return
  loading.value = true; error.value = ''
  try { await enroll({id:props.userId},localStorage.getItem('token') || '') } catch(e) { error.value = e.message } finally { loading.value = false }
}
onMounted(() => { if (code.value.trim()) loadClass() })
</script>
