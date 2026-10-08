<template>
  <v-container fluid class="pa-4 pa-md-6" style="max-width: 1200px;">
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

    <!-- Embedded Admin Login View if Not Authenticated as Admin or Super Admin -->
    <div v-if="!['admin', 'super_admin'].includes(activeUserRole)" class="d-flex justify-center py-12">
      <v-card border flat class="pa-6 bg-white rounded-lg elevation-3" style="max-width: 440px; width: 100%;">
        <div class="text-center mb-4">
          <v-avatar color="indigo-darken-4" size="56" class="text-white mb-2 elevation-2">
            <v-icon size="large">mdi-shield-lock-outline</v-icon>
          </v-avatar>
          <div class="text-h6 font-weight-black text-indigo-darken-4">SYSTEM ADMINISTRATION PORTAL</div>
          <div class="text-caption text-grey-darken-1 font-weight-medium">
            Authorized Super Admins and School Administrators Only
          </div>
        </div>

        <v-alert v-if="loginError" type="error" variant="tonal" density="compact" class="mb-3 text-caption font-weight-bold">
          {{ loginError }}
        </v-alert>

        <v-text-field
          v-model="loginEmail"
          label="Administrator Email:"
          placeholder="superadmin@fluent.edu.vn"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          prepend-inner-icon="mdi-email-outline"
        />

        <v-text-field
          v-model="loginPassword"
          label="Password:"
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
          Sign In to Administration Console
        </v-btn>
      </v-card>
    </div>

    <!-- Authenticated Administration Workspace -->
    <div v-else>
      <!-- SUPPORT INSPECTION MODE BANNER -->
      <v-alert
        v-if="isSupportMode"
        color="amber-darken-3"
        theme="dark"
        variant="flat"
        density="comfortable"
        class="mb-4 rounded-lg font-weight-bold elevation-2"
        icon="mdi-shield-account"
      >
        <div class="d-flex align-center justify-space-between flex-wrap ga-2">
          <div>
            <span class="text-subtitle-2 font-weight-black">SUPPORT & INSPECTION MODE ACTIVE</span>
            <div class="text-caption font-weight-medium text-amber-lighten-4">
              Currently inspecting <strong>{{ supportSchoolName }}</strong> as School Admin (<strong>{{ supportAdminEmail }}</strong>). Actions are scoped to this school organization.
            </div>
          </div>
          <v-btn
            color="black"
            size="small"
            variant="flat"
            class="text-none font-weight-black text-white"
            prepend-icon="mdi-logout-variant"
            @click="exitSupportMode"
          >
            Exit Support Mode
          </v-btn>
        </div>
      </v-alert>

      <!-- HEADER BANNER: Super Admin vs School Admin -->
      <!-- Case A: SUPER ADMIN Header -->
      <v-card
        v-if="isSuperAdmin"
        border
        flat
        class="pa-4 mb-4 bg-gradient-purple text-white rounded-lg elevation-2"
        style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 60%, #4338ca 100%);"
      >
        <div class="d-flex align-center justify-space-between flex-wrap ga-3">
          <div class="d-flex align-center ga-3">
            <v-avatar color="amber-darken-2" size="48" class="text-white elevation-2">
              <v-icon size="large">mdi-shield-crown</v-icon>
            </v-avatar>
            <div>
              <div class="text-h6 font-weight-black tracking-tight d-flex align-center ga-2">
                <span>ENTERPRISE PLATFORM SUPER ADMIN</span>
                <v-chip size="x-small" color="amber" variant="flat" class="font-weight-black text-black">
                  GLOBAL OWNER
                </v-chip>
              </div>
              <div class="text-caption text-indigo-lighten-4 font-weight-medium">
                Multi-tenant school governance, seat licenses, cross-organization audits, & cloud infrastructure
              </div>
            </div>
          </div>

          <div class="d-flex align-center flex-wrap ga-2">
            <!-- Organization Scope Switcher for Super Admin -->
            <v-select
              v-model="selectedTenantScope"
              :items="tenantScopeOptions"
              item-title="title"
              item-value="value"
              density="compact"
              variant="solo"
              hide-details
              bg-color="white"
              class="font-weight-bold"
              style="min-width: 200px; max-width: 240px;"
              @update:model-value="onTenantScopeChange"
            />
            <v-btn color="white" variant="outlined" size="small" class="font-weight-bold text-none" prepend-icon="mdi-logout" @click="showLogoutDialog = true">
              Sign Out
            </v-btn>
          </div>
        </div>
      </v-card>

      <!-- Case B: SCHOOL ADMIN Header (Strict Data Isolation) -->
      <v-card
        v-else
        border
        flat
        class="pa-4 mb-4 text-white rounded-lg elevation-2"
        style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #0369a1 100%);"
      >
        <div class="d-flex align-center justify-space-between flex-wrap ga-3 mb-3">
          <div class="d-flex align-center ga-3">
            <v-avatar color="light-blue-darken-3" size="48" class="text-white elevation-2">
              <v-icon size="large">mdi-domain</v-icon>
            </v-avatar>
            <div>
              <div class="text-h6 font-weight-black tracking-tight d-flex align-center ga-2">
                <span>SCHOOL ADMIN CONSOLE</span>
                <v-chip size="x-small" color="cyan-lighten-3" variant="flat" class="font-weight-black text-grey-darken-4">
                  {{ overview.current_tenant?.name || 'School Organization' }}
                </v-chip>
              </div>
              <div class="text-caption text-blue-lighten-4 font-weight-medium">
                Manage your school's educators, student seats, classrooms, and homework submissions
              </div>
            </div>
          </div>

          <div class="d-flex align-center ga-2">
            <v-chip color="teal-lighten-4" variant="flat" class="font-weight-black text-teal-darken-4">
              School ID: {{ userTenantId || '1' }}
            </v-chip>
            <v-btn color="white" variant="outlined" size="small" class="font-weight-bold text-none" prepend-icon="mdi-logout" @click="showLogoutDialog = true">
              Sign Out
            </v-btn>
          </div>
        </div>

        <!-- Seat License Meter for School Admin -->
        <div class="bg-black-subtle pa-3 rounded-lg border border-opacity-25 border-white">
          <div class="d-flex align-center justify-space-between text-caption font-weight-bold mb-1">
            <span>Student Seat License Allocation:</span>
            <span>
              <strong>{{ overview.used_seats || 0 }}</strong> / <strong>{{ overview.license_seats || 100 }}</strong> Seats Used
              ({{ Math.max(0, (overview.license_seats || 100) - (overview.used_seats || 0)) }} Seats Remaining)
            </span>
          </div>
          <v-progress-linear
            color="cyan-accent-3"
            bg-color="grey-darken-2"
            rounded
            height="8"
            :model-value="Math.min(100, Math.round(((overview.used_seats || 0) / (overview.license_seats || 100)) * 100))"
          />
        </div>
      </v-card>

      <!-- DYNAMIC KPI METRICS ROW -->
      <v-row class="mb-4" density="comfortable">
        <!-- KPI 1: Tenants (Super Admin) OR Seat Usage (School Admin) -->
        <v-col v-if="isSuperAdmin" cols="12" sm="6" md="2-4">
          <v-card border flat class="pa-3 bg-white rounded-lg d-flex align-center ga-3 cursor-pointer" hover @click="activeTab = 'tenants'">
            <v-avatar color="indigo-lighten-5" size="42" class="text-indigo">
              <v-icon size="default">mdi-domain</v-icon>
            </v-avatar>
            <div>
              <div class="text-caption font-weight-bold text-grey">School Tenants</div>
              <div class="text-h6 font-weight-black text-secondary">{{ overview.total_tenants || 0 }}</div>
            </div>
          </v-card>
        </v-col>

        <!-- KPI 2: Classrooms -->
        <v-col cols="12" sm="6" :md="isSuperAdmin ? '2-4' : '3'">
          <v-card border flat class="pa-3 bg-white rounded-lg d-flex align-center ga-3 cursor-pointer" hover @click="activeTab = 'classrooms'">
            <v-avatar color="blue-lighten-5" size="42" class="text-blue-darken-3">
              <v-icon size="default">mdi-google-classroom</v-icon>
            </v-avatar>
            <div>
              <div class="text-caption font-weight-bold text-grey">Classrooms</div>
              <div class="text-h6 font-weight-black text-blue-darken-3">{{ overview.total_classrooms || 0 }}</div>
            </div>
          </v-card>
        </v-col>

        <!-- KPI 3: Educators -->
        <v-col cols="12" sm="6" :md="isSuperAdmin ? '2-4' : '3'">
          <v-card border flat class="pa-3 bg-white rounded-lg d-flex align-center ga-3 cursor-pointer" hover @click="activeTab = 'users'">
            <v-avatar color="teal-lighten-5" size="42" class="text-teal-darken-3">
              <v-icon size="default">mdi-account-tie</v-icon>
            </v-avatar>
            <div>
              <div class="text-caption font-weight-bold text-grey">Educators</div>
              <div class="text-h6 font-weight-black text-teal-darken-3">{{ overview.total_teachers || 0 }}</div>
            </div>
          </v-card>
        </v-col>

        <!-- KPI 4: Students -->
        <v-col cols="12" sm="6" :md="isSuperAdmin ? '2-4' : '3'">
          <v-card border flat class="pa-3 bg-white rounded-lg d-flex align-center ga-3 cursor-pointer" hover @click="activeTab = 'users'">
            <v-avatar color="purple-lighten-5" size="42" class="text-purple-darken-3">
              <v-icon size="default">mdi-account-school-outline</v-icon>
            </v-avatar>
            <div>
              <div class="text-caption font-weight-bold text-grey">Active Students</div>
              <div class="text-h6 font-weight-black text-purple-darken-3">{{ overview.total_students || 0 }}</div>
            </div>
          </v-card>
        </v-col>

        <!-- KPI 5: Assignments / Storage -->
        <v-col cols="12" sm="6" :md="isSuperAdmin ? '2-4' : '3'">
          <v-card
            border
            flat
            class="pa-3 bg-white rounded-lg d-flex align-center ga-3 cursor-pointer"
            hover
            @click="activeTab = isSuperAdmin ? 'cleanup' : 'assignments'"
          >
            <v-avatar :color="isSuperAdmin ? 'amber-lighten-5' : 'green-lighten-5'" size="42" :class="isSuperAdmin ? 'text-amber-darken-4' : 'text-green-darken-3'">
              <v-icon size="default">{{ isSuperAdmin ? 'mdi-cloud-outline' : 'mdi-clipboard-check-outline' }}</v-icon>
            </v-avatar>
            <div>
              <div class="text-caption font-weight-bold text-grey">{{ isSuperAdmin ? 'Supabase Storage' : 'Homework Assigned' }}</div>
              <div class="text-h6 font-weight-black text-secondary">
                {{ isSuperAdmin ? `${overview.supabase_storage_used_mb || 0} MB` : (overview.total_assignments || 0) }}
              </div>
            </div>
          </v-card>
        </v-col>
      </v-row>

      <!-- MAIN ADMIN WORKSPACE TABS -->
      <v-card border flat class="pa-4 bg-white rounded-lg">
        <v-tabs v-model="activeTab" color="primary" density="compact" class="mb-4">
          <!-- Super Admin Only Tab: Tenants -->
          <v-tab v-if="isSuperAdmin" value="tenants" class="font-weight-black text-none" prepend-icon="mdi-domain">
            School Tenants & Licensing
          </v-tab>

          <!-- Shared Tabs -->
          <v-tab value="classrooms" class="font-weight-black text-none" prepend-icon="mdi-google-classroom">
            Classrooms Directory
          </v-tab>

          <v-tab value="users" class="font-weight-black text-none" prepend-icon="mdi-account-group-outline">
            User Directory & Roles
          </v-tab>

          <v-tab value="assignments" class="font-weight-black text-none" prepend-icon="mdi-clipboard-text-outline">
            Homework & Submissions
          </v-tab>

          <!-- Super Admin Only Tab: Infrastructure -->
          <v-tab v-if="isSuperAdmin" value="cleanup" class="font-weight-black text-none" prepend-icon="mdi-server-security">
            Storage & Maintenance
          </v-tab>

          <!-- Audit Logs Tab (P0) -->
          <v-tab value="audit_logs" class="font-weight-black text-none" prepend-icon="mdi-shield-history">
            Security & Audit Logs
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <!-- TAB 1: School Tenants (Super Admin Only) -->
          <v-window-item v-if="isSuperAdmin" value="tenants">
            <div class="d-flex align-center justify-space-between mb-3 flex-wrap ga-2">
              <div>
                <span class="text-subtitle-2 font-weight-black text-secondary">B2B SCHOOL TENANTS DIRECTORY</span>
                <span class="text-caption text-grey ml-2">({{ (tenantsList.length || overview.tenants?.length || 0) }} organizations registered)</span>
              </div>
              <div class="d-flex align-center ga-2 flex-wrap">
                <v-btn color="secondary" size="small" variant="outlined" class="font-weight-bold text-none" prepend-icon="mdi-database-export-outline" :loading="isExportingSnapshot" @click="downloadBackupSnapshot">
                  Export DB Snapshot
                </v-btn>
                <v-btn color="teal" size="small" variant="outlined" class="font-weight-bold text-none" prepend-icon="mdi-database-import-outline" :loading="isRestoringSnapshot" @click="triggerRestoreSnapshotUpload">
                  Restore Snapshot
                </v-btn>
                <v-btn color="error" size="small" variant="tonal" class="font-weight-bold text-none" prepend-icon="mdi-broom" @click="openConfirmCleanProductionModal">
                  Clean Demo Data
                </v-btn>
                <v-btn color="primary" size="small" variant="flat" class="font-weight-bold text-none" prepend-icon="mdi-school" @click="showOnboardModal = true">
                  Onboard School
                </v-btn>
                <input ref="snapshotFileInput" type="file" accept=".json" style="display: none;" @change="handleSnapshotFileSelected" />
              </div>
            </div>

            <v-table density="comfortable" hover class="border rounded-lg">
              <thead>
                <tr class="bg-grey-lighten-4">
                  <th class="font-weight-black text-caption text-secondary">TENANT ID</th>
                  <th class="font-weight-black text-caption text-secondary">SCHOOL & ADMINISTRATOR</th>
                  <th class="font-weight-black text-caption text-secondary text-center">SEAT LICENSES</th>
                  <th class="font-weight-black text-caption text-secondary text-center">CAMPUS ACTIVITY</th>
                  <th class="font-weight-black text-caption text-secondary text-center">AUDIO STORAGE</th>
                  <th class="font-weight-black text-caption text-secondary text-center">STATUS</th>
                  <th class="font-weight-black text-caption text-secondary text-center">ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in (tenantsList.length ? tenantsList : overview.tenants)" :key="t.id">
                  <td class="font-weight-bold text-caption font-weight-mono text-primary">{{ t.id }}</td>
                  <td>
                    <div class="font-weight-black text-body-2">{{ t.name }}</div>
                    <div class="text-caption text-grey-darken-1 d-flex align-center ga-1" v-if="t.admin_email">
                      <v-icon size="x-small" color="grey">mdi-account-tie</v-icon>
                      <span>{{ t.admin_email }}</span>
                    </div>
                    <div class="text-caption text-amber-darken-3 d-flex align-center ga-1" v-else>
                      <v-icon size="x-small" color="amber-darken-3">mdi-account-alert-outline</v-icon>
                      <span class="font-weight-medium">No admin assigned</span>
                    </div>
                  </td>
                  <td class="text-center">
                    <div class="font-weight-black text-caption">
                      {{ t.student_count ?? t.used_seats ?? 0 }} / {{ t.license_seats }} Seats
                    </div>
                    <v-progress-linear
                      :model-value="t.license_seats ? Math.min(100, Math.round(((t.student_count ?? t.used_seats ?? 0) / t.license_seats) * 100)) : 0"
                      :color="(t.student_count ?? t.used_seats ?? 0) >= t.license_seats ? 'error' : ((t.student_count ?? t.used_seats ?? 0) / t.license_seats > 0.8 ? 'warning' : 'primary')"
                      height="5"
                      rounded
                      class="mt-1"
                      style="max-width: 120px; margin: 0 auto;"
                    />
                    <div class="text-caption text-grey" style="font-size: 11px !important;">
                      Exp: {{ t.license_expiry }}
                    </div>
                  </td>
                  <td class="text-center text-caption font-weight-medium">
                    <div><strong>{{ t.teacher_count ?? 0 }}</strong> Teachers</div>
                    <div class="text-grey"><strong>{{ t.active_class_count ?? t.class_count ?? 0 }}</strong> Active Classes</div>
                  </td>
                  <td class="text-center text-caption">
                    <v-chip size="x-small" color="blue-lighten-4" class="text-blue-darken-4 font-weight-bold">
                      {{ t.audio_storage_mb ?? 0 }} MB
                    </v-chip>
                    <div class="text-grey" style="font-size: 11px !important;">
                      {{ t.submission_count ?? 0 }} Submissions
                    </div>
                  </td>
                  <td class="text-center">
                    <v-chip
                      size="x-small"
                      :color="t.status === 'suspended' ? 'error' : (t.status === 'expired' ? 'warning' : (t.status === 'trial' ? 'info' : 'success'))"
                      variant="flat"
                      class="font-weight-black"
                    >
                      {{ (t.status || 'active').toUpperCase() }}
                    </v-chip>
                  </td>
                  <td class="text-center">
                    <div class="d-flex align-center justify-center ga-1">
                      <v-btn
                        size="x-small"
                        icon="mdi-account-eye-outline"
                        color="secondary"
                        variant="tonal"
                        title="Inspect School (Support Mode)"
                        @click="openInspectSchoolModal(t)"
                      />
                      <v-btn
                        size="x-small"
                        icon="mdi-tune"
                        color="primary"
                        variant="tonal"
                        title="Configure School & Administrator"
                        @click="openLifecycleModal(t)"
                      />
                      <v-btn
                        size="x-small"
                        icon="mdi-delete-outline"
                        color="error"
                        variant="tonal"
                        title="Archive School"
                        @click="confirmDeleteTenant(t)"
                      />
                    </div>
                  </td>
                </tr>
                <tr v-if="!tenantsList.length && !overview.tenants?.length">
                  <td colspan="7" class="text-center pa-6 text-caption text-grey">
                    No school organizations created yet. Click "Onboard School" above!
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-window-item>

          <!-- TAB 2: Classrooms Directory (Shared with Data Isolation) -->
          <v-window-item value="classrooms">
            <div class="d-flex align-center justify-space-between mb-3 flex-wrap ga-2">
              <div class="d-flex align-center flex-wrap ga-2">
                <span class="text-subtitle-2 font-weight-black text-secondary">CLASSROOMS DIRECTORY</span>
                <v-chip-group v-model="activeClassFilter" mandatory density="compact">
                  <v-chip value="all" filter size="small" class="font-weight-bold">All ({{ classroomsList.length }})</v-chip>
                  <v-chip value="active" filter size="small" color="success" class="font-weight-bold">Active</v-chip>
                  <v-chip value="archived" filter size="small" color="grey-darken-1" class="font-weight-bold">Archived</v-chip>
                </v-chip-group>
              </div>

              <div class="d-flex align-center ga-2 flex-wrap">
                <v-text-field
                  v-model="searchClassText"
                  placeholder="Search class or teacher..."
                  variant="outlined"
                  density="compact"
                  hide-details
                  prepend-inner-icon="mdi-magnify"
                  style="max-width: 240px;"
                />
                <v-btn color="primary" size="small" variant="flat" class="font-weight-bold text-none" prepend-icon="mdi-plus-box" @click="showCreateClassModal = true">
                  Create Classroom
                </v-btn>
              </div>
            </div>

            <v-table density="comfortable" hover class="border rounded-lg">
              <thead>
                <tr class="bg-grey-lighten-4">
                  <th class="font-weight-black text-caption text-secondary">CLASS NAME & GRADE</th>
                  <th class="font-weight-black text-caption text-secondary">TEACHER IN CHARGE</th>
                  <th class="font-weight-black text-caption text-secondary text-center">STATUS</th>
                  <th v-if="isSuperAdmin" class="font-weight-black text-caption text-secondary">SCHOOL TENANT</th>
                  <th class="font-weight-black text-caption text-secondary text-center">JOIN CODE</th>
                  <th class="font-weight-black text-caption text-secondary text-center">ENROLLED STUDENTS</th>
                  <th class="font-weight-black text-caption text-secondary text-center">ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="cls in filteredClassrooms" :key="cls.id">
                  <td class="pa-3">
                    <div class="font-weight-black text-body-2 text-indigo-darken-3">{{ cls.name }}</div>
                    <div class="text-caption text-grey">{{ cls.grade_level }}</div>
                  </td>
                  <td>
                    <div class="font-weight-bold text-body-2">{{ cls.teacher_name }}</div>
                    <div class="text-caption text-grey">{{ cls.teacher_email }}</div>
                  </td>
                  <td class="text-center">
                    <v-chip
                      size="x-small"
                      :color="cls.is_archived ? 'grey' : 'success'"
                      variant="flat"
                      class="font-weight-black"
                    >
                      {{ cls.is_archived ? 'ARCHIVED' : 'ACTIVE' }}
                    </v-chip>
                  </td>
                  <td v-if="isSuperAdmin">
                    <v-chip size="x-small" color="blue-lighten-4" class="font-weight-bold text-blue-darken-4">
                      {{ cls.school_name }}
                    </v-chip>
                  </td>
                  <td class="text-center">
                    <v-chip size="small" color="primary" variant="tonal" class="font-weight-mono font-weight-black">
                      {{ cls.join_code }}
                    </v-chip>
                  </td>
                  <td class="text-center">
                    <v-chip
                      size="small"
                      color="indigo-lighten-5"
                      variant="flat"
                      class="font-weight-black text-indigo-darken-3 cursor-pointer"
                      prepend-icon="mdi-account-group"
                      title="Click to view student roster"
                      @click="openClassRoster(cls)"
                    >
                      {{ cls.student_count }} Students
                    </v-chip>
                  </td>
                  <td class="text-center">
                    <div class="d-flex align-center justify-center ga-1">
                      <v-btn
                        size="x-small"
                        icon="mdi-account-switch"
                        color="primary"
                        variant="tonal"
                        title="Reassign Teacher"
                        @click="openAssignTeacherModal(cls)"
                      />
                      <v-btn
                        size="x-small"
                        :icon="cls.is_archived ? 'mdi-archive-arrow-up' : 'mdi-archive-arrow-down'"
                        :color="cls.is_archived ? 'success' : 'amber-darken-3'"
                        variant="tonal"
                        :title="cls.is_archived ? 'Restore Classroom' : 'Archive Classroom'"
                        @click="confirmToggleArchive(cls)"
                      />
                      <v-btn
                        size="x-small"
                        icon="mdi-delete-outline"
                        color="error"
                        variant="tonal"
                        title="Delete Classroom"
                        @click="confirmDeleteClassroom(cls)"
                      />
                    </div>
                  </td>
                </tr>
                <tr v-if="!filteredClassrooms.length">
                  <td :colspan="isSuperAdmin ? 7 : 6" class="text-center pa-6 text-caption text-grey">
                    No classrooms found matching search criteria.
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-window-item>

          <!-- TAB 3: User Directory & Role Assignment -->
          <v-window-item value="users">
            <div class="d-flex align-center justify-space-between mb-3 flex-wrap ga-2">
              <div class="d-flex align-center flex-wrap ga-2">
                <span class="text-subtitle-2 font-weight-black text-secondary">USER DIRECTORY</span>
                <v-chip-group v-model="selectedUserRoleFilter" mandatory density="compact">
                  <v-chip value="all" filter size="small" class="font-weight-bold">All ({{ usersList.length }})</v-chip>
                  <v-chip value="student" filter size="small" color="primary" class="font-weight-bold">Students</v-chip>
                  <v-chip value="teacher" filter size="small" color="teal" class="font-weight-bold">Educators</v-chip>
                  <v-chip value="admin" filter size="small" color="indigo" class="font-weight-bold">Admins</v-chip>
                </v-chip-group>
              </div>

              <div class="d-flex align-center ga-2 flex-wrap">
                <v-text-field
                  v-model="searchUserText"
                  placeholder="Search user name or email..."
                  variant="outlined"
                  density="compact"
                  hide-details
                  prepend-inner-icon="mdi-magnify"
                  style="max-width: 240px;"
                />
                <v-btn color="primary" size="small" variant="flat" class="font-weight-bold text-none" prepend-icon="mdi-account-plus" @click="showProvisionModal = true">
                  Provision Account
                </v-btn>
              </div>
            </div>

            <v-table density="comfortable" hover class="border rounded-lg">
              <thead>
                <tr class="bg-grey-lighten-4">
                  <th class="font-weight-black text-caption text-secondary">USER DETAILS</th>
                  <th class="font-weight-black text-caption text-secondary text-center">ROLE</th>
                  <th class="font-weight-black text-caption text-secondary text-center">STATUS</th>
                  <th v-if="isSuperAdmin" class="font-weight-black text-caption text-secondary">ORGANIZATION</th>
                  <th class="font-weight-black text-caption text-secondary text-center">PRIMARY CLASSROOM</th>
                  <th class="font-weight-black text-caption text-secondary text-center">PARENT TRACKING</th>
                  <th class="font-weight-black text-caption text-secondary text-center">STREAK</th>
                  <th class="font-weight-black text-caption text-secondary text-center">ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="usr in filteredUsers" :key="usr.id">
                  <td class="pa-2">
                    <div class="d-flex align-center ga-2">
                      <v-avatar size="32" color="indigo-lighten-5">
                        <img v-if="usr.avatar" :src="usr.avatar" alt="Avatar" />
                        <span v-else class="text-caption font-weight-bold text-primary">{{ usr.name?.slice(0, 1)?.toUpperCase() || 'U' }}</span>
                      </v-avatar>
                      <div>
                        <div class="font-weight-bold text-body-2">{{ usr.name }}</div>
                        <div class="text-caption text-grey">{{ usr.email }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="text-center">
                    <v-chip
                      size="x-small"
                      :color="getUserRoleColor(usr.role)"
                      variant="flat"
                      class="font-weight-black"
                    >
                      {{ usr.role.toUpperCase() }}
                    </v-chip>
                  </td>
                  <td class="text-center">
                    <v-chip
                      size="x-small"
                      :color="usr.status === 'suspended' ? 'warning' : 'success'"
                      variant="flat"
                      class="font-weight-black"
                    >
                      {{ (usr.status || 'ACTIVE').toUpperCase() }}
                    </v-chip>
                  </td>
                  <td v-if="isSuperAdmin">
                    <template v-if="usr.role === 'teacher'">
                      <v-chip
                        v-if="usr.teacher_type === 'freelance'"
                        size="x-small"
                        color="purple-lighten-5"
                        class="text-purple-darken-3 font-weight-bold"
                      >
                        🎓 Freelance ({{ usr.max_seats || 30 }} seats / {{ usr.max_classes || 3 }} cls)
                      </v-chip>
                      <v-chip
                        v-else
                        size="x-small"
                        color="indigo-lighten-5"
                        class="text-indigo-darken-3 font-weight-bold"
                      >
                        🏫 {{ usr.school_name }}
                      </v-chip>
                    </template>
                    <span v-else class="text-caption font-weight-bold text-grey-darken-2">{{ usr.school_name }}</span>
                  </td>
                  <td class="text-center text-caption font-weight-medium">
                    <v-chip v-if="usr.primary_class && usr.primary_class !== 'None'" size="x-small" color="blue-lighten-5" class="text-blue-darken-3 font-weight-bold">
                      {{ usr.primary_class }}
                    </v-chip>
                    <span v-else class="text-grey">—</span>
                  </td>
                  <td class="text-center font-weight-mono text-caption">
                    <v-chip v-if="usr.parent_code" size="x-small" color="teal-lighten-5" class="text-teal-darken-3 font-weight-bold">
                      {{ usr.parent_code }}
                    </v-chip>
                    <span v-else class="text-grey">N/A</span>
                  </td>
                  <td class="text-center font-weight-bold text-caption text-warning">
                    <span v-if="usr.streak > 0">🔥 {{ usr.streak }}d</span>
                    <span v-else class="text-grey">0d</span>
                  </td>
                  <td class="text-center">
                    <div class="d-flex align-center justify-center ga-1">
                      <!-- Teacher Specific Operations -->
                      <template v-if="usr.role === 'teacher'">
                        <v-btn
                          v-if="isSuperAdmin"
                          size="x-small"
                          icon="mdi-license"
                          color="indigo"
                          variant="tonal"
                          title="Configure Educator Plan & Quotas"
                          @click="openConfigureTeacherPlan(usr)"
                        />
                        <v-btn
                          size="x-small"
                          :icon="usr.status === 'suspended' ? 'mdi-account-check' : 'mdi-account-lock'"
                          :color="usr.status === 'suspended' ? 'success' : 'warning'"
                          variant="tonal"
                          :title="usr.status === 'suspended' ? 'Reactivate Educator' : 'Suspend Educator'"
                          @click="confirmToggleTeacher(usr)"
                        />
                        <v-btn
                          size="x-small"
                          icon="mdi-key-change"
                          color="teal"
                          variant="tonal"
                          title="Reset Password"
                          @click="openResetTeacherPass(usr)"
                        />
                      </template>
                      <v-btn size="x-small" icon="mdi-shield-account-outline" color="indigo" variant="tonal" title="Change Role" @click="openChangeRoleModal(usr)" />
                      <v-btn size="x-small" icon="mdi-pencil-outline" color="primary" variant="tonal" title="Edit User" @click="openEditUserModal(usr)" />
                      <v-btn size="x-small" icon="mdi-delete-outline" color="error" variant="tonal" title="Delete User" @click="confirmDeleteUser(usr)" />
                    </div>
                  </td>
                </tr>
                <tr v-if="!filteredUsers.length">
                  <td :colspan="isSuperAdmin ? 7 : 6" class="text-center pa-6 text-caption text-grey">
                    No users found matching current filters.
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-window-item>

          <!-- TAB 4: Homework & Submissions (Shared) -->
          <v-window-item value="assignments">
            <div class="d-flex align-center justify-space-between mb-3 flex-wrap ga-2">
              <div>
                <span class="text-subtitle-2 font-weight-black text-secondary">ASSIGNMENTS & PROGRESS MONITOR</span>
                <span class="text-caption text-grey ml-2">({{ assignmentsList.length }} assignments assigned)</span>
              </div>
              <v-text-field
                v-model="searchAssignmentText"
                placeholder="Search assignment title..."
                variant="outlined"
                density="compact"
                hide-details
                prepend-inner-icon="mdi-magnify"
                style="max-width: 260px;"
              />
            </div>

            <v-table density="comfortable" hover class="border rounded-lg">
              <thead>
                <tr class="bg-grey-lighten-4">
                  <th class="font-weight-black text-caption text-secondary">ASSIGNMENT TITLE & PROMPT</th>
                  <th class="font-weight-black text-caption text-secondary">CLASSROOM & TEACHER</th>
                  <th class="font-weight-black text-caption text-secondary text-center">DUE DATE</th>
                  <th class="font-weight-black text-caption text-secondary text-center">SUBMISSIONS</th>
                  <th class="font-weight-black text-caption text-secondary text-center">AVG SCORE</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="asg in filteredAssignments" :key="asg.id">
                  <td class="pa-3">
                    <div class="font-weight-black text-body-2">{{ asg.title }}</div>
                    <div class="text-caption text-grey font-italic text-truncate" style="max-width: 320px;">
                      "{{ asg.topic_sentence }}"
                    </div>
                  </td>
                  <td>
                    <div class="font-weight-bold text-caption text-primary">{{ asg.class_name }}</div>
                    <div class="text-caption text-grey">{{ asg.teacher_name }}</div>
                  </td>
                  <td class="text-center text-caption text-grey">
                    {{ asg.due_date || 'Open' }}
                  </td>
                  <td class="text-center font-weight-black text-body-2">
                    <v-chip size="x-small" color="blue-lighten-5" class="text-blue-darken-3 font-weight-black">
                      {{ asg.submission_count }} Submitted
                    </v-chip>
                  </td>
                  <td class="text-center font-weight-black">
                    <v-chip size="x-small" :color="asg.avg_score >= 80 ? 'success' : (asg.avg_score >= 60 ? 'warning' : 'grey')" variant="flat" class="font-weight-black">
                      {{ asg.avg_score > 0 ? `${asg.avg_score}%` : 'N/A' }}
                    </v-chip>
                  </td>
                </tr>
                <tr v-if="!filteredAssignments.length">
                  <td colspan="5" class="text-center pa-6 text-caption text-grey">
                    No homework assignments found.
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-window-item>

          <!-- TAB 5: Storage & Maintenance (Super Admin Only) -->
          <v-window-item v-if="isSuperAdmin" value="cleanup">
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

          <!-- TAB 6: Security & Audit Logs (P0/P3) -->
          <v-window-item value="audit_logs">
            <div class="d-flex align-center justify-space-between mb-3 flex-wrap ga-2">
              <div>
                <span class="text-subtitle-2 font-weight-black text-secondary">IMMUTABLE SYSTEM AUDIT TRAIL</span>
                <span class="text-caption text-grey ml-2">({{ filteredAuditLogs.length }} recorded events)</span>
              </div>
              <div class="d-flex align-center ga-2 flex-wrap">
                <v-text-field
                  v-model="searchAuditText"
                  placeholder="Search operator, details..."
                  variant="outlined"
                  density="compact"
                  hide-details
                  prepend-inner-icon="mdi-magnify"
                  style="min-width: 200px; max-width: 240px;"
                />
                <v-select
                  v-model="selectedAuditAction"
                  :items="auditActionOptions"
                  density="compact"
                  variant="outlined"
                  hide-details
                  style="min-width: 170px; max-width: 210px;"
                />
                <v-btn color="primary" size="small" variant="outlined" class="font-weight-bold text-none" prepend-icon="mdi-refresh" :loading="isFetchingLogs" @click="fetchAuditLogs">
                  Refresh Logs
                </v-btn>
              </div>
            </div>

            <v-table density="comfortable" hover class="border rounded-lg">
              <thead>
                <tr class="bg-grey-lighten-4">
                  <th class="font-weight-black text-caption text-secondary">TIMESTAMP</th>
                  <th class="font-weight-black text-caption text-secondary">ACTION</th>
                  <th class="font-weight-black text-caption text-secondary">OPERATOR</th>
                  <th class="font-weight-black text-caption text-secondary">TARGET</th>
                  <th class="font-weight-black text-caption text-secondary">SCHOOL / TENANT</th>
                  <th class="font-weight-black text-caption text-secondary">DETAILS</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in filteredAuditLogs" :key="log.id">
                  <td class="text-caption font-weight-mono text-grey-darken-1">{{ log.created_at }}</td>
                  <td>
                    <v-chip size="x-small" :color="getAuditActionColor(log.action)" variant="flat" class="font-weight-black">
                      {{ log.action }}
                    </v-chip>
                  </td>
                  <td class="text-body-2 font-weight-bold">{{ log.user_name }} ({{ log.user_email }})</td>
                  <td class="text-caption font-weight-mono">{{ log.target_type }}: #{{ log.target_id }}</td>
                  <td class="text-caption font-weight-bold text-primary">{{ log.tenant_id ? `School ${log.tenant_id}` : 'Global' }}</td>
                  <td class="text-caption text-grey-darken-2">{{ log.details || '—' }}</td>
                </tr>
                <tr v-if="!filteredAuditLogs.length">
                  <td colspan="6" class="text-center pa-6 text-caption text-grey">
                    No security audit logs found matching criteria.
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-window-item>
        </v-window>
      </v-card>

      <!-- MODALS SECTION -->
      <!-- Modal: Provision Account -->
      <v-dialog v-model="showProvisionModal" max-width="500">
        <v-card border rounded="lg" class="pa-4">
          <div class="text-subtitle-1 font-weight-black text-primary mb-3">Provision Educator or Admin Account</div>
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
            :items="provisionRoleOptions"
            item-title="title"
            item-value="value"
            label="Permission Level (Role):"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />

          <!-- If Super Admin provisioning a Teacher: choose Institutional vs Freelance -->
          <v-select
            v-if="isSuperAdmin && newProvRole === 'teacher'"
            v-model="newProvTeacherType"
            :items="[
              { title: '🎓 Independent Educator (Freelance / Solo Tutor)', value: 'freelance' },
              { title: '🏫 Institutional Educator (Affiliated with School)', value: 'institutional' }
            ]"
            item-title="title"
            item-value="value"
            label="Educator Licensing Model:"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />

          <!-- If Institutional Teacher or other roles (Admin/Student): choose School -->
          <v-select
            v-if="isSuperAdmin && (newProvRole !== 'teacher' || newProvTeacherType === 'institutional')"
            v-model="newProvTenantId"
            :items="tenantSelectOptions"
            item-title="title"
            item-value="value"
            label="Assign to School Organization:"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />

          <!-- If Freelance Teacher: show Quotas -->
          <template v-if="isSuperAdmin && newProvRole === 'teacher' && newProvTeacherType === 'freelance'">
            <v-row density="compact">
              <v-col cols="6">
                <v-text-field
                  v-model.number="newProvMaxSeats"
                  label="Student Seats Limit:"
                  type="number"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-seat-passenger"
                  min="1"
                  class="mb-2"
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model.number="newProvMaxClasses"
                  label="Max Classrooms:"
                  type="number"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-google-classroom"
                  min="1"
                  class="mb-2"
                />
              </v-col>
            </v-row>
            <v-text-field
              v-model="newProvPlanExpiry"
              label="Plan Expiration Date (YYYY-MM-DD):"
              placeholder="2028-12-31"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-calendar"
              class="mb-2"
            />
          </template>

          <v-text-field
            v-model="newProvPassword"
            label="Default Password:"
            placeholder="password123"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showProvisionModal = false">Cancel</v-btn>
            <v-btn color="primary" variant="flat" class="text-none font-weight-bold" :loading="isProvisioning" @click="submitProvisioning">Provision Account</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Change User Role -->
      <v-dialog v-model="showChangeRoleModal" max-width="420">
        <v-card border rounded="lg" class="pa-4">
          <div class="text-subtitle-1 font-weight-black text-primary mb-2">Change User Permission Role</div>
          <div class="text-body-2 text-grey-darken-2 mb-3">
            Change role for <strong>{{ userToChangeRole?.name }}</strong> ({{ userToChangeRole?.email }}):
          </div>
          <v-select
            v-model="selectedNewRole"
            :items="allowedRoleChangeOptions"
            item-title="title"
            item-value="value"
            label="Select New Role:"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showChangeRoleModal = false">Cancel</v-btn>
            <v-btn color="primary" variant="flat" class="text-none font-weight-bold" :loading="isUpdatingRole" @click="submitChangeRole">Apply Role</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Delete Classroom Confirmation -->
      <v-dialog v-model="showDeleteClassModal" max-width="400">
        <v-card border rounded="lg" class="pa-4">
          <div class="text-subtitle-1 font-weight-black text-error mb-2 d-flex align-center ga-2">
            <v-icon color="error">mdi-delete-alert</v-icon>
            <span>Confirm Delete Classroom</span>
          </div>
          <div class="text-body-2 text-grey-darken-2 mb-4">
            Are you sure you want to delete classroom <strong>"{{ classToDelete?.name }}"</strong>?
          </div>
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showDeleteClassModal = false">Cancel</v-btn>
            <v-btn color="error" variant="flat" class="text-none font-weight-bold" :loading="isDeletingClass" @click="submitDeleteClassroom">Delete Classroom</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Atomic School Onboarding (Super Admin Only) -->
      <v-dialog v-model="showOnboardModal" max-width="500">
        <v-card border rounded="lg" class="pa-4">
          <div class="d-flex align-center ga-2 mb-2">
            <v-icon color="primary">mdi-school</v-icon>
            <span class="text-subtitle-1 font-weight-black text-primary">Onboard B2B School Organization</span>
          </div>
          <div class="text-caption text-grey-darken-1 mb-3">
            Creates school tenant and provisions initial School Administrator account atomically.
          </div>
          <v-text-field
            v-model="onboardSchoolName"
            label="School Organization Name:"
            placeholder="e.g. Olympia International Academy"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />
          <v-row density="compact">
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="onboardAdminName"
                label="Administrator Full Name:"
                placeholder="Dr. Vance Olympia"
                variant="outlined"
                density="comfortable"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="onboardAdminEmail"
                label="Administrator Email:"
                placeholder="admin@olympia.edu.vn"
                variant="outlined"
                density="comfortable"
              />
            </v-col>
          </v-row>
          <v-text-field
            v-model="onboardAdminPassword"
            label="Initial Admin Password:"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />
          <v-row density="compact">
            <v-col cols="12" sm="6">
              <v-text-field
                v-model.number="onboardSeats"
                label="Seat Licenses Quota:"
                type="number"
                variant="outlined"
                density="comfortable"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="onboardExpiry"
                label="License Expiry Date:"
                placeholder="2028-12-31"
                variant="outlined"
                density="comfortable"
              />
            </v-col>
          </v-row>
          <v-select
            v-model="onboardStatus"
            :items="[
              { title: 'Active (Production)', value: 'active' },
              { title: 'Trial (Evaluation)', value: 'trial' }
            ]"
            label="Initial Organization Status:"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showOnboardModal = false">Cancel</v-btn>
            <v-btn color="primary" variant="flat" class="text-none font-weight-bold" :loading="isOnboarding" @click="submitOnboardTenant">Onboard Organization</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Manage Tenant Lifecycle, Quota & Admin (Super Admin Only) -->
      <v-dialog v-model="showLifecycleModal" max-width="560">
        <v-card border rounded="lg" class="pa-4">
          <div class="d-flex align-center ga-2 mb-1">
            <v-icon color="primary">mdi-tune</v-icon>
            <span class="text-subtitle-1 font-weight-black text-primary">Manage School, Quota & Administrator</span>
          </div>
          <div class="text-caption font-weight-bold text-secondary mb-3">
            Organization ID: <span class="font-weight-mono text-primary">{{ tenantForLifecycle?.id }}</span>
          </div>

          <v-alert
            v-if="!tenantForLifecycle?.admin_email"
            type="warning"
            density="compact"
            variant="tonal"
            class="mb-3 text-caption"
            icon="mdi-account-alert-outline"
          >
            No school administrator is currently linked to this organization. Enter an email and name below to provision or link one.
          </v-alert>

          <!-- Section: School Profile -->
          <div class="text-caption font-weight-bold text-grey-darken-2 mb-1">School Profile</div>
          <v-row density="compact">
            <v-col cols="12" sm="7">
              <v-text-field
                v-model="lifecycleSchoolName"
                label="School Organization Name:"
                variant="outlined"
                density="comfortable"
                hide-details="auto"
                class="mb-2"
              />
            </v-col>
            <v-col cols="12" sm="5">
              <v-select
                v-model="lifecycleStatus"
                :items="[
                  { title: 'ACTIVE (Operational)', value: 'active' },
                  { title: 'TRIAL (Evaluation)', value: 'trial' },
                  { title: 'SUSPENDED (Locked)', value: 'suspended' },
                  { title: 'EXPIRED (Ended)', value: 'expired' }
                ]"
                label="Lifecycle State:"
                variant="outlined"
                density="comfortable"
                hide-details="auto"
                class="mb-2"
              />
            </v-col>
          </v-row>

          <!-- Section: Administrator Account -->
          <div class="text-caption font-weight-bold text-grey-darken-2 mt-2 mb-1">School Administrator Account</div>
          <v-row density="compact">
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="lifecycleAdminEmail"
                label="Administrator Email:"
                placeholder="admin@school.edu.vn"
                variant="outlined"
                density="comfortable"
                hide-details="auto"
                class="mb-2"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="lifecycleAdminName"
                label="Administrator Full Name:"
                placeholder="Principal / Academic Dean"
                variant="outlined"
                density="comfortable"
                hide-details="auto"
                class="mb-2"
              />
            </v-col>
          </v-row>
          <v-text-field
            v-model="lifecycleAdminPassword"
            label="Reset Password (Optional):"
            placeholder="Leave blank to keep existing password"
            type="password"
            variant="outlined"
            density="comfortable"
            hide-details="auto"
            class="mb-2"
          />

          <!-- Section: Quotas & Capacity -->
          <div class="text-caption font-weight-bold text-grey-darken-2 mt-2 mb-1">License & Capacity Quota</div>
          <v-row density="compact">
            <v-col cols="12" sm="6">
              <v-text-field
                v-model.number="lifecycleSeats"
                label="Purchased Seat Licenses:"
                type="number"
                variant="outlined"
                density="comfortable"
                hide-details="auto"
                class="mb-3"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="lifecycleExpiry"
                label="License Expiry Date:"
                placeholder="2028-12-31"
                variant="outlined"
                density="comfortable"
                hide-details="auto"
                class="mb-3"
              />
            </v-col>
          </v-row>

          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showLifecycleModal = false">Cancel</v-btn>
            <v-btn color="primary" variant="flat" class="text-none font-weight-bold" :loading="isUpdatingLifecycle" @click="submitLifecycle">Save Changes</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Support Mode / Inspect Confirmation (Super Admin Only) -->
      <v-dialog v-model="showInspectSchoolModal" max-width="440">
        <v-card border rounded="lg" class="pa-4">
          <div class="d-flex align-center ga-2 mb-2">
            <v-icon color="amber-darken-3">mdi-shield-account</v-icon>
            <span class="text-subtitle-1 font-weight-black text-amber-darken-4">Inspect School (Support Mode)</span>
          </div>
          <div class="text-body-2 text-grey-darken-2 mb-3">
            Enter Support & Inspection mode for <strong>{{ tenantToInspect?.name }}</strong>?
          </div>
          <div class="text-caption text-grey-darken-1 pa-3 bg-grey-lighten-4 rounded mb-4">
            You will inspect this school with the scoped privileges of its administrator ({{ tenantToInspect?.admin_email || 'Assigned Admin' }}). An exit button will remain available to return to Super Admin governance anytime.
          </div>
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showInspectSchoolModal = false">Cancel</v-btn>
            <v-btn color="amber-darken-4" variant="flat" class="text-none font-weight-bold text-white" :loading="isEnteringSupportMode" @click="submitEnterSupportMode">Enter Support Mode</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Create New Tenant (Super Admin Only) -->
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
            v-model.number="newTenantSeats"
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

      <!-- Modal: Edit Tenant (Super Admin Only) -->
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

      <!-- Modal: Delete Tenant Confirmation (Super Admin Only) -->
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
          <div class="text-subtitle-1 font-weight-black text-primary mb-3">Edit User Account</div>
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
          <v-text-field
            v-model="editUserPass"
            label="Reset Password (leave empty to keep current):"
            placeholder="••••••••"
            type="password"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showEditUserModal = false">Cancel</v-btn>
            <v-btn color="primary" variant="flat" class="text-none font-weight-bold" :loading="isUpdatingUser" @click="submitEditUser">Save Changes</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Delete User Confirmation -->
      <v-dialog v-model="showDeleteUserModal" max-width="400">
        <v-card border rounded="lg" class="pa-4">
          <div class="text-subtitle-1 font-weight-black text-error mb-2">Delete User Account</div>
          <div class="text-body-2 text-grey-darken-2 mb-4">
            Are you sure you want to delete account <strong>{{ userToDelete?.name }}</strong> ({{ userToDelete?.email }})?
          </div>
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showDeleteUserModal = false">Cancel</v-btn>
            <v-btn color="error" variant="flat" class="text-none font-weight-bold" :loading="isDeletingUser" @click="submitDeleteUser">Delete User</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Admin Sign Out Confirmation -->
      <v-dialog v-model="showLogoutDialog" max-width="400">
        <v-card border rounded="lg" class="pa-4 bg-white">
          <div class="d-flex align-center ga-3 mb-3">
            <v-avatar color="red-lighten-5" size="40" class="text-error border">
              <v-icon size="default">mdi-logout-variant</v-icon>
            </v-avatar>
            <div>
              <div class="text-subtitle-1 font-weight-black text-secondary">Confirm Sign Out</div>
              <div class="text-caption text-grey-darken-1">Are you sure you want to sign out from Administration Console?</div>
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
      <!-- Modal: Create New Classroom (P1) -->
      <v-dialog v-model="showCreateClassModal" max-width="480">
        <v-card border rounded="lg" class="pa-4 bg-white">
          <div class="text-subtitle-1 font-weight-black text-primary mb-3 d-flex align-center ga-2">
            <v-icon color="primary">mdi-plus-box</v-icon>
            <span>Create New Classroom</span>
          </div>
          <v-text-field
            v-model="newClassName"
            label="Classroom Name:"
            placeholder="e.g. English Grade 10 - Honors"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />
          <v-text-field
            v-model="newClassGrade"
            label="Grade Level / Proficiency:"
            placeholder="e.g. Grade 10 or Intermediate B1"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />
          <v-select
            v-model="newClassTeacherId"
            :items="availableTeachers"
            item-title="title"
            item-value="value"
            label="Assign Teacher in Charge:"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showCreateClassModal = false">Cancel</v-btn>
            <v-btn color="primary" variant="flat" class="text-none font-weight-bold" :loading="isCreatingClass" @click="submitCreateClass">Create Class</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Reassign Classroom Teacher (P1) -->
      <v-dialog v-model="showAssignTeacherModal" max-width="440">
        <v-card border rounded="lg" class="pa-4 bg-white">
          <div class="text-subtitle-1 font-weight-black text-primary mb-2 d-flex align-center ga-2">
            <v-icon color="primary">mdi-account-switch</v-icon>
            <span>Reassign Class Teacher</span>
          </div>
          <div class="text-body-2 text-grey-darken-2 mb-3">
            Reassigning classroom <strong>"{{ classToAssignTeacher?.name }}"</strong>:
          </div>
          <v-select
            v-model="selectedNewTeacherId"
            :items="availableTeachers"
            item-title="title"
            item-value="value"
            label="Select Educator:"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showAssignTeacherModal = false">Cancel</v-btn>
            <v-btn color="primary" variant="flat" class="text-none font-weight-bold" :loading="isAssigningTeacher" @click="submitAssignTeacher">Reassign</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Archive / Unarchive Classroom (P1) -->
      <v-dialog v-model="showArchiveClassModal" max-width="420">
        <v-card border rounded="lg" class="pa-4 bg-white">
          <div class="text-subtitle-1 font-weight-black text-secondary mb-2 d-flex align-center ga-2">
            <v-icon :color="classToToggleArchive?.is_archived ? 'success' : 'amber-darken-3'">
              {{ classToToggleArchive?.is_archived ? 'mdi-archive-arrow-up' : 'mdi-archive-arrow-down' }}
            </v-icon>
            <span>{{ classToToggleArchive?.is_archived ? 'Confirm Restore Classroom' : 'Confirm Archive Classroom' }}</span>
          </div>
          <div class="text-body-2 text-grey-darken-2 mb-4">
            Are you sure you want to {{ classToToggleArchive?.is_archived ? 'restore' : 'archive' }} classroom
            <strong>"{{ classToToggleArchive?.name }}"</strong>?
            <span v-if="!classToToggleArchive?.is_archived" class="d-block mt-1 text-caption text-grey">
              Archived classes will stop accepting new student enrollments while preserving all gradebook history.
            </span>
          </div>
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showArchiveClassModal = false">Cancel</v-btn>
            <v-btn :color="classToToggleArchive?.is_archived ? 'success' : 'amber-darken-3'" variant="flat" class="text-none font-weight-bold" :loading="isArchivingClass" @click="submitToggleArchive">
              {{ classToToggleArchive?.is_archived ? 'Restore to Active' : 'Archive Class' }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Class Roster Directory (P1) -->
      <v-dialog v-model="showClassRosterModal" max-width="760">
        <v-card border rounded="lg" class="pa-4 bg-white">
          <div class="d-flex align-center justify-space-between mb-3 flex-wrap ga-2">
            <div class="d-flex align-center ga-2">
              <v-avatar color="indigo-lighten-5" size="36">
                <v-icon color="indigo">mdi-account-group</v-icon>
              </v-avatar>
              <div>
                <div class="text-subtitle-1 font-weight-black text-secondary">
                  {{ activeRosterClass?.name }}
                </div>
                <div class="text-caption text-grey">
                  Code: <strong class="font-weight-mono text-primary">{{ activeRosterClass?.join_code }}</strong> &bull;
                  Grade: {{ activeRosterClass?.grade_level }} &bull;
                  {{ classRosterStudents.length }} Enrolled Students
                </div>
              </div>
            </div>
            <v-btn variant="text" density="compact" icon="mdi-close" @click="showClassRosterModal = false" />
          </div>

          <v-table density="comfortable" hover class="border rounded-lg mb-3">
            <thead>
              <tr class="bg-grey-lighten-4">
                <th class="font-weight-black text-caption text-secondary">STUDENT</th>
                <th class="font-weight-black text-caption text-secondary text-center">JOINED</th>
                <th class="font-weight-black text-caption text-secondary text-center">SUBMISSIONS</th>
                <th class="font-weight-black text-caption text-secondary text-center">AVG SCORE</th>
                <th class="font-weight-black text-caption text-secondary text-center">ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="stu in classRosterStudents" :key="stu.id">
                <td class="pa-2">
                  <div class="d-flex align-center ga-2">
                    <v-avatar size="30" color="indigo-lighten-5">
                      <img v-if="stu.avatar" :src="stu.avatar" alt="Avatar" />
                      <span v-else class="text-caption font-weight-bold text-primary">{{ stu.name?.slice(0, 1)?.toUpperCase() || 'S' }}</span>
                    </v-avatar>
                    <div>
                      <div class="font-weight-bold text-body-2">{{ stu.name }}</div>
                      <div class="text-caption text-grey">{{ stu.email }}</div>
                    </div>
                  </div>
                </td>
                <td class="text-center text-caption font-weight-mono text-grey-darken-1">{{ stu.joined_at?.slice(0, 10) || '—' }}</td>
                <td class="text-center font-weight-bold text-caption">{{ stu.submission_count || 0 }}</td>
                <td class="text-center">
                  <v-chip v-if="stu.avg_score !== null && stu.avg_score !== undefined" size="x-small" color="success" variant="flat" class="font-weight-black">
                    {{ stu.avg_score }}%
                  </v-chip>
                  <span v-else class="text-caption text-grey">—</span>
                </td>
                <td class="text-center">
                  <div class="d-flex align-center justify-center ga-1">
                    <v-btn
                      size="x-small"
                      icon="mdi-swap-horizontal"
                      color="primary"
                      variant="tonal"
                      title="Transfer to Another Class"
                      @click="openTransferStudentModal(stu)"
                    />
                    <v-btn
                      size="x-small"
                      icon="mdi-account-remove"
                      color="error"
                      variant="tonal"
                      title="Revoke Student Seat"
                      @click="confirmRevokeStudent(stu)"
                    />
                  </div>
                </td>
              </tr>
              <tr v-if="!classRosterStudents.length">
                <td colspan="5" class="text-center pa-6 text-caption text-grey">
                  No students currently enrolled in this classroom.
                </td>
              </tr>
            </tbody>
          </v-table>

          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showClassRosterModal = false">Close</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Transfer Student (P1) -->
      <v-dialog v-model="showTransferStudentModal" max-width="440">
        <v-card border rounded="lg" class="pa-4 bg-white">
          <div class="text-subtitle-1 font-weight-black text-primary mb-2 d-flex align-center ga-2">
            <v-icon color="primary">mdi-swap-horizontal</v-icon>
            <span>Transfer Student</span>
          </div>
          <div class="text-body-2 text-grey-darken-2 mb-3">
            Transfer <strong>{{ studentToTransfer?.name }}</strong> from <em>{{ activeRosterClass?.name }}</em> to:
          </div>
          <v-select
            v-model="targetTransferClassId"
            :items="availableTransferClasses"
            item-title="title"
            item-value="value"
            label="Destination Classroom:"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showTransferStudentModal = false">Cancel</v-btn>
            <v-btn color="primary" variant="flat" class="text-none font-weight-bold" :loading="isTransferringStudent" @click="submitTransferStudent">Confirm Transfer</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Revoke Student Seat Confirmation (P1) -->
      <v-dialog v-model="showRevokeStudentModal" max-width="420">
        <v-card border rounded="lg" class="pa-4 bg-white">
          <div class="text-subtitle-1 font-weight-black text-error mb-2 d-flex align-center ga-2">
            <v-icon color="error">mdi-account-remove</v-icon>
            <span>Confirm Revoke Student Seat</span>
          </div>
          <div class="text-body-2 text-grey-darken-2 mb-3">
            Are you sure you want to remove <strong>{{ studentToRevoke?.name }}</strong> from <em>{{ activeRosterClass?.name }}</em>?
          </div>
          <div class="text-caption text-grey-darken-1 mb-4 bg-grey-lighten-4 pa-2 rounded">
            This will un-enroll the student and return 1 seat back to your school's license quota pool.
          </div>
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showRevokeStudentModal = false">Cancel</v-btn>
            <v-btn color="error" variant="flat" class="text-none font-weight-bold" :loading="isRevokingStudent" @click="submitRevokeStudent">Revoke Seat</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Toggle Teacher Status Confirmation (P1) -->
      <v-dialog v-model="showToggleTeacherModal" max-width="420">
        <v-card border rounded="lg" class="pa-4 bg-white">
          <div class="text-subtitle-1 font-weight-black text-secondary mb-2 d-flex align-center ga-2">
            <v-icon :color="teacherToToggle?.status === 'suspended' ? 'success' : 'warning'">
              {{ teacherToToggle?.status === 'suspended' ? 'mdi-account-check' : 'mdi-account-lock' }}
            </v-icon>
            <span>{{ teacherToToggle?.status === 'suspended' ? 'Reactivate Educator Account' : 'Suspend Educator Account' }}</span>
          </div>
          <div class="text-body-2 text-grey-darken-2 mb-3">
            Are you sure you want to {{ teacherToToggle?.status === 'suspended' ? 'reactivate' : 'suspend' }} account for
            <strong>{{ teacherToToggle?.name }}</strong> ({{ teacherToToggle?.email }})?
          </div>
          <div v-if="teacherToToggle?.status !== 'suspended'" class="text-caption text-warning mb-4 bg-amber-lighten-5 pa-2 rounded border border-warning">
            Suspended educators will immediately lose access to their classes and administrative dashboards.
          </div>
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showToggleTeacherModal = false">Cancel</v-btn>
            <v-btn :color="teacherToToggle?.status === 'suspended' ? 'success' : 'warning'" variant="flat" class="text-none font-weight-bold" :loading="isTogglingTeacher" @click="submitToggleTeacherStatus">
              {{ teacherToToggle?.status === 'suspended' ? 'Reactivate' : 'Suspend Educator' }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Reset Teacher Password (P1) -->
      <v-dialog v-model="showResetTeacherPassModal" max-width="440">
        <v-card border rounded="lg" class="pa-4 bg-white">
          <div class="text-subtitle-1 font-weight-black text-teal-darken-3 mb-2 d-flex align-center ga-2">
            <v-icon color="teal">mdi-key-change</v-icon>
            <span>Reset Educator Password</span>
          </div>
          <div class="text-body-2 text-grey-darken-2 mb-3">
            Reset password for <strong>{{ teacherToResetPass?.name }}</strong> ({{ teacherToResetPass?.email }}):
          </div>
          <v-text-field
            v-model="newTeacherPasswordInput"
            label="New Password (min 6 characters):"
            placeholder="Enter new password"
            type="password"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showResetTeacherPassModal = false">Cancel</v-btn>
            <v-btn color="teal" variant="flat" class="text-none font-weight-bold" :loading="isResettingTeacherPass" @click="submitResetTeacherPassword">Save New Password</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Modal: Configure Educator Plan & Quotas (Super Admin Only) -->
      <v-dialog v-model="showConfigurePlanModal" max-width="480">
        <v-card border rounded="lg" class="pa-4 bg-white">
          <div class="text-subtitle-1 font-weight-black text-indigo-darken-3 mb-2 d-flex align-center ga-2">
            <v-icon color="indigo">mdi-license</v-icon>
            <span>Configure Educator Plan & Quotas</span>
          </div>
          <div class="text-caption text-grey-darken-1 mb-3">
            Manage licensing model and capacity limits for <strong>{{ teacherToConfigurePlan?.name }}</strong> ({{ teacherToConfigurePlan?.email }}).
          </div>

          <v-select
            v-model="editTeacherType"
            :items="[
              { title: '🏫 Institutional (School Managed)', value: 'institutional' },
              { title: '🎓 Freelance / Independent (Self-Managed)', value: 'freelance' }
            ]"
            item-title="title"
            item-value="value"
            label="Educator Licensing Model:"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />

          <template v-if="editTeacherType === 'freelance'">
            <v-row density="compact">
              <v-col cols="6">
                <v-text-field
                  v-model.number="editMaxSeats"
                  label="Student Seats Limit:"
                  type="number"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-seat-passenger"
                  min="1"
                  class="mb-2"
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model.number="editMaxClasses"
                  label="Max Classrooms:"
                  type="number"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-google-classroom"
                  min="1"
                  class="mb-2"
                />
              </v-col>
            </v-row>

            <v-text-field
              v-model="editPlanExpiry"
              label="Plan Expiration Date (YYYY-MM-DD):"
              placeholder="2028-12-31"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-calendar"
              class="mb-2"
            />
          </template>

          <v-alert v-else type="info" variant="tonal" density="compact" class="text-caption mb-3">
            Institutional teachers share their school's student seat license pool and classroom capacity.
          </v-alert>

          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showConfigurePlanModal = false">
              Cancel
            </v-btn>
            <v-btn
              color="indigo-darken-3"
              variant="flat"
              class="text-none font-weight-bold"
              :loading="isSavingPlan"
              @click="submitSaveTeacherPlan"
            >
              Save Educator Plan
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Confirm Clean Demo Data for Production Launch Modal (Mandatory Confirmation) -->
      <v-dialog v-model="showConfirmCleanProductionModal" max-width="500">
        <v-card class="pa-6 rounded-lg elevation-4">
          <div class="d-flex align-center ga-3 mb-3">
            <v-avatar color="error" size="44">
              <v-icon color="white">mdi-alert-octagon</v-icon>
            </v-avatar>
            <div>
              <div class="text-subtitle-1 font-weight-black text-error">CLEAN DEMO DATA FOR PRODUCTION</div>
              <div class="text-caption text-grey">Disaster Prevention & Live Readiness</div>
            </div>
          </div>
          <v-alert type="warning" variant="tonal" density="compact" class="mb-4 text-caption font-weight-medium">
            <strong>Warning:</strong> This action will permanently remove all test classrooms, test assignments, test submissions, practice history, and test students.
            <div class="mt-1">
              <strong>Preserved:</strong> Super Admin, School Admins, Teacher accounts, and system configurations will remain 100% intact.
            </div>
          </v-alert>
          <div class="text-caption text-grey-darken-1 mb-4">
            Before proceeding, an automatic snapshot backup will be created and downloaded to ensure you can restore previous data if needed.
          </div>
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showConfirmCleanProductionModal = false">
              Cancel
            </v-btn>
            <v-btn
              color="error"
              variant="flat"
              class="text-none font-weight-bold"
              :loading="isCleaningProduction"
              @click="submitCleanProductionReset"
            >
              Confirm Clean Production Launch
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Confirm Restore Snapshot Modal (Mandatory Confirmation) -->
      <v-dialog v-model="showConfirmRestoreModal" max-width="480">
        <v-card class="pa-6 rounded-lg elevation-4">
          <div class="d-flex align-center ga-3 mb-3">
            <v-avatar color="teal" size="44">
              <v-icon color="white">mdi-database-import</v-icon>
            </v-avatar>
            <div>
              <div class="text-subtitle-1 font-weight-black text-teal-darken-3">CONFIRM SNAPSHOT RESTORE</div>
              <div class="text-caption text-grey">File: {{ selectedSnapshotFile?.name }}</div>
            </div>
          </div>
          <v-alert type="info" variant="tonal" density="compact" class="mb-4 text-caption font-weight-medium">
            Current database tables will be synchronized and restored to the exact state saved in this snapshot file.
          </v-alert>
          <v-card-actions class="px-0 pb-0">
            <v-spacer />
            <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showConfirmRestoreModal = false">
              Cancel
            </v-btn>
            <v-btn
              color="teal-darken-2"
              variant="flat"
              class="text-none font-weight-bold text-white"
              :loading="isRestoringSnapshot"
              @click="submitRestoreSnapshot"
            >
              Start Database Restore
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </v-container>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  backendUrl: String,
  userRole: String
})

