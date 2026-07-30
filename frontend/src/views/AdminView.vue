<template>
  <v-container fluid class="pa-4 pa-md-6" style="max-width: 1100px;">
    <!-- Modern Vuetify Notification Toast -->
    <v-snackbar
      v-model="toast.show"
      :color="toast.color"
      location="top"
      timeout="3500"
      rounded="lg"
      elevation="4"
    >
      <div class="d-flex align-center ga-2 text-subtitle-2 font-weight-bold text-white">
        <v-icon>{{ toast.icon }}</v-icon>
        <span>{{ toast.text }}</span>
      </div>
    </v-snackbar>

    <!-- Embedded Admin Login View if Not Authenticated as Admin -->
    <div v-if="!['admin', 'super_admin'].includes(activeUserRole)" class="d-flex justify-center py-12">
      <v-card border flat class="pa-6 bg-white rounded-lg elevation-3" style="max-width: 440px; width: 100%;">
        <div class="text-center mb-4">
          <v-avatar color="indigo-darken-4" size="56" class="text-white mb-2 elevation-2">
            <v-icon size="large">mdi-shield-lock-outline</v-icon>
          </v-avatar>
          <div class="text-h6 font-weight-black text-indigo-darken-4">SYSTEM ADMIN PORTAL</div>
          <div class="text-caption text-grey-darken-1 font-weight-medium">Authorized provisioned admin accounts only</div>
        </div>

        <v-alert v-if="loginError" type="error" variant="tonal" density="compact" class="mb-3 text-caption font-weight-bold">
          {{ loginError }}
        </v-alert>

        <v-text-field
          v-model="loginEmail"
          label="Admin Email:"
          placeholder="superadmin@fluent.edu.vn"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          prepend-inner-icon="mdi-email-outline"
        />

        <v-text-field
          v-model="loginPassword"
          label="Admin Password:"
          type="password"
          placeholder="••••••••"
          variant="outlined"
          density="comfortable"
          class="mb-4"
          prepend-inner-icon="mdi-lock-outline"
          @keyup.enter="handleAdminSignIn"
        />

        <v-btn
          color="indigo-darken-4"
          variant="flat"
          block
          size="large"
          class="font-weight-black text-none"
          :loading="isLoggingIn"
          @click="handleAdminSignIn"
        >
          Sign In to Admin Console
        </v-btn>
      </v-card>
    </div>

    <!-- Authenticated Admin Console Workspace -->
    <div v-else>
      <!-- Admin Header Banner -->
      <v-card border flat class="pa-4 mb-4 bg-gradient-dark text-white rounded-lg elevation-2">
        <div class="d-flex align-center justify-space-between flex-wrap ga-3">
          <div class="d-flex align-center ga-3">
            <v-avatar color="white" size="48" class="elevation-2">
              <v-icon color="grey-darken-4" size="large">mdi-shield-crown-outline</v-icon>
            </v-avatar>
            <div>
              <div class="text-h6 font-weight-black tracking-tight">ENTERPRISE SYSTEM ADMIN CONSOLE</div>
              <div class="text-caption opacity-90 font-weight-medium">
                Manage multi-tenant school organizations, provision educator accounts, seat licenses, & Supabase 60-day auto-cleanup
              </div>
            </div>
          </div>

          <div class="d-flex align-center ga-2">
            <v-chip color="amber" variant="flat" class="font-weight-black text-black">
              Role: {{ activeUserRole.toUpperCase() }}
            </v-chip>
            <v-btn color="white" variant="outlined" size="small" class="font-weight-bold text-none" @click="handleAdminSignOut">
              Sign Out
            </v-btn>
          </div>
        </div>
      </v-card>

      <!-- Super Admin KPI Metrics -->
      <v-row class="mb-4" density="comfortable">
        <v-col cols="12" sm="3">
          <v-card border flat class="pa-3 bg-white rounded-lg d-flex align-center ga-3">
            <v-avatar color="indigo-lighten-5" size="42" class="text-indigo">
              <v-icon size="default">mdi-domain</v-icon>
            </v-avatar>
            <div>
              <div class="text-caption font-weight-bold text-grey">School Organizations</div>
              <div class="text-h6 font-weight-black text-secondary">{{ overview.total_tenants }}</div>
            </div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="3">
          <v-card border flat class="pa-3 bg-white rounded-lg d-flex align-center ga-3">
            <v-avatar color="teal-lighten-5" size="42" class="text-teal-darken-3">
              <v-icon size="default">mdi-account-tie</v-icon>
            </v-avatar>
            <div>
              <div class="text-caption font-weight-bold text-grey">Enrolled Educators</div>
              <div class="text-h6 font-weight-black text-teal-darken-3">{{ overview.total_teachers }}</div>
            </div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="3">
          <v-card border flat class="pa-3 bg-white rounded-lg d-flex align-center ga-3">
            <v-avatar color="purple-lighten-5" size="42" class="text-purple-darken-3">
              <v-icon size="default">mdi-account-school-outline</v-icon>
            </v-avatar>
            <div>
              <div class="text-caption font-weight-bold text-grey">Active Student Seats</div>
              <div class="text-h6 font-weight-black text-purple-darken-3">{{ overview.total_students }}</div>
            </div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="3">
          <v-card border flat class="pa-3 bg-white rounded-lg d-flex align-center ga-3">
            <v-avatar color="blue-lighten-5" size="42" class="text-blue-darken-3">
              <v-icon size="default">mdi-cloud-outline</v-icon>
            </v-avatar>
            <div>
              <div class="text-caption font-weight-bold text-grey">Supabase Storage (0 VND)</div>
              <div class="text-h6 font-weight-black text-blue-darken-3">
                {{ overview.supabase_storage_used_mb }} MB / {{ overview.supabase_storage_limit_mb }} MB
              </div>
            </div>
          </v-card>
        </v-col>
      </v-row>

      <!-- Main Admin Workspace -->
      <v-card border flat class="pa-4 bg-white rounded-lg">
        <v-tabs v-model="activeTab" color="primary" density="compact" class="mb-4">
          <v-tab value="tenants" class="font-weight-black text-none" prepend-icon="mdi-domain">
            School Organizations (Tenants)
          </v-tab>
          <v-tab value="provision" class="font-weight-black text-none" prepend-icon="mdi-account-plus-outline">
            Account Provisioning
          </v-tab>
          <v-tab value="cleanup" class="font-weight-black text-none" prepend-icon="mdi-broom">
            Auto-Cleanup Worker (60 Days)
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <!-- Sub-Tab 1: Tenants List & Create -->
          <v-window-item value="tenants">
            <div class="d-flex align-center justify-space-between mb-3">
              <span class="text-subtitle-2 font-weight-black text-secondary">B2B SCHOOL TENANTS DIRECTORY</span>
              <v-btn color="primary" size="small" variant="flat" class="font-weight-bold text-none" prepend-icon="mdi-plus" @click="showCreateTenantModal = true">
                Create New School Tenant
              </v-btn>
            </div>

            <v-table density="comfortable" hover class="border rounded-lg">
              <thead>
                <tr class="bg-grey-lighten-4">
                  <th class="font-weight-black text-caption text-secondary">TENANT ID</th>
                  <th class="font-weight-black text-caption text-secondary">SCHOOL NAME</th>
                  <th class="font-weight-black text-caption text-secondary text-center">SEAT LICENSES</th>
                  <th class="font-weight-black text-caption text-secondary text-center">EXPIRY DATE</th>
                  <th class="font-weight-black text-caption text-secondary text-center">STATUS</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in overview.tenants" :key="t.id">
                  <td class="font-weight-bold text-caption font-weight-mono text-primary">{{ t.id }}</td>
                  <td class="font-weight-black text-body-2">{{ t.name }}</td>
                  <td class="text-center font-weight-bold text-caption">{{ t.license_seats }} Seats</td>
                  <td class="text-center text-caption text-grey">{{ t.license_expiry }}</td>
                  <td class="text-center">
                    <v-chip size="x-small" color="success" variant="flat" class="font-weight-black">ACTIVE</v-chip>
                  </td>
                </tr>
                <tr v-if="!overview.tenants?.length">
                  <td colspan="5" class="text-center pa-6 text-caption text-grey">
                    No school organizations created yet. Click "Create New School Tenant" above!
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-window-item>

          <!-- Sub-Tab 2: Account Provisioning -->
          <v-window-item value="provision">
            <v-row density="comfortable">
              <v-col cols="12" md="6">
                <v-card border flat class="pa-4 bg-grey-lighten-5 rounded-lg">
                  <div class="text-subtitle-2 font-weight-black text-primary mb-3">PROVISION EDUCATOR / ADMIN ACCOUNT</div>
                  <v-text-field
                    v-model="newProvEmail"
                    label="Login Email:"
                    placeholder="teacher@school.edu.vn"
                    variant="outlined"
                    density="comfortable"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="newProvName"
                    label="Full Name:"
                    placeholder="Prof. Alex Smith"
                    variant="outlined"
                    density="comfortable"
                    class="mb-2"
                  />
                  <v-select
                    v-model="newProvRole"
                    :items="[{ title: 'Educator / Teacher', value: 'teacher' }, { title: 'School Admin (Department Head)', value: 'admin' }]"
                    label="Permission Level (Role):"
                    variant="outlined"
                    density="comfortable"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="newProvPassword"
                    label="Default Password:"
                    placeholder="password123"
                    variant="outlined"
                    density="comfortable"
                    class="mb-3"
                  />
                  <v-btn color="primary" variant="flat" block class="font-weight-black text-none" :loading="isProvisioning" @click="submitProvisioning">
                    Provision Account & Parent Code
                  </v-btn>
                </v-card>
              </v-col>

              <v-col cols="12" md="6">
                <v-card border flat class="pa-4 bg-indigo-lighten-5 rounded-lg border-indigo">
                  <div class="text-subtitle-2 font-weight-black text-indigo-darken-3 mb-2">ROLE-BASED ACCESS CONTROL (RBAC RULES)</div>
                  <div class="text-caption text-grey-darken-3">
                    <ul class="pl-4">
                      <li class="mb-1">Admin accounts <strong>cannot self-register</strong>. Strictly provisioned by Super Admin.</li>
                      <li class="mb-1">Educators can self-register at `/teacher` or receive provisioned credentials.</li>
                      <li class="mb-1">Provisioned accounts auto-generate a unique <strong>Parent Tracking Code (`PA-xxxx`)</strong>.</li>
                    </ul>
                  </div>
                </v-card>
              </v-col>
            </v-row>
          </v-window-item>

          <!-- Sub-Tab 3: Auto-Cleanup Worker -->
          <v-window-item value="cleanup">
            <v-card border flat class="pa-4 bg-teal-lighten-5 rounded-lg border-teal">
              <div class="d-flex align-center justify-space-between flex-wrap ga-2 mb-2">
                <div>
                  <div class="text-subtitle-1 font-weight-black text-teal-darken-3">ZERO-COST STORAGE MAINTENANCE (SUPABASE AUTO-CLEANUP WORKER)</div>
                  <div class="text-caption text-teal-darken-4">
                    Purges audio recordings older than 60 days from Supabase Storage while preserving gradebook score records in Database.
                  </div>
                </div>
                <v-btn color="teal-darken-2" variant="flat" class="font-weight-black text-none" prepend-icon="mdi-broom" @click="runAutoCleanup">
                  Trigger Storage Purge Worker
                </v-btn>
              </div>
            </v-card>
          </v-window-item>
        </v-window>
      </v-card>

      <!-- Modal: Create New Tenant -->
      <v-dialog v-model="showCreateTenantModal" max-width="450">
        <v-card border rounded="lg" class="pa-4">
          <div class="text-subtitle-1 font-weight-black text-primary mb-3">Create New B2B School Organization</div>
          <v-text-field
            v-model="newTenantName"
            label="School Organization Name:"
            placeholder="ABC Academy School"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />
          <v-text-field
            v-model="newTenantSeats"
            label="Purchased Seat Licenses:"
            type="number"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showCreateTenantModal = false">Cancel</v-btn>
            <v-btn color="primary" variant="flat" class="text-none font-weight-bold" @click="submitCreateTenant">Activate Organization</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  backendUrl: String,
  userRole: String
})

