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
            <v-btn color="white" variant="outlined" size="small" class="font-weight-bold text-none" prepend-icon="mdi-logout" @click="showLogoutDialog = true">
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
                  <th class="font-weight-black text-caption text-secondary text-center">ACTION</th>
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
                  <td class="text-center">
                    <div class="d-flex align-center justify-center ga-1">
                      <v-btn size="x-small" icon="mdi-pencil-outline" color="primary" variant="tonal" title="Edit Tenant" @click="openEditTenantModal(t)" />
                      <v-btn size="x-small" icon="mdi-delete-outline" color="error" variant="tonal" title="Delete Tenant" @click="confirmDeleteTenant(t)" />
                    </div>
                  </td>
                </tr>
                <tr v-if="!overview.tenants?.length">
                  <td colspan="6" class="text-center pa-6 text-caption text-grey">
                    No school organizations created yet. Click "Create New School Tenant" above!
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-window-item>

          <!-- Sub-Tab 2: Account Provisioning & User Directory -->
          <v-window-item value="provision">
            <v-row density="comfortable" class="mb-4">
              <v-col cols="12" md="5">
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

              <v-col cols="12" md="7">
                <v-card border flat class="pa-4 bg-white rounded-lg">
                  <div class="d-flex align-center justify-space-between mb-3">
                    <span class="text-subtitle-2 font-weight-black text-secondary">PROVISIONED ACCOUNTS DIRECTORY</span>
                    <v-text-field
                      v-model="searchUserText"
                      placeholder="Search email or name..."
                      variant="outlined"
                      density="compact"
                      hide-details
                      prepend-inner-icon="mdi-magnify"
                      style="max-width: 220px;"
                    />
                  </div>

                  <v-table density="comfortable" hover class="border rounded-lg">
                    <thead>
                      <tr class="bg-grey-lighten-4">
                        <th class="font-weight-black text-caption text-secondary">NAME & EMAIL</th>
                        <th class="font-weight-black text-caption text-secondary text-center">ROLE</th>
                        <th class="font-weight-black text-caption text-secondary text-center">PARENT CODE</th>
                        <th class="font-weight-black text-caption text-secondary text-center">ACTION</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="usr in filteredAdminUsers" :key="usr.id">
                        <td class="font-weight-bold text-body-2 pa-2">
                          <div>{{ usr.name }}</div>
                          <div class="text-caption text-grey">{{ usr.email }}</div>
                        </td>
                        <td class="text-center">
                          <v-chip size="x-small" :color="usr.role === 'admin' ? 'indigo' : 'teal'" variant="flat" class="font-weight-black">
                            {{ usr.role.toUpperCase() }}
                          </v-chip>
                        </td>
                        <td class="text-center font-weight-mono text-caption text-primary">
                          {{ usr.parent_code || 'N/A' }}
                        </td>
                        <td class="text-center">
                          <div class="d-flex align-center justify-center ga-1">
                            <v-btn size="x-small" icon="mdi-pencil-outline" color="primary" variant="tonal" title="Edit User" @click="openEditUserModal(usr)" />
                            <v-btn size="x-small" icon="mdi-delete-outline" color="error" variant="tonal" title="Delete User" @click="confirmDeleteUser(usr)" />
                          </div>
                        </td>
                      </tr>
                      <tr v-if="!filteredAdminUsers.length">
                        <td colspan="4" class="text-center pa-4 text-caption text-grey">
                          No provisioned accounts found.
                        </td>
                      </tr>
                    </tbody>
                  </v-table>
                </v-card>
              </v-col>
            </v-row>
          </v-window-item>

          <!-- Sub-Tab 3: Auto-Cleanup Worker & System Config -->
          <v-window-item value="cleanup">
            <v-card border flat class="pa-4 bg-teal-lighten-5 rounded-lg border-teal mb-4">
              <div class="d-flex align-center justify-space-between flex-wrap ga-2 mb-2">
                <div>
                  <div class="text-subtitle-1 font-weight-black text-teal-darken-3">ZERO-COST STORAGE MAINTENANCE (SUPABASE AUTO-CLEANUP WORKER)</div>
                  <div class="text-caption text-teal-darken-4">
                    Purges audio recordings older than retention threshold from Supabase Storage while preserving gradebook score records in Database.
                  </div>
                </div>
                <v-btn color="teal-darken-2" variant="flat" class="font-weight-black text-none" prepend-icon="mdi-broom" @click="runAutoCleanup">
                  Trigger Storage Purge Worker
                </v-btn>
              </div>
            </v-card>

            <!-- System Settings Form -->
            <v-card border flat class="pa-4 bg-white rounded-lg">
              <div class="text-subtitle-2 font-weight-black text-primary mb-3">SUPER ADMIN STORAGE CONFIGURATION</div>
              <v-row density="comfortable" align="center">
                <v-col cols="12" sm="6" md="4">
                  <v-text-field
                    v-model.number="retentionDaysInput"
                    label="Audio Retention Policy (Days):"
                    type="number"
                    variant="outlined"
                    density="comfortable"
                    prepend-inner-icon="mdi-calendar-range"
                    hide-details
                  />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-btn color="primary" variant="flat" class="font-weight-black text-none" :loading="isSavingSettings" @click="saveSystemSettings">
                    Save Retention Settings
                  </v-btn>
                </v-col>
              </v-row>
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

      <!-- Modal: Edit Tenant -->
      <v-dialog v-model="showEditTenantModal" max-width="450">
        <v-card border rounded="lg" class="pa-4">
          <div class="text-subtitle-1 font-weight-black text-primary mb-3">Edit B2B School Organization</div>
          <v-text-field
            v-model="editTenantName"
            label="School Organization Name:"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />
          <v-text-field
            v-model.number="editTenantSeats"
            label="Purchased Seat Licenses:"
            type="number"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />
          <v-text-field
            v-model="editTenantExpiry"
            label="License Expiry Date:"
            placeholder="2027-08-01"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showEditTenantModal = false">Cancel</v-btn>
            <v-btn color="primary" variant="flat" class="text-none font-weight-bold" :loading="isUpdatingTenant" @click="submitEditTenant">Save Changes</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Delete Tenant Confirmation -->
      <v-dialog v-model="showDeleteTenantModal" max-width="400">
        <v-card border rounded="lg" class="pa-4">
          <div class="text-subtitle-1 font-weight-black text-error mb-2">Delete School Organization</div>
          <div class="text-body-2 text-grey-darken-2 mb-4">
            Are you sure you want to delete school organization <strong>{{ tenantToDelete?.name }}</strong>?
          </div>
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showDeleteTenantModal = false">Cancel</v-btn>
            <v-btn color="error" variant="flat" class="text-none font-weight-bold" :loading="isDeletingTenant" @click="submitDeleteTenant">Delete Tenant</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Edit Provisioned User -->
      <v-dialog v-model="showEditUserModal" max-width="450">
        <v-card border rounded="lg" class="pa-4">
          <div class="text-subtitle-1 font-weight-black text-primary mb-3">Edit Provisioned User Account</div>
          <v-text-field
            v-model="editUserEmail"
            label="Login Email:"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />
          <v-text-field
            v-model="editUserName"
            label="Full Name:"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />
          <v-select
            v-model="editUserRole"
            :items="[{ title: 'Educator / Teacher', value: 'teacher' }, { title: 'School Admin', value: 'admin' }]"
            label="Role:"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />
          <v-text-field
            v-model="editUserPassword"
            label="Reset Password (Optional):"
            placeholder="Leave empty to keep current"
            type="password"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showEditUserModal = false">Cancel</v-btn>
            <v-btn color="primary" variant="flat" class="text-none font-weight-bold" :loading="isUpdatingUser" @click="submitEditUser">Save User</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Delete User Confirmation -->
      <v-dialog v-model="showDeleteUserModal" max-width="400">
        <v-card border rounded="lg" class="pa-4">
          <div class="text-subtitle-1 font-weight-black text-error mb-2">Delete Provisioned Account</div>
          <div class="text-body-2 text-grey-darken-2 mb-4">
            Are you sure you want to delete account <strong>{{ userToDelete?.email }}</strong>?
          </div>
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showDeleteUserModal = false">Cancel</v-btn>
            <v-btn color="error" variant="flat" class="text-none font-weight-bold" :loading="isDeletingUser" @click="submitDeleteUser">Delete Account</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Sign Out Confirmation -->
      <v-dialog v-model="showLogoutDialog" max-width="400">
        <v-card border rounded="lg" class="pa-4 bg-white">
          <div class="d-flex align-center ga-3 mb-3">
            <v-avatar color="red-lighten-5" size="40" class="text-error border">
              <v-icon size="default">mdi-logout-variant</v-icon>
            </v-avatar>
            <div>
              <div class="text-subtitle-1 font-weight-black text-secondary">Confirm Sign Out</div>
              <div class="text-caption text-grey-darken-1">Are you sure you want to sign out from Admin Console?</div>
            </div>
          </div>
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showLogoutDialog = false">Cancel</v-btn>
            <v-btn color="error" variant="flat" class="text-none font-weight-bold" prepend-icon="mdi-logout" @click="confirmAdminSignOut">
              Sign Out
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  backendUrl: String,
  userRole: String
})