const router = useRouter()

// Authentication & Identity
const activeUserRole = ref(props.userRole || localStorage.getItem('user_role') || 'student')
const userTenantId = ref(localStorage.getItem('user_tenant_id') || (activeUserRole.value === 'admin' ? '1' : ''))
const isSuperAdmin = computed(() => activeUserRole.value === 'super_admin')

watch(() => props.userRole, (newRole) => {
  if (newRole) {
    activeUserRole.value = newRole
    if (['admin', 'super_admin'].includes(newRole)) {
      fetchAllAdminData()
    }
  }
})

const loginEmail = ref('')
const loginPassword = ref('')
const isLoggingIn = ref(false)
const loginError = ref('')

const toast = ref({ show: false, text: '', color: 'success', icon: 'mdi-check-circle' })
const notify = (text, color = 'success', icon = 'mdi-check-circle') => {
  toast.value = { show: true, text, color, icon }
}

// Navigation & Tabs
const activeTab = ref(isSuperAdmin.value ? 'tenants' : 'classrooms')
const selectedTenantScope = ref(isSuperAdmin.value ? 'all' : (userTenantId.value || '1'))

// State Data
const overview = ref({
  total_tenants: 0,
  total_teachers: 0,
  total_students: 0,
  total_classrooms: 0,
  total_assignments: 0,
  total_submissions: 0,
  license_seats: 100,
  used_seats: 0,
  current_tenant: null,
  tenants: []
})
const classroomsList = ref([])
const usersList = ref([])
const assignmentsList = ref([])
const auditLogsList = ref([])
const isFetchingLogs = ref(false)