const activeUserRole = ref(localStorage.getItem('user_role') || 'student')
const loginEmail = ref('superadmin@fluent.edu.vn')
const loginPassword = ref('')
const isLoggingIn = ref(false)
const loginError = ref('')

const toast = ref({ show: false, text: '', color: 'success', icon: 'mdi-check-circle' })
const notify = (text, color = 'success', icon = 'mdi-check-circle') => {
  toast.value = { show: true, text, color, icon }
}

const activeTab = ref('tenants')
const overview = ref({ total_tenants: 0, total_teachers: 0, total_students: 0, total_submissions: 0, tenants: [] })

const showCreateTenantModal = ref(false)
const newTenantName = ref('')
const newTenantSeats = ref(350)

const newProvEmail = ref('')
const newProvName = ref('')
const newProvRole = ref('teacher')
const newProvPassword = ref('password123')
const isProvisioning = ref(false)

const handleAdminSignIn = async () => {
  if (!loginEmail.value.trim() || !loginPassword.value.trim()) return
  isLoggingIn.value = true
  loginError.value = ''
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: loginEmail.value.trim(),
        password: loginPassword.value.trim()
      })
    })
    if (res.ok) {
      const data = await res.json()
      activeUserRole.value = data.user.role
      localStorage.setItem('user_role', data.user.role)
      notify(`Welcome! Authenticated as ${data.user.role.toUpperCase()}`, 'success', 'mdi-shield-check')
      await fetchOverview()
    } else {
      const err = await res.json()
      loginError.value = err.detail || 'Invalid Admin Email or Password.'
    }
  } catch (e) {
    loginError.value = 'Sign In Error: ' + e.message
  } finally {
    isLoggingIn.value = false
  }
}

