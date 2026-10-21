<template>
  <v-main class="d-flex align-center justify-center pa-4" style="min-height:100vh">
    <v-card max-width="540" width="100%" class="pa-5" rounded="xl">
      <v-card-title class="text-wrap">Welcome to Your Classroom</v-card-title>
      <v-card-subtitle class="text-wrap mb-4">No email or Google account is required.</v-card-subtitle>
      <v-alert v-if="error" type="error" variant="tonal" class="mb-3">{{ error }}</v-alert>
      <v-progress-linear v-if="loading" indeterminate class="mb-3" />
      <template v-if="joined">
        <h2 class="text-h6 mb-2">You are in {{ classroom?.class_name }}!</h2>
        <p class="mb-3">This browser will remember {{ joined.name }}. Use the same browser next time.</p>
        <v-expansion-panels class="mb-4">
          <v-expansion-panel title="Save Your Student Key">
            <v-expansion-panel-text>
              <p class="mb-2">Ask a parent to keep this key privately. It restores your profile on a new device or after browser data is cleared. Anyone with this key can access your profile.</p>
              <code style="overflow-wrap:anywhere">{{ savedKey }}</code>
              <v-btn class="mt-2" variant="tonal" @click="copyKey">Copy Student Key</v-btn>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
        <v-btn color="primary" block size="large" @click="$router.replace('/homework')">Enter Classroom</v-btn>
      </template>
      <template v-else>
        <v-text-field v-model="code" label="Class Code" :readonly="Boolean($route.query.join_code)" @keyup.enter="loadClass" />
        <v-btn v-if="!classroom" variant="tonal" :disabled="loading || !code.trim()" @click="loadClass">Find Class</v-btn>
        <template v-if="classroom">
          <h2 class="text-h6 mb-3">{{ classroom.class_name }}</h2>
          <template v-if="userId && userRole === 'student'">
            <p class="mb-3">Continue as <strong>{{ userName || 'your saved student profile' }}</strong>.</p>
            <v-btn color="primary" block size="large" :loading="loading" @click="joinExisting">Join Class</v-btn>
          </template>
          <v-alert v-else-if="userId" type="info" variant="tonal">You are signed in as an educator. Open this link in the student's browser to create a learner profile.</v-alert>
          <template v-else>
            <v-text-field v-if="!recovering" v-model="name" label="Your Full Name" maxlength="80" hint="Use the name your teacher knows." persistent-hint @keyup.enter="joinNew" />
            <v-textarea v-else v-model="recoveryKey" label="Your Saved Student Key" rows="3" autocomplete="off" />
            <v-btn color="primary" block size="large" class="mt-4" :loading="loading" :disabled="recovering ? !recoveryKey.trim() : name.trim().length < 2" @click="joinNew">{{ recovering ? 'Restore and Join Class' : 'Join Class' }}</v-btn>
            <v-btn variant="text" block class="mt-2" @click="recovering = !recovering">{{ recovering ? 'Create a New Student Profile' : 'I Have a Student Key' }}</v-btn>
          </template>
        </template>
        <v-btn variant="text" block class="mt-4" @click="router.push({path:'/',query:{signin:'1'}})">I Already Have an Email Account</v-btn>
        <p class="text-caption mt-4">Private browsing or clearing browser data removes this device's saved sign-in. Keep your Student Key to recover your profile.</p>
      </template>
    </v-card>
  </v-main>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
const props = defineProps({ backendUrl: String, userId: Number, userName: String, userRole: String })
const emit = defineEmits(['login'])
const route = useRoute()
const router = useRouter()
const code = ref(String(route.query.join_code || localStorage.getItem('pending_join_code') || ''))
const name = ref('')
const classroom = ref(null)
const loading = ref(false)
const error = ref('')
const joined = ref(null)
const recovering = ref(false)
const recoveryKey = ref('')
const savedKey = ref('')
async function readResponse(response) {
  const data = await response.json()
  if (!response.ok) throw new Error(data.detail || 'Unable to join. Please try again.')
  return data
}
async function loadClass() {
  error.value = ''; loading.value = true; classroom.value = null
  try {
    const data = await readResponse(await fetch(`${props.backendUrl}/api/class-invites/${encodeURIComponent(code.value.trim())}`))
    classroom.value = data
    localStorage.setItem('pending_join_code', code.value.trim())
  } catch (e) { error.value = e.message } finally { loading.value = false }
}
async function joinNew() {
  if (loading.value || !classroom.value) return
  error.value = ''; loading.value = true
  try {
    const oldKey = localStorage.getItem('myhanh_student_key')
    // Persist the idempotency/recovery credential BEFORE the network request.
    const key = recovering.value ? recoveryKey.value.trim().toLowerCase() : (oldKey || Array.from(crypto.getRandomValues(new Uint8Array(32)), x => x.toString(16).padStart(2, '0')).join(''))
    if (!/^[0-9a-f]{64}$/.test(key)) throw new Error('Please enter the complete 64-character Student Key.')
    if (recovering.value) await readResponse(await fetch(`${props.backendUrl}/api/learners/resume`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({student_key:key}) }))
    localStorage.setItem('myhanh_student_key', key)
    const data = await readResponse(await fetch(`${props.backendUrl}/api/learners/join`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({join_code:code.value.trim(),name:name.value,student_key:key})}))
    savedKey.value = key; joined.value = data.user
    localStorage.removeItem('pending_join_code')
    emit('login', data.user)
  } catch(e) { error.value = e.message } finally { loading.value = false }
}
async function joinExisting() {
  if (loading.value) return
  loading.value = true; error.value = ''
  try {
    await readResponse(await fetch(`${props.backendUrl}/api/classes/join`, {method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${localStorage.getItem('token') || ''}`},body:JSON.stringify({student_id:props.userId,join_code:code.value.trim()})}))
    localStorage.removeItem('pending_join_code')
    router.replace('/homework')
  } catch(e) { error.value = e.message } finally { loading.value = false }
}
async function copyKey() {
  try { await navigator.clipboard.writeText(savedKey.value) } catch { error.value = 'Unable to copy. Please save the key shown above privately.' }
}
onMounted(() => { if (code.value.trim()) loadClass() })
</script>