// Search & Filters
const searchClassText = ref('')
const searchUserText = ref('')
const searchAssignmentText = ref('')
const selectedUserRoleFilter = ref('all')
const activeClassFilter = ref('all')

// P1 Modals State
const showCreateClassModal = ref(false)
const newClassName = ref('')
const newClassGrade = ref('')
const newClassTeacherId = ref(null)
const isCreatingClass = ref(false)

const showAssignTeacherModal = ref(false)
const classToAssignTeacher = ref(null)
const selectedNewTeacherId = ref(null)
const isAssigningTeacher = ref(false)

const showArchiveClassModal = ref(false)
const classToToggleArchive = ref(null)
const isArchivingClass = ref(false)

const showClassRosterModal = ref(false)
const activeRosterClass = ref(null)
const classRosterStudents = ref([])
const isFetchingRoster = ref(false)

const showTransferStudentModal = ref(false)
const studentToTransfer = ref(null)
const targetTransferClassId = ref(null)
const isTransferringStudent = ref(false)

const showRevokeStudentModal = ref(false)
const studentToRevoke = ref(null)
const isRevokingStudent = ref(false)

const showToggleTeacherModal = ref(false)
const teacherToToggle = ref(null)
const isTogglingTeacher = ref(false)

const showResetTeacherPassModal = ref(false)
const teacherToResetPass = ref(null)
const newTeacherPasswordInput = ref('')
const isResettingTeacherPass = ref(false)