const router = useRouter()

const activeUserRole = ref(localStorage.getItem('user_role') || 'student')
const loginEmail = ref('')
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

const showLogoutDialog = ref(false)

const confirmAdminSignOut = () => {
  showLogoutDialog.value = false
  handleAdminSignOut()
}

const handleAdminSignOut = () => {
  activeUserRole.value = 'student'
  localStorage.setItem('user_role', 'student')
  loginEmail.value = ''
  loginPassword.value = ''
  notify('Signed out from Admin Console.', 'info', 'mdi-logout')
  router.push('/')
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
      await fetchAdminUsers()
    }
  } catch (e) {
    notify('Provisioning error: ' + e.message, 'error', 'mdi-alert-circle')
  } finally {
    isProvisioning.value = false
  }
}

// Edit / Delete Tenant states
const showEditTenantModal = ref(false)
const editingTenant = ref(null)
const editTenantName = ref('')
const editTenantSeats = ref(350)
const editTenantExpiry = ref('2027-08-01')
const isUpdatingTenant = ref(false)

const showDeleteTenantModal = ref(false)
const tenantToDelete = ref(null)
const isDeletingTenant = ref(false)

// User Directory & Edit / Delete User states
const adminUsers = ref([])
const searchUserText = ref('')
const filteredAdminUsers = computed(() => {
  if (!searchUserText.value.trim()) return adminUsers.value
  const q = searchUserText.value.toLowerCase().trim()
  return adminUsers.value.filter(u => (u.name || '').toLowerCase().includes(q) || (u.email || '').toLowerCase().includes(q))
})