const handleAdminSignOut = () => {
  activeUserRole.value = 'student'
  localStorage.setItem('user_role', 'student')
  notify('Signed out from Admin Console.', 'info', 'mdi-information-outline')
}

const fetchOverview = async () => {
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/overview`)
    if (res.ok) {
      overview.value = await res.json()
    }
  } catch (e) {
    console.error('Fetch admin overview error:', e)
  }
}

const submitCreateTenant = async () => {
  if (!newTenantName.value.trim()) return
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/tenants/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: newTenantName.value.trim(),
        license_seats: Number(newTenantSeats.value) || 350
      })
    })
    if (res.ok) {
      showCreateTenantModal.value = false
      newTenantName.value = ''
      notify('New B2B School Organization created successfully!', 'success')
      await fetchOverview()
    }
  } catch (e) {
    notify('Failed to create tenant: ' + e.message, 'error', 'mdi-alert-circle')
  }
}

const submitProvisioning = async () => {
  if (!newProvEmail.value.trim() || !newProvName.value.trim()) return
  isProvisioning.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/provision-account`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: newProvEmail.value.trim(),
        name: newProvName.value.trim(),
        role: newProvRole.value,
        password: newProvPassword.value.trim()
      })
    })
    if (res.ok) {
      notify('Account and Parent Code provisioned successfully!', 'success', 'mdi-account-check')
      newProvEmail.value = ''
      newProvName.value = ''
      await fetchOverview()
    }
  } catch (e) {
    notify('Provisioning error: ' + e.message, 'error', 'mdi-alert-circle')
  } finally {
    isProvisioning.value = false
  }
}

const runAutoCleanup = async () => {
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/auto-cleanup`, { method: 'POST' })
    if (res.ok) {
      const data = await res.json()
      notify(data.message, 'success', 'mdi-broom')
    }
  } catch (e) {
    notify('Auto-cleanup error: ' + e.message, 'error', 'mdi-alert-circle')
  }
}

onMounted(() => {
  if (['admin', 'super_admin'].includes(activeUserRole.value)) {
    fetchOverview()
  }
})
</script>

<style scoped>
.bg-gradient-dark {
  background: linear-gradient(135deg, #212121 0%, #000000 100%);
}
</style>