// Modals State
const showLogoutDialog = ref(false)
const showCreateTenantModal = ref(false)
const showEditTenantModal = ref(false)
const showDeleteTenantModal = ref(false)
const showProvisionModal = ref(false)
const showEditUserModal = ref(false)
const showDeleteUserModal = ref(false)
const showChangeRoleModal = ref(false)
const showDeleteClassModal = ref(false)

// Forms State
const newTenantName = ref('')
const newTenantSeats = ref(100)
const editTenantId = ref(null)
const editTenantName = ref('')
const editTenantSeats = ref(100)
const editTenantExpiry = ref('')
const tenantToDelete = ref(null)

const newProvEmail = ref('')
const newProvName = ref('')
const newProvRole = ref('teacher')
const newProvTeacherType = ref('freelance')
const newProvMaxSeats = ref(30)
const newProvMaxClasses = ref(3)
const newProvPlanExpiry = ref('2028-12-31')
const newProvPassword = ref('password123')
const newProvTenantId = ref('1')
const isProvisioning = ref(false)

const editUserId = ref(null)
const editUserEmail = ref('')
const editUserName = ref('')
const editUserPass = ref('')
const isUpdatingUser = ref(false)
const userToDelete = ref(null)
const isDeletingUser = ref(false)

const userToChangeRole = ref(null)
const selectedNewRole = ref('teacher')
const isUpdatingRole = ref(false)