const showEditUserModal = ref(false)
const editingUser = ref(null)
const editUserName = ref('')
const editUserEmail = ref('')
const editUserRole = ref('teacher')
const editUserPassword = ref('')
const isUpdatingUser = ref(false)

const showDeleteUserModal = ref(false)
const userToDelete = ref(null)
const isDeletingUser = ref(false)

// Storage Settings states
const retentionDaysInput = ref(60)
const isSavingSettings = ref(false)

const fetchAdminUsers = async () => {
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/users`)
    if (res.ok) {
      const data = await res.json()
      adminUsers.value = data.users || []
    }
  } catch (e) {
    console.error('Fetch admin users error:', e)
  }
}

const openEditTenantModal = (t) => {
  editingTenant.value = t
  editTenantName.value = t.name
  editTenantSeats.value = t.license_seats || 350
  editTenantExpiry.value = t.license_expiry || '2027-08-01'
  showEditTenantModal.value = true
}

const submitEditTenant = async () => {
  if (!editingTenant.value || !editTenantName.value.trim()) return
  isUpdatingTenant.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/tenants/${editingTenant.value.id}/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: editTenantName.value.trim(),
        license_seats: Number(editTenantSeats.value) || 350,
        license_expiry: editTenantExpiry.value.trim()
      })
    })
    if (res.ok) {
      showEditTenantModal.value = false
      notify('School Organization updated successfully!', 'success')
      await fetchOverview()
    }
  } catch (e) {
    notify('Failed to update tenant: ' + e.message, 'error', 'mdi-alert-circle')
  } finally {
    isUpdatingTenant.value = false
  }
}

const confirmDeleteTenant = (t) => {
  tenantToDelete.value = t
  showDeleteTenantModal.value = true
}

const submitDeleteTenant = async () => {
  if (!tenantToDelete.value) return
  isDeletingTenant.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/tenants/${tenantToDelete.value.id}`, {
      method: 'DELETE'
    })
    if (res.ok) {
      showDeleteTenantModal.value = false
      notify('School Organization deleted.', 'info')
      await fetchOverview()
    }
  } catch (e) {
    notify('Failed to delete tenant: ' + e.message, 'error', 'mdi-alert-circle')
  } finally {
    isDeletingTenant.value = false
  }
}