const classToDelete = ref(null)
const isDeletingClass = ref(false)

const retentionDaysInput = ref(60)
const isSavingSettings = ref(false)
const isUpdatingTenant = ref(false)
const isDeletingTenant = ref(false)

// P3 Super Admin Governance States
const tenantsList = ref([])
const isFetchingTenants = ref(false)

// Support / Inspection Mode
const isSupportMode = ref(false)
const supportSchoolName = ref('')
const supportAdminEmail = ref('')
const tenantToInspect = ref(null)
const showInspectSchoolModal = ref(false)
const isEnteringSupportMode = ref(false)

// Onboard School Modal State
const showOnboardModal = ref(false)
const onboardSchoolName = ref('')
const onboardAdminName = ref('')
const onboardAdminEmail = ref('')
const onboardAdminPassword = ref('Admin@12345')
const onboardSeats = ref(100)
const onboardExpiry = ref('2028-12-31')
const onboardStatus = ref('active')
const isOnboarding = ref(false)

// Lifecycle & School Configuration Modal State
const showLifecycleModal = ref(false)
const tenantForLifecycle = ref(null)
const lifecycleSchoolName = ref('')
const lifecycleAdminEmail = ref('')
const lifecycleAdminName = ref('')
const lifecycleAdminPassword = ref('')
const lifecycleStatus = ref('active')
const lifecycleSeats = ref(100)
const lifecycleExpiry = ref('2028-12-31')
const isUpdatingLifecycle = ref(false)

// Snapshot Export State
const isExportingSnapshot = ref(false)

// Audit Log Search & Action Filters
const searchAuditText = ref('')
const selectedAuditAction = ref('ALL')
const auditActionOptions = [
  'ALL', 'LOGIN', 'ONBOARD_TENANT', 'UPDATE_TENANT_LIFECYCLE', 'CREATE_CLASSROOM',
  'ASSIGN_TEACHER', 'ARCHIVE_CLASS', 'RESTORE_CLASS', 'TRANSFER_STUDENT',
  'REVOKE_SEAT', 'PROVISION_ACCOUNT', 'CHANGE_ROLE', 'UPDATE_USER', 'DELETE_USER',
  'IMPERSONATE_TENANT', 'UPDATE_SETTINGS'
]

// Computed Filters
const availableTeachers = computed(() => {
  return usersList.value
    .filter(u => u.role === 'teacher' && u.status !== 'suspended')
    .map(u => ({ title: `${u.name} (${u.email})`, value: u.id }))
})

const availableTransferClasses = computed(() => {
  if (!activeRosterClass.value) return []
  return classroomsList.value
    .filter(c => c.id !== activeRosterClass.value.id && !c.is_archived)
    .map(c => ({ title: `${c.name} (${c.grade_level})`, value: c.id }))
})

const tenantScopeOptions = computed(() => {
  const opts = [{ title: 'All Schools (Global)', value: 'all' }]
  overview.value.tenants?.forEach(t => {
    opts.push({ title: t.name, value: String(t.id) })
  })
  return opts
})

const tenantSelectOptions = computed(() => {
  return (overview.value.tenants || []).map(t => ({ title: t.name, value: String(t.id) }))
})

const provisionRoleOptions = computed(() => {
  if (isSuperAdmin.value) {
    return [
      { title: 'Educator / Teacher', value: 'teacher' },
      { title: 'School Administrator', value: 'admin' },
      { title: 'Student', value: 'student' }
    ]
  }
  return [
    { title: 'Educator / Teacher', value: 'teacher' },
    { title: 'Student', value: 'student' }
  ]
})

const allowedRoleChangeOptions = computed(() => {
  if (isSuperAdmin.value) {
    return [
      { title: 'Student', value: 'student' },
      { title: 'Educator / Teacher', value: 'teacher' },
      { title: 'School Administrator', value: 'admin' }
    ]
  }
  return [
    { title: 'Student', value: 'student' },
    { title: 'Educator / Teacher', value: 'teacher' }
  ]
})

const filteredClassrooms = computed(() => {
  let list = classroomsList.value
  if (activeClassFilter.value === 'active') {
    list = list.filter(c => !c.is_archived)
  } else if (activeClassFilter.value === 'archived') {
    list = list.filter(c => c.is_archived)
  }
  const q = searchClassText.value.toLowerCase().trim()
  if (!q) return list
  return list.filter(c =>
    c.name?.toLowerCase().includes(q) ||
    c.teacher_name?.toLowerCase().includes(q) ||
    c.join_code?.toLowerCase().includes(q)
  )
})

const filteredUsers = computed(() => {
  let list = usersList.value
  if (selectedUserRoleFilter.value !== 'all') {
    list = list.filter(u => u.role === selectedUserRoleFilter.value)
  }
  const q = searchUserText.value.toLowerCase().trim()
  if (!q) return list
  return list.filter(u =>
    u.name?.toLowerCase().includes(q) ||
    u.email?.toLowerCase().includes(q) ||
    u.parent_code?.toLowerCase().includes(q)
  )
})

const filteredAssignments = computed(() => {
  const q = searchAssignmentText.value.toLowerCase().trim()
  if (!q) return assignmentsList.value
  return assignmentsList.value.filter(a =>
    a.title?.toLowerCase().includes(q) ||
    a.class_name?.toLowerCase().includes(q) ||
    a.teacher_name?.toLowerCase().includes(q)
  )
})

const filteredAuditLogs = computed(() => {
  let logs = auditLogsList.value || []
  if (selectedAuditAction.value && selectedAuditAction.value !== 'ALL') {
    logs = logs.filter(l => l.action === selectedAuditAction.value)
  }
  if (searchAuditText.value?.trim()) {
    const q = searchAuditText.value.toLowerCase().trim()
    logs = logs.filter(l =>
      (l.user_email || '').toLowerCase().includes(q) ||
      (l.user_name || '').toLowerCase().includes(q) ||
      (l.details || '').toLowerCase().includes(q) ||
      (l.action || '').toLowerCase().includes(q)
    )
  }
  return logs
})

const getUserRoleColor = (role) => {
  if (role === 'super_admin') return 'deep-purple-darken-3'
  if (role === 'admin') return 'indigo-darken-2'
  if (role === 'teacher') return 'teal-darken-2'
  return 'primary'
}