const openEditUserModal = (usr) => {
  editingUser.value = usr
  editUserName.value = usr.name
  editUserEmail.value = usr.email
  editUserRole.value = usr.role
  editUserPassword.value = ''
  showEditUserModal.value = true
}

const submitEditUser = async () => {
  if (!editingUser.value || !editUserEmail.value.trim()) return
  isUpdatingUser.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/users/${editingUser.value.id}/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: editUserName.value.trim(),
        email: editUserEmail.value.trim(),
        role: editUserRole.value,
        password: editUserPassword.value.trim()
      })
    })
    if (res.ok) {
      showEditUserModal.value = false
      notify('User account updated successfully!', 'success')
      await fetchAdminUsers()
    }
  } catch (e) {
    notify('Failed to update user: ' + e.message, 'error', 'mdi-alert-circle')
  } finally {
    isUpdatingUser.value = false
  }
}

const confirmDeleteUser = (usr) => {
  userToDelete.value = usr
  showDeleteUserModal.value = true
}

const submitDeleteUser = async () => {
  if (!userToDelete.value) return
  isDeletingUser.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/users/${userToDelete.value.id}`, {
      method: 'DELETE'
    })
    if (res.ok) {
      showDeleteUserModal.value = false
      notify('User account deleted.', 'info')
      await fetchAdminUsers()
    }
  } catch (e) {
    notify('Failed to delete user: ' + e.message, 'error', 'mdi-alert-circle')
  } finally {
    isDeletingUser.value = false
  }
}

const fetchSystemSettings = async () => {
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/settings`)
    if (res.ok) {
      const data = await res.json()
      retentionDaysInput.value = data.retention_days || 60
    }
  } catch (e) {
    console.error('Fetch system settings error:', e)
  }
}

const saveSystemSettings = async () => {
  isSavingSettings.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/settings/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ retention_days: Number(retentionDaysInput.value) || 60 })
    })
    if (res.ok) {
      notify('System storage retention settings updated!', 'success')
    }
  } catch (e) {
    notify('Failed to save settings: ' + e.message, 'error', 'mdi-alert-circle')
  } finally {
    isSavingSettings.value = false
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
    fetchAdminUsers()
    fetchSystemSettings()
  }
})
</script>

<style scoped>
.bg-gradient-dark {
  background: linear-gradient(135deg, #212121 0%, #000000 100%);
}
</style>