// Data Fetching Methods & Security Headers
const getAdminAuthHeaders = () => {
  const token = localStorage.getItem('admin_auth_token') || ''
  const headers = { 'Content-Type': 'application/json' }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

const getEffectiveTenantId = () => {
  if (isSuperAdmin.value) {
    return selectedTenantScope.value
  }
  return userTenantId.value || '1'
}

const fetchOverview = async () => {
  try {
    const tid = getEffectiveTenantId()
    const res = await fetch(`${props.backendUrl}/api/admin/overview?tenant_id=${tid}`, {
      headers: getAdminAuthHeaders()
    })
    if (res.status === 401) {
      handleAdminSignOut()
      notify('Session expired. Please sign in again.', 'warning', 'mdi-alert')
      return
    }
    if (res.ok) {
      overview.value = await res.json()
    }
  } catch (e) {
    console.error('Fetch admin overview error:', e)
  }
}

const fetchClassrooms = async () => {
  try {
    const tid = getEffectiveTenantId()
    const res = await fetch(`${props.backendUrl}/api/admin/classes?tenant_id=${tid}`, {
      headers: getAdminAuthHeaders()
    })
    if (res.status === 401) {
      handleAdminSignOut()
      return
    }
    if (res.ok) {
      const data = await res.json()
      classroomsList.value = data.classes || []
    }
  } catch (e) {
    console.error('Fetch admin classrooms error:', e)
  }
}

const fetchUsers = async () => {
  try {
    const tid = getEffectiveTenantId()
    const res = await fetch(`${props.backendUrl}/api/admin/users?tenant_id=${tid}`, {
      headers: getAdminAuthHeaders()
    })
    if (res.status === 401) {
      handleAdminSignOut()
      return
    }
    if (res.ok) {
      const data = await res.json()
      usersList.value = data.users || []
    }
  } catch (e) {
    console.error('Fetch admin users error:', e)
  }
}

const fetchAssignments = async () => {
  try {
    const tid = getEffectiveTenantId()
    const res = await fetch(`${props.backendUrl}/api/admin/assignments?tenant_id=${tid}`, {
      headers: getAdminAuthHeaders()
    })
    if (res.status === 401) {
      handleAdminSignOut()
      return
    }
    if (res.ok) {
      const data = await res.json()
      assignmentsList.value = data.assignments || []
    }
  } catch (e) {
    console.error('Fetch admin assignments error:', e)
  }
}

const fetchTenants = async () => {
  if (!isSuperAdmin.value) return
  isFetchingTenants.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/tenants`, {
      headers: getAdminAuthHeaders()
    })
    if (res.status === 401) {
      handleAdminSignOut()
      return
    }
    if (res.ok) {
      const data = await res.json()
      tenantsList.value = data.tenants || []
      overview.value.tenants = tenantsList.value
    }
  } catch (e) {
    console.error('Fetch tenants error:', e)
  } finally {
    isFetchingTenants.value = false
  }
}

const fetchAuditLogs = async () => {
  isFetchingLogs.value = true
  try {
    let url = `${props.backendUrl}/api/admin/audit-logs?limit=250`
    if (selectedAuditAction.value && selectedAuditAction.value !== 'ALL') {
      url += `&action=${encodeURIComponent(selectedAuditAction.value)}`
    }
    if (searchAuditText.value?.trim()) {
      url += `&search=${encodeURIComponent(searchAuditText.value.trim())}`
    }
    const res = await fetch(url, {
      headers: getAdminAuthHeaders()
    })
    if (res.status === 401) {
      handleAdminSignOut()
      return
    }
    if (res.ok) {
      const data = await res.json()
      auditLogsList.value = data.logs || []
    }
  } catch (e) {
    console.error('Fetch admin audit logs error:', e)
  } finally {
    isFetchingLogs.value = false
  }
}

const getAuditActionColor = (action) => {
  if (action?.includes('DELETE') || action?.includes('CLEAR') || action?.includes('SUSPEND')) return 'error'
  if (action?.includes('CREATE') || action?.includes('PROVISION') || action?.includes('ONBOARD')) return 'success'
  if (action?.includes('UPDATE') || action?.includes('CHANGE') || action?.includes('LIFECYCLE')) return 'warning'
  if (action === 'LOGIN' || action?.includes('IMPERSONATE')) return 'info'
  return 'primary'
}

const fetchAllAdminData = async () => {
  await Promise.all([
    fetchOverview(),
    fetchTenants(),
    fetchClassrooms(),
    fetchUsers(),
    fetchAssignments(),
    fetchAuditLogs()
  ])
}

const onTenantScopeChange = async () => {
  await fetchAllAdminData()
}

// Authentication Actions
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
      if (data.token) {
        localStorage.setItem('admin_auth_token', data.token)
      }
      activeUserRole.value = data.user.role
      localStorage.setItem('user_role', data.user.role)
      if (data.user?.tenant_id) {
        userTenantId.value = data.user.tenant_id
        localStorage.setItem('user_tenant_id', data.user.tenant_id)
      } else {
        userTenantId.value = ''
        localStorage.removeItem('user_tenant_id')
      }
      if (data.user?.email) {
        localStorage.setItem('speak_user_email', data.user.email)
      }
      if (data.user?.name) {
        localStorage.setItem('speak_user_name', data.user.name)
      }
      selectedTenantScope.value = isSuperAdmin.value ? 'all' : (userTenantId.value || '1')
      activeTab.value = isSuperAdmin.value ? 'tenants' : 'classrooms'
      notify(`Welcome! Authenticated as ${data.user.role.toUpperCase()}`, 'success', 'mdi-shield-check')
      await fetchAllAdminData()
    } else {
      const err = await res.json()
      loginError.value = err.detail || 'Invalid Administrator Email or Password.'
    }
  } catch (e) {
    loginError.value = 'Sign In Error: ' + e.message
  } finally {
    isLoggingIn.value = false
  }
}

const confirmAdminSignOut = () => {
  showLogoutDialog.value = false
  handleAdminSignOut()
}

const handleAdminSignOut = () => {
  activeUserRole.value = 'none'
  localStorage.removeItem('user_role')
  localStorage.removeItem('user_tenant_id')
  localStorage.removeItem('admin_auth_token')
  localStorage.removeItem('admin_token')
  localStorage.removeItem('speak_user_email')
  localStorage.removeItem('speak_user_name')
  loginEmail.value = ''
  loginPassword.value = ''
  notify('Signed out from Administration Console.', 'info', 'mdi-logout')
  window.location.href = '/'
}

// Provisioning & User Actions
const submitProvisioning = async () => {
  if (!newProvEmail.value.trim() || !newProvName.value.trim()) {
    notify('Please fill in email and full name.', 'warning')
    return
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(newProvEmail.value.trim())) {
    notify('Please enter a valid email address.', 'warning')
    return
  }
  isProvisioning.value = true
  try {
    const isFreelance = isSuperAdmin.value && newProvRole.value === 'teacher' && newProvTeacherType.value === 'freelance'
    const payload = {
      email: newProvEmail.value.trim(),
      name: newProvName.value.trim(),
      role: newProvRole.value,
      tenant_id: isFreelance ? null : (isSuperAdmin.value ? newProvTenantId.value : (userTenantId.value || '1')),
      password: newProvPassword.value.trim() || 'password123',
      teacher_type: isFreelance ? 'freelance' : 'institutional',
      max_seats: isFreelance ? (Number(newProvMaxSeats.value) || 30) : null,
      max_classes: isFreelance ? (Number(newProvMaxClasses.value) || 3) : null,
      license_expiry: isFreelance ? newProvPlanExpiry.value.trim() : null
    }
    const res = await fetch(`${props.backendUrl}/api/admin/provision-account`, {
      method: 'POST',
      headers: getAdminAuthHeaders(),
      body: JSON.stringify(payload)
    })
    if (res.ok) {
      showProvisionModal.value = false
      notify(`Account provisioned successfully${isFreelance ? ' as Freelance Educator' : ''}!`, 'success', 'mdi-account-check')
      newProvEmail.value = ''
      newProvName.value = ''
      newProvPassword.value = 'password123'
      await fetchAllAdminData()
    } else {
      const err = await res.json()
      notify(err.detail || 'Provisioning failed.', 'error')
    }
  } catch (e) {
    notify('Provisioning failed: ' + e.message, 'error', 'mdi-alert-circle')
  } finally {
    isProvisioning.value = false
  }
}

const openChangeRoleModal = (usr) => {
  userToChangeRole.value = usr
  selectedNewRole.value = usr.role === 'student' ? 'teacher' : (usr.role === 'teacher' ? 'student' : usr.role)
  showChangeRoleModal.value = true
}

const submitChangeRole = async () => {
  if (!userToChangeRole.value) return
  isUpdatingRole.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/users/${userToChangeRole.value.id}/change-role`, {
      method: 'POST',
      headers: getAdminAuthHeaders(),
      body: JSON.stringify({
        new_role: selectedNewRole.value,
        tenant_id: userToChangeRole.value.tenant_id || (userTenantId.value || '1')
      })
    })
    if (res.ok) {
      showChangeRoleModal.value = false
      notify(`Role updated to ${selectedNewRole.value.toUpperCase()}!`, 'success')
      await fetchUsers()
      await fetchOverview()
    } else {
      const err = await res.json()
      notify(err.detail || 'Could not update role.', 'error')
    }
  } catch (e) {
    notify('Role change error: ' + e.message, 'error')
  } finally {
    isUpdatingRole.value = false
  }
}

const openEditUserModal = (usr) => {
  editUserId.value = usr.id
  editUserEmail.value = usr.email
  editUserName.value = usr.name
  editUserPass.value = ''
  showEditUserModal.value = true
}

const submitEditUser = async () => {
  if (!editUserId.value) return
  isUpdatingUser.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/users/${editUserId.value}/update`, {
      method: 'POST',
      headers: getAdminAuthHeaders(),
      body: JSON.stringify({
        email: editUserEmail.value.trim(),
        name: editUserName.value.trim(),
        role: usersList.value.find(u => u.id === editUserId.value)?.role || 'student',
        password: editUserPass.value.trim()
      })
    })
    if (res.ok) {
      showEditUserModal.value = false
      notify('User details updated!', 'success')
      await fetchUsers()
    } else {
      const err = await res.json()
      notify(err.detail || 'Could not update user.', 'error')
    }
  } catch (e) {
    notify('Update user error: ' + e.message, 'error')
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
      method: 'DELETE',
      headers: getAdminAuthHeaders()
    })
    if (res.ok) {
      showDeleteUserModal.value = false
      notify(`Account deleted successfully.`, 'info')
      await fetchAllAdminData()
    } else {
      const err = await res.json()
      notify(err.detail || 'Could not delete user.', 'error')
    }
  } catch (e) {
    notify('Delete user error: ' + e.message, 'error')
  } finally {
    isDeletingUser.value = false
  }
}

// Classroom Actions
const confirmDeleteClassroom = (cls) => {
  classToDelete.value = cls
  showDeleteClassModal.value = true
}

const submitDeleteClassroom = async () => {
  if (!classToDelete.value) return
  isDeletingClass.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/classes/${classToDelete.value.id}/delete`, {
      method: 'POST',
      headers: getAdminAuthHeaders(),
      body: JSON.stringify({})
    })
    if (res.ok) {
      showDeleteClassModal.value = false
      notify(`Classroom deleted.`, 'info')
      await fetchAllAdminData()
    } else {
      const err = await res.json()
      notify(err.detail || 'Could not delete classroom.', 'error')
    }
  } catch (e) {
    notify('Delete class error: ' + e.message, 'error')
  } finally {
    isDeletingClass.value = false
  }
}

// P1: Classroom & Student Actions
const submitCreateClass = async () => {
  if (!newClassName.value.trim() || !newClassTeacherId.value) {
    notify('Please specify class name and select a teacher in charge.', 'warning')
    return
  }
  isCreatingClass.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/classes/create`, {
      method: 'POST',
      headers: getAdminAuthHeaders(),
      body: JSON.stringify({
        name: newClassName.value.trim(),
        grade_level: newClassGrade.value.trim() || 'General',
        teacher_id: Number(newClassTeacherId.value),
        tenant_id: isSuperAdmin.value ? selectedTenantScope.value : (userTenantId.value || '1')
      })
    })
    if (res.ok) {
      showCreateClassModal.value = false
      newClassName.value = ''
      newClassGrade.value = ''
      newClassTeacherId.value = null
      notify('Classroom created successfully!', 'success', 'mdi-check-circle')
      await fetchClassrooms()
      await fetchOverview()
    } else {
      const err = await res.json()
      notify(err.detail || 'Could not create classroom.', 'error')
    }
  } catch (e) {
    notify('Create class error: ' + e.message, 'error')
  } finally {
    isCreatingClass.value = false
  }
}

const openAssignTeacherModal = (cls) => {
  classToAssignTeacher.value = cls
  selectedNewTeacherId.value = cls.teacher_id || null
  showAssignTeacherModal.value = true
}

const submitAssignTeacher = async () => {
  if (!classToAssignTeacher.value || !selectedNewTeacherId.value) return
  isAssigningTeacher.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/classes/${classToAssignTeacher.value.id}/assign-teacher`, {
      method: 'POST',
      headers: getAdminAuthHeaders(),
      body: JSON.stringify({ teacher_id: Number(selectedNewTeacherId.value) })
    })
    if (res.ok) {
      showAssignTeacherModal.value = false
      notify('Teacher reassigned successfully!', 'success')
      await fetchClassrooms()
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to reassign teacher.', 'error')
    }
  } catch (e) {
    notify('Assign teacher error: ' + e.message, 'error')
  } finally {
    isAssigningTeacher.value = false
  }
}

const confirmToggleArchive = (cls) => {
  classToToggleArchive.value = cls
  showArchiveClassModal.value = true
}

const submitToggleArchive = async () => {
  if (!classToToggleArchive.value) return
  isArchivingClass.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/classes/${classToToggleArchive.value.id}/toggle-archive`, {
      method: 'POST',
      headers: getAdminAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      showArchiveClassModal.value = false
      notify(data.message || 'Classroom status updated.', 'success')
      await fetchClassrooms()
      await fetchOverview()
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to toggle archive status.', 'error')
    }
  } catch (e) {
    notify('Archive toggle error: ' + e.message, 'error')
  } finally {
    isArchivingClass.value = false
  }
}

const openClassRoster = async (cls) => {
  activeRosterClass.value = cls
  classRosterStudents.value = []
  showClassRosterModal.value = true
  isFetchingRoster.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/classes/${cls.id}/roster`, {
      headers: getAdminAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      classRosterStudents.value = data.students || []
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to load class roster.', 'error')
    }
  } catch (e) {
    notify('Load roster error: ' + e.message, 'error')
  } finally {
    isFetchingRoster.value = false
  }
}

const openTransferStudentModal = (stu) => {
  studentToTransfer.value = stu
  targetTransferClassId.value = null
  showTransferStudentModal.value = true
}

const submitTransferStudent = async () => {
  if (!studentToTransfer.value || !targetTransferClassId.value || !activeRosterClass.value) return
  isTransferringStudent.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/classes/${activeRosterClass.value.id}/transfer-student`, {
      method: 'POST',
      headers: getAdminAuthHeaders(),
      body: JSON.stringify({
        student_id: Number(studentToTransfer.value.id),
        to_class_id: Number(targetTransferClassId.value)
      })
    })
    if (res.ok) {
      showTransferStudentModal.value = false
      notify('Student transferred successfully!', 'success')
      await openClassRoster(activeRosterClass.value)
      await fetchClassrooms()
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to transfer student.', 'error')
    }
  } catch (e) {
    notify('Transfer error: ' + e.message, 'error')
  } finally {
    isTransferringStudent.value = false
  }
}

const confirmRevokeStudent = (stu) => {
  studentToRevoke.value = stu
  showRevokeStudentModal.value = true
}

const submitRevokeStudent = async () => {
  if (!studentToRevoke.value || !activeRosterClass.value) return
  isRevokingStudent.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/classes/${activeRosterClass.value.id}/revoke-student/${studentToRevoke.value.id}`, {
      method: 'POST',
      headers: getAdminAuthHeaders()
    })
    if (res.ok) {
      showRevokeStudentModal.value = false
      notify('Student seat revoked successfully.', 'info', 'mdi-account-minus')
      await openClassRoster(activeRosterClass.value)
      await fetchAllAdminData()
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to revoke seat.', 'error')
    }
  } catch (e) {
    notify('Revoke error: ' + e.message, 'error')
  } finally {
    isRevokingStudent.value = false
  }
}

const confirmToggleTeacher = (usr) => {
  teacherToToggle.value = usr
  showToggleTeacherModal.value = true
}

const submitToggleTeacherStatus = async () => {
  if (!teacherToToggle.value) return
  isTogglingTeacher.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/teachers/${teacherToToggle.value.id}/toggle-status`, {
      method: 'POST',
      headers: getAdminAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      showToggleTeacherModal.value = false
      notify(data.message || 'Teacher status updated.', 'success')
      await fetchUsers()
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to change teacher status.', 'error')
    }
  } catch (e) {
    notify('Toggle status error: ' + e.message, 'error')
  } finally {
    isTogglingTeacher.value = false
  }
}

const openResetTeacherPass = (usr) => {
  teacherToResetPass.value = usr
  newTeacherPasswordInput.value = ''
  showResetTeacherPassModal.value = true
}

const submitResetTeacherPassword = async () => {
  if (!teacherToResetPass.value || !newTeacherPasswordInput.value.trim()) return
  if (newTeacherPasswordInput.value.trim().length < 6) {
    notify('Password must be at least 6 characters long.', 'warning')
    return
  }
  isResettingTeacherPass.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/teachers/${teacherToResetPass.value.id}/reset-password`, {
      method: 'POST',
      headers: getAdminAuthHeaders(),
      body: JSON.stringify({ new_password: newTeacherPasswordInput.value.trim() })
    })
    if (res.ok) {
      showResetTeacherPassModal.value = false
      notify('Teacher password updated successfully!', 'success', 'mdi-key-check')
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to reset password.', 'error')
    }
  } catch (e) {
    notify('Reset password error: ' + e.message, 'error')
  } finally {
    isResettingTeacherPass.value = false
  }
}

// Independent / Freelance Educator Plan Management (Super Admin Only)
const showConfigurePlanModal = ref(false)
const teacherToConfigurePlan = ref(null)
const editTeacherType = ref('freelance')
const editMaxSeats = ref(30)
const editMaxClasses = ref(3)
const editPlanExpiry = ref('2028-12-31')
const isSavingPlan = ref(false)

const openConfigureTeacherPlan = (usr) => {
  teacherToConfigurePlan.value = usr
  editTeacherType.value = usr.teacher_type || 'institutional'
  editMaxSeats.value = usr.max_seats || 30
  editMaxClasses.value = usr.max_classes || 3
  editPlanExpiry.value = usr.license_expiry || '2028-12-31'
  showConfigurePlanModal.value = true
}

const submitSaveTeacherPlan = async () => {
  if (!teacherToConfigurePlan.value) return
  isSavingPlan.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/teachers/${teacherToConfigurePlan.value.id}/plan`, {
      method: 'POST',
      headers: getAdminAuthHeaders(),
      body: JSON.stringify({
        teacher_type: editTeacherType.value,
        max_seats: Number(editMaxSeats.value) || 30,
        max_classes: Number(editMaxClasses.value) || 3,
        license_expiry: editPlanExpiry.value.trim()
      })
    })
    if (res.ok) {
      showConfigurePlanModal.value = false
      notify('Educator plan updated successfully!', 'success', 'mdi-check-decagram')
      await fetchUsers()
      await fetchTeachers()
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to update plan.', 'error')
    }
  } catch (e) {
    notify('Update plan error: ' + e.message, 'error')
  } finally {
    isSavingPlan.value = false
  }
}

// Tenant Actions (Super Admin Only)
const submitCreateTenant = async () => {
  if (!newTenantName.value.trim()) return
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/tenants/create`, {
      method: 'POST',
      headers: getAdminAuthHeaders(),
      body: JSON.stringify({
        name: newTenantName.value.trim(),
        license_seats: Number(newTenantSeats.value) || 100
      })
    })
    if (res.ok) {
      showCreateTenantModal.value = false
      newTenantName.value = ''
      notify('New B2B School Organization activated!', 'success')
      await fetchOverview()
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to create tenant.', 'error')
    }
  } catch (e) {
    notify('Failed to create tenant: ' + e.message, 'error')
  }
}

const openEditTenantModal = (t) => {
  editTenantId.value = t.id
  editTenantName.value = t.name
  editTenantSeats.value = t.license_seats
  editTenantExpiry.value = t.license_expiry
  showEditTenantModal.value = true
}

const submitEditTenant = async () => {
  if (!editTenantId.value) return
  isUpdatingTenant.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/tenants/${editTenantId.value}/update`, {
      method: 'POST',
      headers: getAdminAuthHeaders(),
      body: JSON.stringify({
        name: editTenantName.value.trim(),
        license_seats: Number(editTenantSeats.value) || 100,
        license_expiry: editTenantExpiry.value.trim()
      })
    })
    if (res.ok) {
      showEditTenantModal.value = false
      notify('School tenant details updated!', 'success')
      await fetchOverview()
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to update tenant.', 'error')
    }
  } catch (e) {
    notify('Failed to update tenant: ' + e.message, 'error')
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
      method: 'DELETE',
      headers: getAdminAuthHeaders()
    })
    if (res.ok) {
      showDeleteTenantModal.value = false
      notify(`Tenant ${tenantToDelete.value.name} removed.`, 'info')
      await fetchOverview()
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to delete tenant.', 'error')
    }
  } catch (e) {
    notify('Delete tenant error: ' + e.message, 'error')
  } finally {
    isDeletingTenant.value = false
  }
}

// Storage Maintenance (Super Admin Only)
const runAutoCleanup = async () => {
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/auto-cleanup`, {
      method: 'POST',
      headers: getAdminAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      notify(data.message, 'success', 'mdi-broom')
      await fetchOverview()
    } else {
      const err = await res.json()
      notify(err.detail || 'Cleanup failed.', 'error')
    }
  } catch (e) {
    notify('Cleanup worker error: ' + e.message, 'error')
  }
}

const saveSystemSettings = async () => {
  isSavingSettings.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/settings/update`, {
      method: 'POST',
      headers: getAdminAuthHeaders(),
      body: JSON.stringify({ retention_days: Number(retentionDaysInput.value) || 60 })
    })
    if (res.ok) {
      notify('Audio retention policy updated successfully!', 'success')
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to update settings.', 'error')
    }
  } catch (e) {
    notify('Failed to update settings: ' + e.message, 'error')
  } finally {
    isSavingSettings.value = false
  }
}

// P3 Super Admin Governance Actions
const submitOnboardTenant = async () => {
  if (!onboardSchoolName.value.trim() || !onboardAdminEmail.value.trim() || !onboardAdminName.value.trim()) {
    notify('Please fill in school name, admin email, and admin name.', 'warning')
    return
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(onboardAdminEmail.value.trim())) {
    notify('Please enter a valid administrator email address.', 'warning')
    return
  }
  isOnboarding.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/tenants/onboard`, {
      method: 'POST',
      headers: getAdminAuthHeaders(),
      body: JSON.stringify({
        school_name: onboardSchoolName.value.trim(),
        admin_email: onboardAdminEmail.value.trim(),
        admin_name: onboardAdminName.value.trim(),
        admin_password: onboardAdminPassword.value.trim() || 'Admin@12345',
        license_seats: Number(onboardSeats.value) || 100,
        license_expiry: onboardExpiry.value.trim() || '2028-12-31',
        status: onboardStatus.value || 'active'
      })
    })
    if (res.ok) {
      const data = await res.json()
      showOnboardModal.value = false
      onboardSchoolName.value = ''
      onboardAdminEmail.value = ''
      onboardAdminName.value = ''
      onboardAdminPassword.value = 'Admin@12345'
      onboardSeats.value = 100
      notify(`School '${data.school_name}' onboarded successfully with School Admin ${data.admin_email}!`, 'success', 'mdi-check-decagram')
      await fetchAllAdminData()
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to onboard school.', 'error')
    }
  } catch (e) {
    notify('Onboarding error: ' + e.message, 'error')
  } finally {
    isOnboarding.value = false
  }
}

const openLifecycleModal = (t) => {
  tenantForLifecycle.value = t
  lifecycleSchoolName.value = t.name || ''
  lifecycleAdminEmail.value = t.admin_email || ''
  lifecycleAdminName.value = t.admin_name || ''
  lifecycleAdminPassword.value = ''
  lifecycleStatus.value = t.status || 'active'
  lifecycleSeats.value = t.license_seats ?? 100
  lifecycleExpiry.value = t.license_expiry || '2028-12-31'
  showLifecycleModal.value = true
}

const submitLifecycle = async () => {
  if (!tenantForLifecycle.value) return
  if (!lifecycleSchoolName.value.trim()) {
    notify('School name cannot be empty.', 'warning')
    return
  }
  if (lifecycleAdminEmail.value.trim()) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(lifecycleAdminEmail.value.trim())) {
      notify('Please enter a valid administrator email address.', 'warning')
      return
    }
  }
  isUpdatingLifecycle.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/tenants/${tenantForLifecycle.value.id}/lifecycle`, {
      method: 'POST',
      headers: getAdminAuthHeaders(),
      body: JSON.stringify({
        status: lifecycleStatus.value,
        license_seats: Number(lifecycleSeats.value) || 100,
        license_expiry: lifecycleExpiry.value.trim(),
        school_name: lifecycleSchoolName.value.trim(),
        admin_email: lifecycleAdminEmail.value.trim() || null,
        admin_name: lifecycleAdminName.value.trim() || null,
        admin_password: lifecycleAdminPassword.value.trim() || null
      })
    })
    if (res.ok) {
      const data = await res.json()
      showLifecycleModal.value = false
      notify(`School '${data.school_name || tenantForLifecycle.value.name}' updated successfully!`, 'success')
      await fetchAllAdminData()
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to update tenant configuration.', 'error')
    }
  } catch (e) {
    notify('Update error: ' + e.message, 'error')
  } finally {
    isUpdatingLifecycle.value = false
  }
}

const openInspectSchoolModal = (t) => {
  tenantToInspect.value = t
  showInspectSchoolModal.value = true
}

const submitEnterSupportMode = async () => {
  if (!tenantToInspect.value) return
  isEnteringSupportMode.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/impersonate-tenant/${tenantToInspect.value.id}`, {
      method: 'POST',
      headers: getAdminAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      showInspectSchoolModal.value = false

      const originalToken = localStorage.getItem('admin_auth_token')
      if (originalToken) {
        localStorage.setItem('super_admin_backup_token', originalToken)
      }
      localStorage.setItem('admin_auth_token', data.token)
      activeUserRole.value = 'admin'
      userTenantId.value = String(data.user.tenant_id)
      supportSchoolName.value = data.tenant.name
      supportAdminEmail.value = data.user.email
      isSupportMode.value = true
      activeTab.value = 'classrooms'
      notify(`Entered Support Inspection Mode for ${data.tenant.name}`, 'info', 'mdi-shield-account')
      await fetchAllAdminData()
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to enter support mode.', 'error')
    }
  } catch (e) {
    notify('Support mode error: ' + e.message, 'error')
  } finally {
    isEnteringSupportMode.value = false
  }
}

const exitSupportMode = async () => {
  const originalToken = localStorage.getItem('super_admin_backup_token')
  if (originalToken) {
    localStorage.setItem('admin_auth_token', originalToken)
    localStorage.removeItem('super_admin_backup_token')
  }
  activeUserRole.value = 'super_admin'
  userTenantId.value = ''
  isSupportMode.value = false
  selectedTenantScope.value = 'all'
  activeTab.value = 'tenants'
  notify('Exited Support Mode. Returned to Super Admin Platform Governance.', 'success', 'mdi-shield-check')
  await fetchAllAdminData()
}

const downloadBackupSnapshot = async () => {
  isExportingSnapshot.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/admin/backup-snapshot`, {
      headers: getAdminAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      const jsonStr = JSON.stringify(data, null, 2)
      const blob = new Blob([jsonStr], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      a.href = url
      a.download = `fluent_platform_backup_${timestamp}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      notify(`Platform backup snapshot downloaded! Total records: ${data.total_records}`, 'success', 'mdi-download')
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to export backup.', 'error')
    }
  } catch (e) {
    notify('Failed to export backup snapshot: ' + e.message, 'error')
  } finally {
    isExportingSnapshot.value = false
  }
}

const snapshotFileInput = ref(null)
const selectedSnapshotFile = ref(null)
const showConfirmRestoreModal = ref(false)
const isRestoringSnapshot = ref(false)
const showConfirmCleanProductionModal = ref(false)
const isCleaningProduction = ref(false)

const triggerRestoreSnapshotUpload = () => {
  snapshotFileInput.value?.click()
}

const handleSnapshotFileSelected = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  selectedSnapshotFile.value = file
  showConfirmRestoreModal.value = true
}

const submitRestoreSnapshot = async () => {
  if (!selectedSnapshotFile.value) return
  isRestoringSnapshot.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedSnapshotFile.value)
    const res = await fetch(`${props.backendUrl}/api/admin/restore-snapshot`, {
      method: 'POST',
      headers: {
        Authorization: getAdminAuthHeaders().Authorization
      },
      body: formData
    })
    if (res.ok) {
      showConfirmRestoreModal.value = false
      selectedSnapshotFile.value = null
      notify('Database snapshot restored successfully!', 'success', 'mdi-check-decagram')
      await fetchAllAdminData()
    } else {
      const err = await res.json()
      notify(err.detail || 'Restore failed.', 'error')
    }
  } catch (e) {
    notify('Restore error: ' + e.message, 'error')
  } finally {
    isRestoringSnapshot.value = false
    if (snapshotFileInput.value) snapshotFileInput.value.value = ''
  }
}

const openConfirmCleanProductionModal = () => {
  showConfirmCleanProductionModal.value = true
}

const submitCleanProductionReset = async () => {
  isCleaningProduction.value = true
  try {
    // 1. Download snapshot backup automatically before cleaning
    await downloadBackupSnapshot()
    
    // 2. Perform production reset
    const res = await fetch(`${props.backendUrl}/api/admin/clean-production-reset`, {
      method: 'POST',
      headers: getAdminAuthHeaders()
    })
    if (res.ok) {
      showConfirmCleanProductionModal.value = false
      notify('Demo data cleaned! System is in Clean Production State.', 'success', 'mdi-broom')
      await fetchAllAdminData()
    } else {
      const err = await res.json()
      notify(err.detail || 'Clean production reset failed.', 'error')
    }
  } catch (e) {
    notify('Clean error: ' + e.message, 'error')
  } finally {
    isCleaningProduction.value = false
  }
}

onMounted(async () => {
  if (['admin', 'super_admin'].includes(activeUserRole.value)) {
    await fetchAllAdminData()
  }
})
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}
.bg-black-subtle {
  background-color: rgba(0, 0, 0, 0.25);
}
</style>
