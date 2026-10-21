<template>
  <v-container fluid class="pa-4 pa-md-6">
    <!-- Vuetify Toast Notification -->
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

    <!-- Embedded Educator Sign In Card if Not Authenticated as Teacher -->
    <div v-if="!['teacher', 'admin', 'super_admin'].includes(activeUserRole)" class="d-flex justify-center py-12">
      <v-card border flat class="pa-6 bg-white rounded-lg elevation-3" style="max-width: 440px; width: 100%;">
        <div class="text-center mb-4">
          <v-avatar color="indigo-darken-3" size="56" class="text-white mb-2 elevation-2">
            <v-icon size="large">mdi-school-outline</v-icon>
          </v-avatar>
          <div class="text-h6 font-weight-black text-indigo-darken-3">EDUCATOR PORTAL SIGN IN</div>
          <div class="text-caption text-grey-darken-1 font-weight-medium">Authorized Teachers & Instructors Only</div>
        </div>

        <v-alert v-if="loginError" type="error" variant="tonal" density="compact" class="mb-3 text-caption font-weight-bold">
          {{ loginError }}
        </v-alert>

        <v-text-field
          v-model="loginEmail"
          label="Teacher Email:"
          placeholder="teacher@fluent.edu.vn"
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
          class="mb-3"
          prepend-inner-icon="mdi-lock-outline"
          @keyup.enter="handleTeacherSignIn"
        />

        <v-btn
          color="indigo-darken-3"
          variant="flat"
          block
          size="large"
          class="font-weight-black text-none"
          :loading="isLoggingIn"
          @click="handleTeacherSignIn"
        >
          Sign In to Teacher Hub
        </v-btn>
      </v-card>
    </div>

    <!-- Main Educator Workspace -->
    <div v-else>
      <!-- Sleek Minimalist Page Header Bar -->
      <div class="d-flex align-center justify-space-between flex-wrap ga-2 mb-3 pb-2 border-b">
        <div class="d-flex align-center ga-3 flex-wrap">
          <div class="d-flex align-center ga-2">
            <v-icon color="indigo-darken-3" size="26">mdi-school-outline</v-icon>
            <span class="text-h6 font-weight-black text-grey-darken-4">Teacher Hub</span>
          </div>

          <!-- Micro Stats Badges (Replaces 3 Bulky Cards) -->
          <div class="d-flex align-center ga-1.5 flex-wrap">
            <v-chip size="small" variant="tonal" color="indigo" class="font-weight-bold">
              <v-icon start size="14">mdi-google-classroom</v-icon>
              {{ classes.length }} Classes
            </v-chip>
            <v-chip size="small" variant="tonal" color="teal" class="font-weight-bold">
              <v-icon start size="14">mdi-account-group</v-icon>
              {{ totalStudentsCount }} Students
            </v-chip>
            <v-chip size="small" variant="tonal" color="purple" class="font-weight-bold">
              <v-icon start size="14">mdi-file-document-check</v-icon>
              {{ totalSubmissionsCount }} Submissions
            </v-chip>
          </div>
        </div>

        <div class="d-flex align-center ga-2">
          <v-btn
            color="primary"
            variant="flat"
            size="small"
            class="font-weight-black text-none"
            prepend-icon="mdi-plus"
            @click="showCreateClassModal = true"
          >
            Create Class
          </v-btn>
          <v-btn
            color="grey-darken-2"
            variant="text"
            size="small"
            class="font-weight-bold text-none"
            prepend-icon="mdi-logout"
            @click="showLogoutDialog = true"
          >
            Sign Out
          </v-btn>
        </div>
      </div>

      <!-- Freelance Educator License Plan Card -->
      <v-card
        v-if="teacherQuota && teacherQuota.teacher_type === 'freelance'"
        border
        flat
        class="pa-3 mb-3 bg-indigo-lighten-5 rounded-lg border-indigo-lighten-4 elevation-1"
      >
        <div class="d-flex align-center justify-space-between flex-wrap ga-3">
          <div class="d-flex align-center ga-3 flex-wrap">
            <div class="d-flex align-center ga-2">
              <v-avatar size="34" color="indigo-darken-3" class="text-white elevation-1">
                <v-icon size="18">mdi-account-star</v-icon>
              </v-avatar>
              <div>
                <div class="d-flex align-center ga-2">
                  <span class="text-subtitle-2 font-weight-black text-indigo-darken-4">Freelance Educator Plan</span>
                  <v-chip size="x-small" :color="teacherQuota.is_expired ? 'error' : 'success'" variant="flat" class="font-weight-black">
                    {{ teacherQuota.is_expired ? 'EXPIRED' : 'ACTIVE' }}
                  </v-chip>
                </div>
                <div class="text-caption text-grey-darken-2">
                  License Expiry: <strong>{{ teacherQuota.license_expiry || '2028-12-31' }}</strong>
                </div>
              </div>
            </div>

            <!-- Student Seats Meter -->
            <div class="bg-white px-3 py-1.5 rounded-lg border" style="min-width: 190px;">
              <div class="d-flex justify-space-between text-caption font-weight-bold text-grey-darken-3 mb-1">
                <span class="d-flex align-center ga-1"><v-icon size="14" color="indigo">mdi-seat</v-icon> Student Seats</span>
                <span :class="teacherQuota.used_seats >= teacherQuota.max_seats ? 'text-error font-weight-black' : 'text-indigo-darken-3'">
                  {{ teacherQuota.used_seats }} / {{ teacherQuota.max_seats }}
                </span>
              </div>
              <v-progress-linear
                :model-value="teacherQuota.usage_percentage"
                :color="teacherQuota.used_seats >= teacherQuota.max_seats ? 'error' : 'indigo'"
                height="6"
                rounded
              />
            </div>

            <!-- Classrooms Meter -->
            <div class="bg-white px-3 py-1.5 rounded-lg border" style="min-width: 170px;">
              <div class="d-flex justify-space-between text-caption font-weight-bold text-grey-darken-3 mb-1">
                <span class="d-flex align-center ga-1"><v-icon size="14" color="teal">mdi-google-classroom</v-icon> Classrooms</span>
                <span :class="teacherQuota.used_classes >= teacherQuota.max_classes ? 'text-warning font-weight-black' : 'text-teal-darken-3'">
                  {{ teacherQuota.used_classes }} / {{ teacherQuota.max_classes }}
                </span>
              </div>
              <v-progress-linear
                :model-value="(teacherQuota.used_classes / (teacherQuota.max_classes || 1)) * 100"
                :color="teacherQuota.used_classes >= teacherQuota.max_classes ? 'warning' : 'teal'"
                height="6"
                rounded
              />
            </div>
          </div>

          <!-- Upgrade / Manage Plan Button -->
          <v-btn
            color="indigo-darken-3"
            variant="flat"
            size="small"
            class="font-weight-black text-none"
            prepend-icon="mdi-arrow-up-bold-circle-outline"
            @click="showPlanDetailsModal = true"
          >
            Upgrade Plan
          </v-btn>
        </div>
      </v-card>

    <!-- Main Content Area -->
    <v-row density="comfortable">
      <!-- Mobile Horizontal Class Switcher Bar (Visible on mobile/tablet) -->
      <v-col cols="12" class="d-md-none pb-0">
        <v-card border flat class="pa-3 bg-white rounded-lg mb-2">
          <div class="d-flex align-center justify-space-between mb-2">
            <span class="text-caption font-weight-black text-secondary">ACTIVE CLASSROOMS ({{ classes.length }})</span>
            <v-btn size="x-small" color="primary" variant="flat" prepend-icon="mdi-plus" class="font-weight-bold text-none" @click="showCreateClassModal = true">
              New Class
            </v-btn>
          </div>
          <div class="d-flex align-center ga-2 overflow-x-auto pb-1" style="white-space: nowrap;">
            <v-chip
              v-for="cls in classes"
              :key="cls.id"
              :color="selectedClassId === cls.id ? 'primary' : 'grey-lighten-4'"
              :variant="selectedClassId === cls.id ? 'flat' : 'tonal'"
              size="comfortable"
              class="font-weight-bold flex-shrink-0 cursor-pointer"
              @click="selectClass(cls.id)"
            >
              <v-icon start size="small">mdi-google-classroom</v-icon>
              {{ cls.name }} ({{ cls.student_count || 0 }})
            </v-chip>
          </div>
        </v-card>
      </v-col>

      <!-- Desktop Left Column: Sticky & Searchable Class Selector List -->
      <v-col cols="12" md="3" class="d-none d-md-block">
        <v-card border flat class="pa-3 bg-white rounded-lg class-sidebar-sticky">
          <!-- Header with Quick Add & Refresh -->
          <div class="text-subtitle-2 font-weight-black text-secondary mb-2 d-flex align-center justify-space-between">
            <span class="d-flex align-center ga-1">
              <v-icon size="small" color="secondary">mdi-google-classroom</v-icon>
              <span>MY CLASSES ({{ classes.length }})</span>
            </span>
            <div class="d-flex align-center ga-1">
              <v-btn icon="mdi-plus" variant="tonal" color="primary" density="compact" size="small" title="Quick Add Class" @click="showCreateClassModal = true" />
              <v-btn icon="mdi-refresh" variant="text" density="compact" size="small" title="Refresh Class List" @click="fetchClasses" />
            </div>
          </div>

          <!-- Quick Search Filter for Classes -->
          <v-text-field
            v-if="classes.length > 2"
            v-model="searchClassText"
            placeholder="Search classes..."
            variant="outlined"
            density="compact"
            hide-details
            clearable
            prepend-inner-icon="mdi-magnify"
            class="mb-2"
          />

          <!-- Scrollable Class Cards Container -->
          <div class="class-list-scroll">
            <v-list density="compact" class="pa-0">
              <v-list-item
                v-for="cls in filteredClasses"
                :key="cls.id"
                :active="selectedClassId === cls.id"
                rounded="lg"
                class="mb-1 pa-2 transition-all cursor-pointer"
                :class="selectedClassId === cls.id ? 'bg-indigo-lighten-5 text-indigo-darken-4 font-weight-black' : 'text-grey-darken-3 hover-item'"
                @click="selectClass(cls.id)"
              >
                <template #prepend>
                  <v-avatar
                    :color="selectedClassId === cls.id ? 'indigo' : 'grey-lighten-3'"
                    :class="selectedClassId === cls.id ? 'text-white' : 'text-grey-darken-3'"
                    size="30"
                    class="mr-2 font-weight-black text-caption"
                  >
                    {{ cls.name.slice(0, 2).toUpperCase() }}
                  </v-avatar>
                </template>
                <v-list-item-title class="font-weight-black text-body-2 text-truncate">{{ cls.name }}</v-list-item-title>
                <v-list-item-subtitle class="text-caption text-grey-darken-1 d-flex align-center ga-1 mt-0.5">
                  <span class="font-mono text-primary font-weight-bold">{{ cls.join_code }}</span>
                  <span>•</span>
                  <span>{{ cls.student_count || 0 }} {{ cls.student_count === 1 ? 'student' : 'students' }}</span>
                </v-list-item-subtitle>
              </v-list-item>

              <!-- Empty state for search -->
              <div v-if="classes.length && !filteredClasses.length" class="text-center pa-4 text-caption text-grey">
                <v-icon size="small" color="grey">mdi-magnify-close</v-icon>
                <div class="mt-1">No classes match "{{ searchClassText }}"</div>
              </div>

              <!-- Empty state for zero classes -->
              <div v-else-if="!classes.length" class="text-center pa-4 text-caption text-grey">
                No classes created yet. Click "Create Class" to start!
              </div>
            </v-list>
          </div>
        </v-card>
      </v-col>

      <!-- Right Column: Gradebook & Assignments for Selected Class -->
      <v-col cols="12" md="9">
        <v-card v-if="selectedClass" border flat class="pa-3 bg-white rounded-lg">
          <!-- Class Header Banner -->
          <div class="d-flex align-center justify-space-between flex-wrap ga-2 border-b pb-2 mb-3">
            <div>
              <div class="d-flex align-center ga-2 flex-wrap">
                <span class="text-h6 font-weight-black text-grey-darken-4">{{ selectedClass.name }}</span>
                <v-chip color="indigo" size="x-small" variant="tonal" class="font-weight-bold">
                  {{ selectedClass.grade_level }}
                </v-chip>
                <v-btn icon="mdi-pencil-outline" size="x-small" color="grey-darken-2" variant="text" title="Edit Class Information" @click="openEditClassModal" />
                <v-btn icon="mdi-delete-outline" size="x-small" color="error" variant="text" title="Delete Classroom" @click="showDeleteClassModal = true" />
              </div>
              <div class="text-caption text-grey-darken-2 d-flex align-center flex-wrap ga-2 mt-1">
                <v-chip
                  color="primary"
                  size="small"
                  variant="tonal"
                  class="font-weight-mono font-weight-black cursor-pointer"
                  prepend-icon="mdi-key-variant"
                  title="Click to copy join code"
                  @click="copyJoinCode(selectedClass.join_code)"
                >
                  Code: {{ selectedClass.join_code }}
                  <v-icon end size="x-small">mdi-content-copy</v-icon>
                </v-chip>

                <!-- Full Domain Link & QR Code Buttons -->
                <v-btn size="small" color="grey-darken-3" variant="text" class="font-weight-bold text-none" prepend-icon="mdi-link-variant" @click="copyFullClassLink(selectedClass.join_code)">
                  Copy Link
                </v-btn>

                <v-btn size="small" color="indigo-darken-2" variant="text" class="font-weight-bold text-none" prepend-icon="mdi-qrcode" @click="openQrPosterModal(selectedClass)">
                  Class QR
                </v-btn>
              </div>
            </div>

            <div class="d-flex align-center ga-2">
              <v-btn
                color="secondary"
                variant="flat"
                size="small"
                class="font-weight-bold text-none"
                prepend-icon="mdi-send-outline"
                @click="showCreateAssignmentModal = true"
              >
                Assign Homework
              </v-btn>
            </div>
          </div>

          <!-- Class Tabs: Gradebook Roster vs Assignments vs Analytics vs Noticeboard -->
          <v-tabs v-model="activeTab" color="primary" density="compact" class="mb-3">
            <v-tab value="gradebook" class="font-weight-black text-none" prepend-icon="mdi-table-account">
              Gradebook Roster ({{ filteredStudents.length }})
            </v-tab>
            <v-tab value="assignments" class="font-weight-black text-none" prepend-icon="mdi-clipboard-text-outline">
              Assignments ({{ gradebook.assignments?.length || 0 }})
            </v-tab>
            <v-tab value="analytics" class="font-weight-black text-none" prepend-icon="mdi-chart-box-outline">
              Analytics & Insights
            </v-tab>
            <v-tab value="noticeboard" class="font-weight-black text-none" prepend-icon="mdi-bullhorn-outline">
              Noticeboard ({{ announcements.length }})
            </v-tab>
          </v-tabs>

          <v-window v-model="activeTab">
            <!-- Tab 1: Gradebook Roster Table -->
            <v-window-item value="gradebook">
              <div class="mb-3 d-flex align-center justify-space-between flex-wrap ga-2">
                <v-text-field
                  v-model="searchStudentText"
                  placeholder="Search student name or email..."
                  variant="outlined"
                  density="compact"
                  hide-details
                  prepend-inner-icon="mdi-magnify"
                  style="max-width: 320px;"
                />
                <v-btn
                  color="success"
                  variant="flat"
                  size="small"
                  class="font-weight-black text-none"
                  prepend-icon="mdi-file-excel-outline"
                  @click="exportGradebookCSV"
                >
                  Export Gradebook (CSV)
                </v-btn>
              </div>

              <v-table density="comfortable" hover class="border rounded-lg">
                <thead>
                  <tr class="bg-grey-lighten-4">
                    <th class="font-weight-black text-caption text-secondary">STUDENT NAME</th>
                    <th class="font-weight-black text-caption text-secondary">EMAIL</th>
                    <th class="font-weight-black text-caption text-secondary text-center">SUBMISSIONS</th>
                    <th class="font-weight-black text-caption text-secondary text-center">AVG SCORE</th>
                    <th class="font-weight-black text-caption text-secondary text-center">ACTION</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="std in filteredStudents" :key="std.id">
                    <td class="font-weight-bold text-body-2">
                      <div class="d-flex align-center ga-2 pa-1">
                        <v-avatar color="indigo-lighten-5" size="28" class="text-indigo font-weight-black text-caption border">
                          {{ std.name.slice(0, 1).toUpperCase() }}
                        </v-avatar>
                        <span>{{ std.name }}</span>
                      </div>
                    </td>
                    <td class="text-caption text-grey">{{ std.email }}</td>
                    <td class="text-center font-weight-bold text-caption">
                      {{ getStudentSubmissions(std.id).length }}
                    </td>
                    <td class="text-center font-weight-black">
                      <v-chip
                        size="small"
                        :color="getStudentAvgScore(std.id) >= 8 ? 'success' : getStudentAvgScore(std.id) >= 6 ? 'info' : 'warning'"
                        variant="flat"
                        class="font-weight-black"
                      >
                        {{ getStudentAvgScore(std.id).toFixed(1) }}/10
                      </v-chip>
                    </td>
                    <td class="text-center">
                      <div class="d-flex align-center justify-center ga-1">
                        <v-btn
                          size="x-small"
                          color="primary"
                          variant="tonal"
                          class="font-weight-bold text-none"
                          prepend-icon="mdi-headphones"
                          :disabled="!getStudentSubmissions(std.id).length"
                          @click="openStudentSubmissionsModal(std)"
                        >
                          View Submissions
                        </v-btn>
                        <v-btn
                          size="x-small"
                          color="error"
                          variant="tonal"
                          icon="mdi-account-remove-outline"
                          title="Remove student from class"
                          @click="confirmRemoveStudent(std)"
                        />
                      </div>
                    </td>
                  </tr>

                  <tr v-if="!filteredStudents.length">
                    <td colspan="5" class="text-center pa-6 text-caption text-grey">
                      No students found. Share join code <strong>{{ selectedClass.join_code }}</strong> with your class!
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-window-item>

            <!-- Tab 2: Assignments List -->
            <v-window-item value="assignments">
              <div class="d-flex flex-column ga-2">
                <v-card
                  v-for="asg in gradebook.assignments"
                  :key="asg.id"
                  border
                  flat
                  class="pa-3 bg-grey-lighten-5 rounded-lg"
                >
                  <div class="d-flex align-center justify-space-between flex-wrap ga-2">
                    <div class="flex-grow-1">
                      <v-img v-if="asg.assignment_type === 'picture' && asg.image_url" :src="getMediaUrl(asg.image_url)"
                        width="280" height="180" contain class="rounded border mb-3 cursor-pointer"
                        @click="assignmentPreviewUrl = asg.image_url" />
                      <div class="d-flex align-center ga-2 flex-wrap">
                        <span class="text-subtitle-2 font-weight-black text-primary">{{ asg.title }}</span>
                        <v-chip
                          size="x-small"
                          :color="asg.assignment_type === 'picture' ? 'purple-darken-2' : 'indigo-darken-2'"
                          variant="tonal"
                          class="font-weight-bold"
                          :prepend-icon="asg.assignment_type === 'picture' ? 'mdi-image-filter-frames' : 'mdi-waveform'"
                        >
                          {{ asg.assignment_type === 'picture' ? 'Describe Picture' : 'Sentence Reading' }}
                        </v-chip>
                        <v-chip
                          size="x-small"
                          :color="asg.status === 'closed' ? 'grey-darken-1' : 'teal'"
                          variant="flat"
                          class="font-weight-bold"
                        >
                          {{ asg.status === 'closed' ? 'CLOSED' : 'ACTIVE' }}
                        </v-chip>
                        <v-chip v-if="asg.target_ipa" size="x-small" color="indigo" variant="tonal" class="font-weight-mono font-weight-bold">
                          {{ asg.target_ipa }}
                        </v-chip>
                      </div>
                      <div class="text-caption font-weight-bold text-grey-darken-3 font-italic mt-0.5" style="white-space: pre-wrap;">
                        "{{ asg.topic_sentence }}"
                      </div>
                      <div class="text-caption text-grey mt-1">
                        Due Date: {{ asg.due_date || 'No deadline' }} • Created: {{ asg.created_at }}
                      </div>
                    </div>

                    <div class="d-flex align-center flex-wrap ga-1">
                      <v-btn color="primary" variant="flat" size="small" prepend-icon="mdi-clipboard-text-search" @click="openAssignmentReview(asg)">Review Submissions</v-btn>
                      <v-chip @click="openAssignmentReview(asg)" color="teal" size="small" variant="flat" class="font-weight-bold mr-1">
                        Submissions: {{ getAssignmentSubmissionsCount(asg.id) }}/{{ gradebook.students?.length || 0 }}
                      </v-chip>
                      <v-btn
                        size="x-small"
                        icon="mdi-bell-ring-outline"
                        color="amber-darken-3"
                        variant="tonal"
                        title="Remind Non-Submitters"
                        @click="openRemindModal(asg)"
                      />
                      <v-btn
                        size="x-small"
                        icon="mdi-content-copy"
                        color="teal"
                        variant="tonal"
                        title="Duplicate Assignment"
                        @click="openDuplicateModal(asg)"
                      />
                      <v-btn
                        size="x-small"
                        icon="mdi-clock-fast"
                        color="indigo"
                        variant="tonal"
                        title="Re-open / Extend Deadline"
                        @click="openReopenModal(asg)"
                      />
                      <v-btn
                        size="x-small"
                        icon="mdi-pencil-outline"
                        color="primary"
                        variant="tonal"
                        title="Edit Assignment"
                        @click="openEditAssignmentModal(asg)"
                      />
                      <v-btn
                        size="x-small"
                        icon="mdi-delete-outline"
                        color="error"
                        variant="tonal"
                        title="Delete Assignment"
                        @click="confirmDeleteAssignment(asg)"
                      />
                    </div>
                  </div>
                </v-card>

                <div v-if="!gradebook.assignments?.length" class="text-center pa-6 text-caption text-grey border rounded-lg">
                  No assignments posted for this class yet. Click "Assign Homework" above!
                </div>
              </div>
            </v-window-item>

            <!-- Tab 3: Class Analytics & Pronunciation Insights -->
            <v-window-item value="analytics">
              <div v-if="isFetchingAnalytics" class="text-center pa-8">
                <v-progress-circular indeterminate color="primary" />
                <div class="text-caption font-weight-bold text-grey mt-2">Computing class pronunciation analytics...</div>
              </div>

              <div v-else-if="analyticsData" class="d-flex flex-column ga-3">
                <!-- KPI Stat Cards Row -->
                <v-row dense>
                  <v-col cols="12" sm="6" md="3">
                    <div class="pa-3 border rounded-lg bg-indigo-lighten-5">
                      <div class="text-caption font-weight-bold text-indigo-darken-3">COMPLETION RATE</div>
                      <div class="text-h5 font-weight-black text-indigo-darken-4 mt-1">
                        {{ analyticsData.summary?.completion_rate || 0 }}%
                      </div>
                      <div class="text-caption text-grey-darken-1 mt-0.5">
                        {{ analyticsData.summary?.total_submissions || 0 }} total audio recordings
                      </div>
                    </div>
                  </v-col>

                  <v-col cols="12" sm="6" md="3">
                    <div class="pa-3 border rounded-lg bg-teal-lighten-5">
                      <div class="text-caption font-weight-bold text-teal-darken-3">CLASS AVERAGE SCORE</div>
                      <div class="text-h5 font-weight-black text-teal-darken-4 mt-1">
                        {{ (analyticsData.summary?.class_avg_score || 0).toFixed(1) }}/10
                      </div>
                      <div class="text-caption text-grey-darken-1 mt-0.5">
                        Across {{ analyticsData.summary?.total_assignments || 0 }} active assignments
                      </div>
                    </div>
                  </v-col>

                  <v-col cols="12" sm="6" md="3">
                    <div class="pa-3 border rounded-lg bg-amber-lighten-5">
                      <div class="text-caption font-weight-bold text-amber-darken-4">AT-RISK STUDENTS</div>
                      <div class="text-h5 font-weight-black text-amber-darken-4 mt-1">
                        {{ analyticsData.summary?.at_risk_count || 0 }}
                      </div>
                      <div class="text-caption text-grey-darken-1 mt-0.5">
                        Missing >= 2 or score &lt; 6.0
                      </div>
                    </div>
                  </v-col>

                  <v-col cols="12" sm="6" md="3">
                    <div class="pa-3 border rounded-lg bg-purple-lighten-5">
                      <div class="text-caption font-weight-bold text-purple-darken-3">COHORT SIZE</div>
                      <div class="text-h5 font-weight-black text-purple-darken-4 mt-1">
                        {{ analyticsData.summary?.total_students || 0 }}
                      </div>
                      <div class="text-caption text-grey-darken-1 mt-0.5">
                        Enrolled learners in class
                      </div>
                    </div>
                  </v-col>
                </v-row>

                <!-- Weak Phonemes Diagnostic Breakdown Section -->
                <div class="border rounded-lg pa-3 bg-white">
                  <div class="d-flex align-center justify-space-between mb-2">
                    <div>
                      <div class="text-subtitle-2 font-weight-black text-secondary d-flex align-center ga-1">
                        <v-icon size="small" color="secondary">mdi-waveform</v-icon>
                        <span>PRONUNCIATION TROUBLE SPOTS (TOP WEAK PHONEMES)</span>
                      </div>
                      <div class="text-caption text-grey">
                        Aggregated friction points identified from student audio transcription and phonetic error logs.
                      </div>
                    </div>
                    <v-chip color="indigo" size="small" variant="tonal" class="font-weight-bold">
                      Diagnostic Insights
                    </v-chip>
                  </div>

                  <v-row dense>
                    <v-col v-for="ph in analyticsData.weak_phonemes" :key="ph.phoneme" cols="12" sm="6" md="4">
                      <div class="pa-3 border rounded-lg bg-grey-lighten-5 h-100 d-flex flex-column justify-space-between">
                        <div>
                          <div class="d-flex align-center justify-space-between mb-1">
                            <span class="text-h6 font-weight-black text-primary font-mono">{{ ph.phoneme }}</span>
                            <v-chip size="x-small" :color="ph.error_count > 5 ? 'error' : 'warning'" variant="flat" class="font-weight-bold">
                              {{ ph.error_count }} Errors
                            </v-chip>
                          </div>
                          <div class="text-caption font-weight-bold text-grey-darken-3">{{ ph.name }}</div>
                          <div class="d-flex align-center ga-1 flex-wrap my-1.5">
                            <span class="text-caption text-grey font-weight-bold">Focus:</span>
                            <v-chip v-for="w in ph.example_words" :key="w" size="x-small" variant="tonal" color="grey-darken-3" class="font-weight-bold">
                              {{ w }}
                            </v-chip>
                          </div>
                        </div>
                        <div class="text-caption text-indigo-darken-3 font-weight-medium border-t pt-1 mt-1 bg-white pa-1.5 rounded">
                          💡 <em>Tip:</em> {{ ph.tip }}
                        </div>
                      </div>
                    </v-col>
                  </v-row>
                </div>

                <!-- At-Risk Students Action Table -->
                <div class="border rounded-lg pa-3 bg-white">
                  <div class="text-subtitle-2 font-weight-black text-error d-flex align-center ga-1 mb-2">
                    <v-icon size="small" color="error">mdi-alert-circle</v-icon>
                    <span>STUDENTS REQUIRING PEDAGOGICAL SUPPORT ({{ analyticsData.at_risk_students?.length || 0 }})</span>
                  </div>

                  <v-table density="compact" class="border rounded-lg">
                    <thead>
                      <tr class="bg-grey-lighten-4">
                        <th class="font-weight-black text-caption text-secondary">STUDENT</th>
                        <th class="font-weight-black text-caption text-secondary text-center">MISSING ASSIGNMENTS</th>
                        <th class="font-weight-black text-caption text-secondary text-center">AVERAGE SCORE</th>
                        <th class="font-weight-black text-caption text-secondary text-center">RISK LEVEL</th>
                        <th class="font-weight-black text-caption text-secondary">DIAGNOSTIC REASON</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="st in analyticsData.at_risk_students" :key="st.id">
                        <td class="font-weight-bold text-body-2">
                          <div>{{ st.name }}</div>
                          <div class="text-caption text-grey font-weight-regular">{{ st.email }}</div>
                        </td>
                        <td class="text-center font-weight-black text-error">
                          {{ st.missing_count }}
                        </td>
                        <td class="text-center font-weight-black">
                          {{ st.submitted_count > 0 ? (st.avg_score.toFixed(1) + '/10') : 'No Submissions' }}
                        </td>
                        <td class="text-center">
                          <v-chip size="x-small" :color="st.risk_level === 'HIGH' ? 'error' : 'warning'" variant="flat" class="font-weight-bold">
                            {{ st.risk_level }}
                          </v-chip>
                        </td>
                        <td class="text-caption text-grey-darken-2">
                          {{ st.reasons?.join(', ') || 'Needs attention' }}
                        </td>
                      </tr>
                      <tr v-if="!analyticsData.at_risk_students?.length">
                        <td colspan="5" class="text-center pa-4 text-caption text-success font-weight-bold">
                          🎉 Excellent! All learners in this class are actively completing homework with strong progress.
                        </td>
                      </tr>
                    </tbody>
                  </v-table>
                </div>
              </div>
            </v-window-item>

            <!-- Tab 4: Class Noticeboard -->
            <v-window-item value="noticeboard">
              <div class="d-flex align-center justify-space-between mb-3">
                <div>
                  <div class="text-subtitle-2 font-weight-black text-secondary">CLASS NOTICEBOARD & ANNOUNCEMENTS</div>
                  <div class="text-caption text-grey">Broadcast homework instructions, schedule updates, and reminders to all students.</div>
                </div>
                <v-btn
                  color="primary"
                  variant="flat"
                  size="small"
                  class="font-weight-black text-none"
                  prepend-icon="mdi-plus"
                  @click="showPostAnnouncementModal = true"
                >
                  Post Notice
                </v-btn>
              </div>

              <div class="d-flex flex-column ga-2">
                <v-card
                  v-for="ann in announcements"
                  :key="ann.id"
                  border
                  flat
                  class="pa-3 rounded-lg"
                  :class="ann.announcement_type === 'urgent' ? 'bg-red-lighten-5 border-error' : (ann.announcement_type === 'reminder' ? 'bg-amber-lighten-5' : 'bg-grey-lighten-5')"
                >
                  <div class="d-flex align-center justify-space-between flex-wrap ga-2">
                    <div class="d-flex align-center ga-2 flex-wrap">
                      <span class="text-subtitle-2 font-weight-black text-grey-darken-4">{{ ann.title }}</span>
                      <v-chip
                        size="x-small"
                        :color="ann.announcement_type === 'urgent' ? 'error' : (ann.announcement_type === 'reminder' ? 'amber-darken-4' : 'primary')"
                        variant="flat"
                        class="font-weight-bold uppercase"
                      >
                        {{ (ann.announcement_type || 'general').toUpperCase() }}
                      </v-chip>
                    </div>

                    <div class="d-flex align-center ga-2">
                      <span class="text-caption text-grey">{{ ann.created_at }}</span>
                      <v-btn
                        size="x-small"
                        icon="mdi-delete-outline"
                        color="error"
                        variant="text"
                        title="Delete Announcement"
                        @click="confirmDeleteAnnouncement(ann)"
                      />
                    </div>
                  </div>

                  <div class="text-body-2 text-grey-darken-3 mt-1" style="white-space: pre-wrap;">
                    {{ ann.content }}
                  </div>

                  <div class="text-caption text-grey mt-2 d-flex align-center ga-1">
                    <v-icon size="x-small">mdi-account-tie</v-icon>
                    <span>Posted by {{ ann.teacher_name || 'Teacher Lead' }}</span>
                  </div>
                </v-card>

                <div v-if="!announcements.length" class="text-center pa-6 text-caption text-grey border rounded-lg bg-white">
                  No announcements posted on the noticeboard yet. Click "Post Notice" above to send an update!
                </div>
              </div>
            </v-window-item>
          </v-window>
        </v-card>

        <!-- Empty State Select Class -->
        <v-card v-else border flat class="pa-8 text-center bg-white rounded-lg">
          <v-icon size="64" color="grey-lighten-1">mdi-school-outline</v-icon>
          <div class="text-subtitle-1 font-weight-bold text-grey mt-2">Select a class from the left menu to view gradebook</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Modal: Create New Class -->
    <v-dialog v-model="showCreateClassModal" max-width="450">
      <v-card border rounded="lg" class="pa-4">
        <div class="text-subtitle-1 font-weight-black text-primary mb-3 d-flex align-center ga-2">
          <v-icon color="primary">mdi-plus-box</v-icon>
          <span>Create New Classroom</span>
        </div>

        <v-text-field
          v-model="newClassName"
          label="Classroom Name:"
          placeholder="Example: Class 5A - Morning"
          variant="outlined"
          density="comfortable"
          class="mb-2"
          prepend-inner-icon="mdi-school"
        />

        <v-select
          v-model="newClassGrade"
          :items="classGradeOptions"
          label="Grade Level Category:"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          prepend-inner-icon="mdi-notebook"
        />

        <!-- Freelance Quota Warning in Create Class -->
        <v-alert
          v-if="teacherQuota && teacherQuota.teacher_type === 'freelance' && teacherQuota.used_classes >= teacherQuota.max_classes"
          type="warning"
          variant="tonal"
          density="compact"
          class="mb-3 text-caption font-weight-bold"
        >
          Class limit reached ({{ teacherQuota.used_classes }}/{{ teacherQuota.max_classes }} active classes). Please archive an unused classroom or upgrade your plan.
        </v-alert>
        <v-alert
          v-else-if="teacherQuota && teacherQuota.teacher_type === 'freelance' && teacherQuota.is_expired"
          type="error"
          variant="tonal"
          density="compact"
          class="mb-3 text-caption font-weight-bold"
        >
          Educator plan expired on {{ teacherQuota.license_expiry }}. Please renew your plan.
        </v-alert>

        <v-card-actions class="px-0 pb-0">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showCreateClassModal = false">Cancel</v-btn>
          <v-btn
            color="primary"
            variant="flat"
            class="text-none font-weight-bold"
            :loading="isCreatingClass"
            :disabled="Boolean(teacherQuota && teacherQuota.teacher_type === 'freelance' && (teacherQuota.used_classes >= teacherQuota.max_classes || teacherQuota.is_expired))"
            @click="submitCreateClass"
          >
            Generate Class & Join Code
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Modal: Plan Details & Upgrade Support -->
    <v-dialog v-model="showPlanDetailsModal" max-width="480">
      <v-card border rounded="lg" class="pa-5 bg-white">
        <div class="text-center mb-4">
          <v-avatar color="indigo-lighten-5" size="56" class="text-indigo-darken-3 mb-2 elevation-1">
            <v-icon size="28">mdi-account-star</v-icon>
          </v-avatar>
          <div class="text-h6 font-weight-black text-indigo-darken-4">Independent Educator Plan</div>
          <div class="text-caption text-grey-darken-1">Manage your solo educator subscription & quota</div>
        </div>

        <v-list density="compact" class="border rounded-lg mb-4 pa-2 bg-grey-lighten-5">
          <v-list-item>
            <template #prepend><v-icon color="indigo">mdi-seat-passenger</v-icon></template>
            <v-list-item-title class="font-weight-bold text-caption">Student License Seats</v-list-item-title>
            <template #append>
              <span class="text-caption font-weight-black text-indigo-darken-3">{{ teacherQuota?.used_seats }} / {{ teacherQuota?.max_seats }} Used</span>
            </template>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <template #prepend><v-icon color="teal">mdi-google-classroom</v-icon></template>
            <v-list-item-title class="font-weight-bold text-caption">Active Classrooms</v-list-item-title>
            <template #append>
              <span class="text-caption font-weight-black text-teal-darken-3">{{ teacherQuota?.used_classes }} / {{ teacherQuota?.max_classes }} Classes</span>
            </template>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <template #prepend><v-icon color="amber-darken-3">mdi-calendar-clock</v-icon></template>
            <v-list-item-title class="font-weight-bold text-caption">Expiration Date</v-list-item-title>
            <template #append>
              <span class="text-caption font-weight-bold">{{ teacherQuota?.license_expiry }}</span>
            </template>
          </v-list-item>
        </v-list>

        <v-alert type="info" variant="tonal" density="compact" class="text-caption mb-4">
          Need more student seats or additional classrooms? Contact Platform Administration to upgrade your educator plan.
        </v-alert>

        <div class="bg-indigo-lighten-5 pa-3 rounded-lg border border-indigo-lighten-4 mb-4">
          <div class="text-caption font-weight-bold text-indigo-darken-4 mb-1">Direct Platform Support:</div>
          <div class="text-caption text-grey-darken-3 font-weight-medium">📧 Email: <strong>support@fluent.edu.vn</strong></div>
          <div class="text-caption text-grey-darken-3 font-weight-medium">📞 Hotline / Zalo: <strong>+84 901 888 999</strong></div>
        </div>

        <v-card-actions class="px-0 pb-0">
          <v-spacer />
          <v-btn color="indigo-darken-3" variant="flat" class="text-none font-weight-bold" block @click="showPlanDetailsModal = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Modal: Edit Classroom -->
    <v-dialog v-model="showEditClassModal" max-width="450">
      <v-card border rounded="lg" class="pa-4">
        <div class="text-subtitle-1 font-weight-black text-primary mb-3 d-flex align-center ga-2">
          <v-icon color="primary">mdi-pencil</v-icon>
          <span>Update Classroom Details</span>
        </div>

        <v-text-field
          v-model="editClassName"
          label="Classroom Name:"
          variant="outlined"
          density="comfortable"
          class="mb-2"
          prepend-inner-icon="mdi-school"
        />

        <v-select
          v-model="editClassGrade"
          :items="classGradeOptions"
          label="Grade Level Category:"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          prepend-inner-icon="mdi-notebook"
        />

        <v-card-actions class="px-0 pb-0">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showEditClassModal = false">Cancel</v-btn>
          <v-btn color="primary" variant="flat" class="text-none font-weight-bold" :loading="isUpdatingClass" @click="submitEditClass">
            Save Changes
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Modal: Delete Classroom Confirmation -->
    <v-dialog v-model="showDeleteClassModal" max-width="400">
      <v-card border rounded="lg" class="pa-4">
        <div class="text-subtitle-1 font-weight-black text-error mb-2 d-flex align-center ga-2">
          <v-icon color="error">mdi-alert-circle</v-icon>
          <span>Delete Classroom</span>
        </div>
        <div class="text-body-2 text-grey-darken-2 mb-4">
          Are you sure you want to delete classroom <strong>{{ selectedClass?.name }}</strong>? Students will no longer be able to submit homework to this class.
        </div>
        <v-card-actions class="px-0 pb-0">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showDeleteClassModal = false">Cancel</v-btn>
          <v-btn color="error" variant="flat" class="text-none font-weight-bold" :loading="isDeletingClass" @click="submitDeleteClass">
            Delete Classroom
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Modal: Remove Student Confirmation -->
    <v-dialog v-model="showRemoveStudentModal" max-width="400">
      <v-card border rounded="lg" class="pa-4">
        <div class="text-subtitle-1 font-weight-black text-error mb-2 d-flex align-center ga-2">
          <v-icon color="error">mdi-account-remove</v-icon>
          <span>Remove Student</span>
        </div>
        <div class="text-body-2 text-grey-darken-2 mb-4">
          Remove student <strong>{{ studentToRemove?.name }}</strong> from classroom <strong>{{ selectedClass?.name }}</strong>?
        </div>
        <v-card-actions class="px-0 pb-0">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showRemoveStudentModal = false">Cancel</v-btn>
          <v-btn color="error" variant="flat" class="text-none font-weight-bold" :loading="isRemovingStudent" @click="submitRemoveStudent">
            Remove Student
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Modal: Edit Assignment -->
    <v-dialog v-model="showEditAssignmentModal" :max-width="editingAsg?.assignment_type === 'picture' ? 1100 : 760">
      <v-card border rounded="lg" class="pa-4 bg-white">
        <div class="text-subtitle-1 font-weight-black text-primary mb-3 d-flex align-center ga-2">
          <v-icon color="primary">mdi-pencil</v-icon>
          <span>Edit Homework Assignment</span>
          <v-chip v-if="editingAsg?.assignment_type === 'picture'" size="x-small" color="purple" variant="tonal" class="ml-auto font-weight-bold">
            Describe Picture
          </v-chip>
        </div>

        <v-text-field
          v-model="editAsgTitle"
          label="Assignment Title:"
          variant="outlined"
          density="comfortable"
          class="mb-2"
          prepend-inner-icon="mdi-format-title"
        />

        <!-- If Sentence Assignment -->
        <v-textarea
          v-if="editingAsg?.assignment_type !== 'picture'"
          v-model="editAsgSentence"
          label="Model Reading Sentence:"
          variant="outlined"
          density="comfortable"
          rows="3"
          class="mb-2"
          prepend-inner-icon="mdi-subtitles"
        />

        <!-- If Picture Speaking Assignment -->
        <div v-else class="mb-3">
          <v-text-field
            v-model="editAsgSentence"
            label="Speaking Topic / Task Prompt:"
            variant="outlined"
            density="comfortable"
            class="mb-2"
            prepend-inner-icon="mdi-image-filter-frames"
          />

          <!-- Picture & Settings Preview -->
          <div class="d-flex ga-3 align-center mb-3 pa-2 bg-grey-lighten-5 rounded border">
            <v-img
              v-if="editAsgImageUrl"
              :src="getMediaUrl(editAsgImageUrl)"
              height="90"
              width="140"
              cover
              class="rounded border bg-white flex-shrink-0"
            />
            <div class="flex-grow-1">
              <v-text-field
                v-model="editAsgImageUrl"
                label="Image URL:"
                variant="outlined"
                density="compact"
                hide-details
                class="mb-2 bg-white text-caption"
              />
              <p class="text-caption text-grey">Students stop the recording when they have finished.</p>
            </div>
          </div>

          <!-- Guiding Questions Editor -->
          <div class="mb-3">
            <div class="d-flex align-center justify-space-between mb-2">
              <span class="text-caption font-weight-bold text-purple-darken-3 d-flex align-center ga-1">
                <v-icon size="small" color="purple-darken-3">mdi-help-box-multiple</v-icon>
                <span>Guiding Questions (Students will answer these):</span>
              </span>
              <v-btn
                size="x-small"
                variant="tonal"
                color="purple-darken-2"
                prepend-icon="mdi-plus"
                class="text-none font-weight-bold"
                @click="addEditAsgQuestion"
              >
                Add Question
              </v-btn>
            </div>

            <div v-for="(q, idx) in editAsgGuidingQuestionsList" :key="idx" class="d-flex align-center ga-2 mb-2">
              <v-chip size="small" color="purple-darken-2" variant="flat" class="font-weight-bold flex-shrink-0" style="min-width: 42px; justify-content: center;">
                Q{{ idx + 1 }}
              </v-chip>
              <v-text-field
                v-model="editAsgGuidingQuestionsList[idx]"
                placeholder="Enter guiding question for students..."
                variant="outlined"
                density="compact"
                hide-details
                class="flex-grow-1 bg-white text-body-2"
              />
              <v-btn
                icon="mdi-trash-can-outline"
                size="x-small"
                color="error"
                variant="text"
                title="Delete Question"
                :disabled="editAsgGuidingQuestionsList.length <= 1"
                @click="removeEditAsgQuestion(idx)"
              />
            </div>
          </div>

          <!-- Target Keywords -->
          <v-text-field
            v-model="editAsgTargetKeywordsText"
            label="Target Keywords (comma-separated):"
            variant="outlined"
            density="compact"
            hide-details
            class="bg-white text-caption"
            prepend-inner-icon="mdi-tag-multiple-outline"
          />
        </div>

        <v-text-field
          v-model="editAsgDueDate"
          type="date"
          label="Due Date (Optional):"
          placeholder="Example: 2026-08-05"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          prepend-inner-icon="mdi-calendar-clock"
        />

        <v-card-actions class="px-0 pb-0">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showEditAssignmentModal = false">Cancel</v-btn>
          <v-btn color="primary" variant="flat" class="text-none font-weight-bold" :loading="isUpdatingAsg" @click="submitEditAssignment">
            Save Assignment
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Modal: Delete Assignment Confirmation -->
    <v-dialog v-model="showDeleteAssignmentModal" max-width="400">
      <v-card border rounded="lg" class="pa-4">
        <div class="text-subtitle-1 font-weight-black text-error mb-2 d-flex align-center ga-2">
          <v-icon color="error">mdi-delete</v-icon>
          <span>Delete Assignment</span>
        </div>
        <div class="text-body-2 text-grey-darken-2 mb-4">
          Are you sure you want to delete assignment <strong>"{{ asgToDelete?.title }}"</strong>?
        </div>
        <v-card-actions class="px-0 pb-0">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showDeleteAssignmentModal = false">Cancel</v-btn>
          <v-btn color="error" variant="flat" class="text-none font-weight-bold" :loading="isDeletingAsg" @click="submitDeleteAssignment">
            Delete Assignment
          </v-btn>
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
            <div class="text-caption text-grey-darken-1">Are you sure you want to sign out from Teacher Hub?</div>
          </div>
        </div>
        <v-card-actions class="px-0 pb-0">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showLogoutDialog = false">Cancel</v-btn>
          <v-btn color="error" variant="flat" class="text-none font-weight-bold" prepend-icon="mdi-logout" @click="confirmSignOut">
            Sign Out
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog :model-value="Boolean(assignmentPreviewUrl)" max-width="1100" @update:model-value="assignmentPreviewUrl = ''">
      <v-card class="pa-3">
        <v-btn icon="mdi-close" variant="text" class="align-self-end" @click="assignmentPreviewUrl = ''" />
        <v-img :src="getMediaUrl(assignmentPreviewUrl)" max-height="80vh" contain />
      </v-card>
    </v-dialog>
    <!-- Modal: 1-Click Assignment Creation with AI Picture Speaking & Sentence -->
    <v-dialog v-model="showCreateAssignmentModal" :max-width="newAsgType === 'picture' ? 1100 : 760">
      <v-card border rounded="lg" class="pa-4 bg-white">
        <div class="d-flex align-center justify-space-between mb-3 border-b pb-2">
          <div class="d-flex align-center ga-2">
            <v-avatar color="purple-lighten-5" size="36">
              <v-icon color="purple-darken-3">mdi-send</v-icon>
            </v-avatar>
            <div class="text-subtitle-1 font-weight-black text-secondary">
              Assign Homework to {{ selectedClass?.name }}
            </div>
          </div>
          <v-btn icon="mdi-close" variant="text" size="small" @click="showCreateAssignmentModal = false" />
        </div>

        <!-- Format Switcher -->
        <div class="mb-3">
          <div class="text-caption font-weight-bold text-grey mb-1">Homework Format:</div>
          <v-btn-toggle v-model="newAsgType" mandatory color="purple-darken-2" density="comfortable" class="w-100 border">
            <v-btn value="sentence" class="flex-grow-1 text-none font-weight-bold" prepend-icon="mdi-waveform">
              Sentence Reading
            </v-btn>
            <v-btn value="picture" class="flex-grow-1 text-none font-weight-bold" prepend-icon="mdi-image-filter-frames">
              {{ isMyHanh ? 'Describe Picture' : 'Describe Picture (IELTS/TOEIC)' }}
            </v-btn>
          </v-btn-toggle>
        </div>

        <!-- Common: Assignment Title -->
        <v-text-field
          v-model="newAsgTitle"
          label="Assignment Title:"
          :placeholder="newAsgType === 'picture' ? (isMyHanh ? 'e.g. A Morning at School' : 'e.g. IELTS Speaking Part 2 - Modern Airport') : 'e.g. Unit 3 - Practice Daily Routine Sentence'"
          variant="outlined"
          density="comfortable"
          class="mb-2"
          prepend-inner-icon="mdi-format-title"
        />

        <!-- Branch 1: Sentence Reading -->
        <div v-if="newAsgType === 'sentence'">
          <v-textarea
            v-model="newAsgSentence"
            label="Model Reading Sentence:"
            :placeholder="isMyHanh ? 'Example: I like cats and dogs.' : 'Example: Learning a new language opens up a world of opportunities.'"
            variant="outlined"
            density="comfortable"
            rows="3"
            class="mb-2"
            prepend-inner-icon="mdi-subtitles"
          />
        </div>

        <!-- Branch 2: Picture Speaking with AI Generator -->
        <div v-else>
          <div class="mb-2">
            <div class="d-flex align-center justify-space-between mb-2">
              <span class="text-caption font-weight-bold text-grey">Creation Method:</span>
              <v-btn-toggle v-model="teacherPictureMode" mandatory color="purple-darken-2" density="compact" class="border">
                <v-btn value="ai_gen" size="x-small" class="text-none font-weight-bold" prepend-icon="mdi-sparkles">AI Prompt</v-btn>
                <v-btn value="upload" size="x-small" class="text-none font-weight-bold" prepend-icon="mdi-upload">Upload Image</v-btn>
              </v-btn-toggle>
            </div>

            <!-- Mode 1: AI Prompt Generator -->
            <div v-if="teacherPictureMode === 'ai_gen'">
              <div class="d-flex align-center justify-space-between mb-1">
                <span class="text-caption font-weight-bold text-grey">Topic or Speaking Theme:</span>
                <v-btn
                  color="purple-darken-2"
                  variant="flat"
                  size="x-small"
                  class="text-none font-weight-bold"
                  prepend-icon="mdi-sparkles"
                  :loading="isGeneratingAsgPicture"
                  @click="generateAIPictureScenario"
                >
                  Generate Scene & Questions
                </v-btn>
              </div>
              <v-text-field
                v-model="newAsgPictureTopic"
                :placeholder="isMyHanh ? 'e.g. My Classroom, Family Picnic, Playground' : 'e.g. Hospital Emergency Hallway, Airport Lounge, Tech Office'"
                variant="outlined"
                density="comfortable"
                class="mb-2"
                prepend-inner-icon="mdi-image-search-outline"
              />
            </div>

            <!-- Mode 2: Upload Custom Exam Image -->
            <div v-else class="mb-2">
              <input
                ref="teacherFileInputRef"
                type="file"
                accept="image/*"
                class="d-none"
                @change="handleTeacherUploadImageChange"
              />
              <div class="border-dashed rounded pa-3 text-center bg-grey-lighten-5 cursor-pointer mb-2" @click="$refs.teacherFileInputRef?.click()">
                <v-icon color="purple-darken-2" size="default">mdi-cloud-upload</v-icon>
                <div class="text-caption font-weight-bold text-grey-darken-3">Click to upload exam or textbook picture</div>
                <div class="text-caption text-grey" style="font-size: 11px;">Supports JPG, PNG, WEBP</div>
              </div>
              <v-text-field
                v-model="newAsgPictureTopic"
                :placeholder="isMyHanh ? 'Optional Topic (e.g. My Classroom)' : 'Optional Topic / Exam Context (e.g. Cambridge PET Exam Picture)'"
                variant="outlined"
                density="compact"
                class="mb-2"
              />
            </div>
          </div>

          <!-- Quick Topic Idea Chips for Teachers -->
          <div class="mb-3">
            <div class="text-caption font-weight-bold text-grey mb-1">Suggested Curricular Themes:</div>
            <div class="d-flex flex-wrap ga-1">
              <v-chip
                v-for="theme in teacherTopicIdeas"
                :key="theme"
                size="x-small"
                variant="tonal"
                color="purple-darken-2"
                class="cursor-pointer font-weight-bold"
                @click="selectTeacherTopicIdea(theme)"
              >
                {{ theme }}
              </v-chip>
            </div>
          </div>

          <!-- Scenario Preview & Guiding Questions Editor -->
          <div v-if="newAsgImageUrl" class="pa-3 border rounded-lg bg-grey-lighten-5 mb-3">
            <div class="d-flex align-center justify-space-between mb-2">
              <span class="text-caption font-weight-black text-purple-darken-3 d-flex align-center ga-1">
                <v-icon size="x-small" color="purple-darken-3">mdi-check-circle</v-icon>
                <span>GENERATED SCENARIO & QUESTION EDITOR</span>
              </span>
              <span class="text-caption text-grey">Student-controlled recording</span>
            </div>

            <!-- Helpful Guidance Banner for Lecturer -->
            <div class="d-flex align-center ga-2 pa-2 mb-3 rounded bg-purple-lighten-5 border border-purple-lighten-4">
              <v-icon color="purple-darken-2" size="small">mdi-lightbulb-on-outline</v-icon>
              <div class="text-caption text-purple-darken-4 font-weight-medium" style="line-height: 1.3;">
                Review and customize the AI-generated questions below before assigning. You can edit wording, remove questions, or add custom ones.
              </div>
            </div>

            <div class="d-flex ga-3 flex-column flex-sm-row mb-3">
              <div class="flex-shrink-0 text-center">
                <v-img
                  :src="getMediaUrl(newAsgImageUrl)"
                  height="240"
                  width="360"
                  style="max-width: 100%;"
                  cover
                  class="rounded border bg-white mx-auto"
                />
                <v-btn
                  size="x-small"
                  variant="text"
                  color="purple-darken-2"
                  prepend-icon="mdi-refresh"
                  class="text-none mt-1"
                  :loading="isGeneratingAsgPicture"
                  @click="generateAIPictureScenario"
                >
                  Regenerate
                </v-btn>
              </div>

              <!-- Question Mode & Editor -->
              <div class="flex-grow-1">
                <div class="d-flex align-center justify-space-between mb-2">
                  <span class="text-caption font-weight-bold text-grey-darken-3">
                    Guiding Questions ({{ newAsgGuidingQuestionsList.length }}):
                  </span>
                  <div class="d-flex align-center ga-1">
                    <v-btn
                      size="x-small"
                      :variant="newAsgQuestionsMode === 'list' ? 'flat' : 'text'"
                      :color="newAsgQuestionsMode === 'list' ? 'purple-darken-2' : 'grey'"
                      class="text-none font-weight-bold"
                      @click="newAsgQuestionsMode = 'list'"
                    >
                      Question List
                    </v-btn>
                    <v-btn
                      size="x-small"
                      :variant="newAsgQuestionsMode === 'bulk' ? 'flat' : 'text'"
                      :color="newAsgQuestionsMode === 'bulk' ? 'purple-darken-2' : 'grey'"
                      class="text-none font-weight-bold"
                      @click="syncNewAsgQuestionsToText(); newAsgQuestionsMode = 'bulk'"
                    >
                      Bulk Text
                    </v-btn>
                  </div>
                </div>

                <!-- Mode A: Interactive List with Individual Inputs -->
                <div v-if="newAsgQuestionsMode === 'list'">
                  <div
                    v-for="(q, idx) in newAsgGuidingQuestionsList"
                    :key="idx"
                    class="d-flex align-center ga-1 mb-2"
                  >
                    <v-chip
                      size="small"
                      color="purple-darken-2"
                      variant="flat"
                      class="font-weight-bold flex-shrink-0"
                      style="min-width: 38px; justify-content: center;"
                    >
                      Q{{ idx + 1 }}
                    </v-chip>
                    <v-text-field
                      v-model="newAsgGuidingQuestionsList[idx]"
                      placeholder="Enter question for students..."
                      variant="outlined"
                      density="compact"
                      hide-details
                      class="flex-grow-1 bg-white text-caption"
                      @input="syncNewAsgQuestionsToText"
                    />
                    <v-btn
                      icon="mdi-trash-can-outline"
                      size="x-small"
                      color="error"
                      variant="text"
                      title="Delete Question"
                      :disabled="newAsgGuidingQuestionsList.length <= 1"
                      @click="removeNewAsgQuestion(idx)"
                    />
                  </div>

                  <v-btn
                    size="x-small"
                    variant="tonal"
                    color="purple-darken-2"
                    prepend-icon="mdi-plus"
                    class="text-none font-weight-bold mt-1"
                    @click="addNewAsgQuestion"
                  >
                    Add Question
                  </v-btn>
                </div>

                <!-- Mode B: Bulk Text (1 per line) -->
                <div v-else>
                  <v-textarea
                    v-model="newAsgGuidingQuestionsText"
                    label="Questions (1 per line):"
                    rows="4"
                    variant="outlined"
                    density="compact"
                    class="mb-1 text-caption bg-white"
                    hide-details
                    @input="syncNewAsgQuestionsFromText"
                  />
                </div>
              </div>
            </div>

            <!-- Target Keywords -->
            <v-text-field
              v-model="newAsgTargetKeywordsText"
              label="Target Keywords / Collocations (comma-separated):"
              :placeholder="isMyHanh ? 'e.g. cat, dog, tree, school' : 'e.g. airport terminal, flight departure, travelers, boarding gate'"
              variant="outlined"
              density="compact"
              hide-details
              class="bg-white text-caption"
              prepend-inner-icon="mdi-tag-multiple-outline"
            />
          </div>
        </div>

        <v-text-field
          v-model="newAsgDueDate"
          type="date"
          label="Due Date (Optional):"
          placeholder="Example: 2026-10-30"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          prepend-inner-icon="mdi-calendar-clock"
        />

        <v-card-actions class="px-0 pb-0 border-t pt-2">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showCreateAssignmentModal = false">Cancel</v-btn>
          <v-btn color="secondary" variant="flat" class="text-none font-weight-bold" :loading="isCreatingAsg" :disabled="isGeneratingAsgPicture || (newAsgType === 'picture' && !newAsgImageUrl)" @click="submitCreateAssignment">
            Assign Homework
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Modal: Review Student Audio Submissions from Supabase -->
    <v-dialog v-model="showSubmissionsModal" max-width="1000">
      <v-card v-if="selectedStudent" border rounded="lg" class="pa-4">
        <div class="d-flex align-center justify-space-between mb-3 border-b pb-2">
          <div class="d-flex align-center ga-2">
            <v-avatar color="indigo-lighten-5" size="36" class="text-indigo border font-weight-black">
              {{ selectedStudent.name.slice(0, 1).toUpperCase() }}
            </v-avatar>
            <div>
              <div class="text-subtitle-1 font-weight-black text-primary">{{ selectedStudent.name }}'s Submissions</div>
              <div class="text-caption text-grey">{{ selectedStudent.email }}</div>
            </div>
          </div>
          <v-btn icon="mdi-close" variant="text" density="compact" @click="showSubmissionsModal = false" />
        </div>

        <div class="d-flex flex-column ga-3">
          <v-card
            v-for="sub in selectedStudentSubmissions"
            :key="sub.id"
            border
            flat
            class="pa-3 bg-grey-lighten-5 rounded-lg"
          >
            <div class="d-flex align-center justify-space-between flex-wrap ga-2 mb-2">
              <span class="text-subtitle-2 font-weight-black text-indigo">{{ getAssignmentTitle(sub.assignment_id) }}</span>
              <v-chip @click="selectedAssessment = sub" aria-label="View AI assessment details" color="success" size="small" variant="flat" class="font-weight-black">
                Score: {{ (sub.score_override ?? sub.score).toFixed(1) }}/10
              </v-chip>
            </div>

            <div class="text-caption font-italic text-grey-darken-3 bg-white pa-2 rounded border mb-2">
              "{{ sub.transcribed_text }}"
            </div>

            <!-- Supabase Audio Stream Player -->
            <div v-if="sub.audio_url" class="bg-white pa-2 rounded border d-flex align-center ga-2 mb-2">
              <v-icon color="primary">mdi-volume-high</v-icon>
              <audio controls :src="getMediaUrl(sub.audio_url)" class="w-100" style="height: 32px;" />
            </div>
            <div v-else class="text-caption text-warning font-weight-bold mb-2">
              <v-icon size="x-small">mdi-alert</v-icon> The audio file was not retained for this earlier submission.
            </div>

            <SubmissionEvaluation :evaluation="sub.evaluation || {}" :transcript="sub.transcribed_text || ''" />
            <!-- Teacher Feedback Input -->
            <div class="d-flex align-center ga-2">
              <v-text-field
                v-model="feedbackInputs[sub.id]"
                placeholder="Write custom feedback for student..."
                variant="outlined"
                density="compact"
                hide-details
                class="bg-white"
              />
              <v-btn
                color="primary"
                size="small"
                variant="flat"
                class="font-weight-bold text-none"
                @click="saveFeedback(sub.id)"
              >
                Save
              </v-btn>
            </div>
          </v-card>

          <div v-if="!selectedStudentSubmissions.length" class="text-center pa-6 text-caption text-grey">
            No audio submissions received from this student yet.
          </div>
        </div>
      </v-card>
    </v-dialog>

    <!-- Modal: Class QR Code Projection Poster -->
    <v-dialog v-model="showQrModal" max-width="480">
      <v-card v-if="qrClass" border rounded="lg" class="pa-6 text-center bg-white" id="qr-poster-card">
        <div class="d-flex align-center justify-space-between mb-2 border-b pb-2">
          <div class="d-flex align-center ga-2">
            <v-avatar color="indigo-lighten-5" size="36" class="text-indigo">
              <v-icon size="small">mdi-qrcode-scan</v-icon>
            </v-avatar>
            <div class="text-subtitle-1 font-weight-black text-primary text-left">CLASSROOM QR CODE POSTER</div>
          </div>
          <v-btn icon="mdi-close" variant="text" density="compact" @click="showQrModal = false" />
        </div>

        <div class="text-h6 font-weight-black text-indigo-darken-3 mb-1">{{ qrClass.name }}</div>
        <div class="text-caption text-grey font-weight-bold mb-3">{{ qrClass.grade_level }} • Join Code: <strong>{{ qrClass.join_code }}</strong></div>

        <div class="d-flex justify-center mb-3">
          <v-card border flat class="pa-3 bg-white rounded-lg elevation-2">
            <v-img :src="getQrCodeUrl(qrClass.join_code)" width="240" height="240" alt="Classroom QR Code" />
          </v-card>
        </div>

        <div class="text-caption font-weight-bold text-grey-darken-2 mb-4 bg-indigo-lighten-5 pa-2 rounded border border-indigo" style="word-break: break-all;">
          🔗 {{ getFullClassLink(qrClass.join_code) }}
        </div>

        <div class="d-flex align-center justify-center ga-2">
          <v-btn color="indigo" variant="flat" class="font-weight-bold text-none" prepend-icon="mdi-content-copy" @click="copyFullClassLink(qrClass.join_code)">
            Copy Full Link
          </v-btn>
          <v-btn color="teal" variant="tonal" class="font-weight-bold text-none" prepend-icon="mdi-printer" @click="printQrPoster">
            Print Poster
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <!-- Modal: Remind Non-Submitters -->
    <v-dialog v-model="showRemindModal" max-width="500">
      <v-card border rounded="lg" class="pa-4 bg-white">
        <div class="text-subtitle-1 font-weight-black text-amber-darken-4 mb-2 d-flex align-center ga-2">
          <v-icon color="amber-darken-4">mdi-bell-ring</v-icon>
          <span>Remind Non-Submitters</span>
        </div>
        <div class="text-caption text-grey mb-3">
          Broadcast a homework submission alert to enrolled students who have not yet submitted recordings for <strong>{{ remindAsg?.title }}</strong>.
        </div>
        <v-textarea
          v-model="remindCustomMessage"
          label="Custom Reminder Message (Optional):"
          placeholder="Friendly reminder to submit your pronunciation audio before the deadline..."
          rows="3"
          variant="outlined"
          density="comfortable"
          class="mb-3"
        />
        <div class="d-flex align-center justify-end ga-2">
          <v-btn variant="text" size="small" class="font-weight-bold text-none" @click="showRemindModal = false">
            Cancel
          </v-btn>
          <v-btn
            color="amber-darken-4"
            variant="flat"
            size="small"
            class="font-weight-black text-none"
            :loading="isSendingRemind"
            @click="submitRemind"
          >
            Dispatch Reminder Alert
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <!-- Modal: Duplicate Assignment -->
    <v-dialog v-model="showDuplicateModal" max-width="500">
      <v-card border rounded="lg" class="pa-4 bg-white">
        <div class="text-subtitle-1 font-weight-black text-teal-darken-3 mb-2 d-flex align-center ga-2">
          <v-icon color="teal">mdi-content-copy</v-icon>
          <span>Duplicate Assignment</span>
        </div>
        <div class="text-caption text-grey mb-3">
          Clone this assignment prompt and target IPA to the current class or another class you teach.
        </div>
        <v-select
          v-model="dupTargetClassId"
          :items="classes"
          item-title="name"
          item-value="id"
          label="Target Classroom:"
          variant="outlined"
          density="comfortable"
          class="mb-2"
        />
        <v-text-field
          v-model="dupTitle"
          label="New Assignment Title:"
          variant="outlined"
          density="comfortable"
          class="mb-2"
        />
        <v-text-field
          v-model="dupDueDate"
          label="New Due Date (YYYY-MM-DD):"
          type="date"
          variant="outlined"
          density="comfortable"
          class="mb-3"
        />
        <div class="d-flex align-center justify-end ga-2">
          <v-btn variant="text" size="small" class="font-weight-bold text-none" @click="showDuplicateModal = false">
            Cancel
          </v-btn>
          <v-btn
            color="teal"
            variant="flat"
            size="small"
            class="font-weight-black text-none"
            :loading="isDuplicating"
            @click="submitDuplicate"
          >
            Clone Assignment
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <!-- Modal: Re-open / Extend Deadline -->
    <v-dialog v-model="showReopenModal" max-width="500">
      <v-card border rounded="lg" class="pa-4 bg-white">
        <div class="text-subtitle-1 font-weight-black text-indigo-darken-3 mb-2 d-flex align-center ga-2">
          <v-icon color="indigo">mdi-clock-fast</v-icon>
          <span>Re-open / Extend Deadline</span>
        </div>
        <div class="text-caption text-grey mb-3">
          Extend the submission window for <strong>{{ reopenAsg?.title }}</strong>. A deadline notice will automatically be posted to the class noticeboard.
        </div>
        <v-text-field
          v-model="reopenDueDate"
          label="Extended Due Date (YYYY-MM-DD):"
          type="date"
          variant="outlined"
          density="comfortable"
          class="mb-2"
        />
        <v-text-field
          v-model="reopenNote"
          label="Extension Note for Students (Optional):"
          placeholder="Example: Extended by 3 days for revision."
          variant="outlined"
          density="comfortable"
          class="mb-3"
        />
        <div class="d-flex align-center justify-end ga-2">
          <v-btn variant="text" size="small" class="font-weight-bold text-none" @click="showReopenModal = false">
            Cancel
          </v-btn>
          <v-btn
            color="indigo"
            variant="flat"
            size="small"
            class="font-weight-black text-none"
            :loading="isReopening"
            @click="submitReopen"
          >
            Confirm Extension
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <!-- Modal: Post Noticeboard Announcement -->
    <v-dialog v-model="showPostAnnouncementModal" max-width="500">
      <v-card border rounded="lg" class="pa-4 bg-white">
        <div class="text-subtitle-1 font-weight-black text-primary mb-2 d-flex align-center ga-2">
          <v-icon color="primary">mdi-bullhorn</v-icon>
          <span>Post Class Announcement</span>
        </div>
        <v-text-field
          v-model="postAnnTitle"
          label="Notice Title:"
          placeholder="Example: Homework Schedule Update"
          variant="outlined"
          density="comfortable"
          class="mb-2"
        />
        <v-select
          v-model="postAnnType"
          :items="[
            { title: 'General Notice', value: 'general' },
            { title: 'Urgent Alert', value: 'urgent' },
            { title: 'Homework Reminder', value: 'reminder' }
          ]"
          item-title="title"
          item-value="value"
          label="Category:"
          variant="outlined"
          density="comfortable"
          class="mb-2"
        />
        <v-textarea
          v-model="postAnnContent"
          label="Announcement Content:"
          placeholder="Write your announcement message for students..."
          rows="4"
          variant="outlined"
          density="comfortable"
          class="mb-3"
        />
        <div class="d-flex align-center justify-end ga-2">
          <v-btn variant="text" size="small" class="font-weight-bold text-none" @click="showPostAnnouncementModal = false">
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            size="small"
            class="font-weight-black text-none"
            :loading="isPostingAnn"
            @click="submitPostAnnouncement"
          >
            Publish Notice
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <!-- Modal: Delete Announcement Confirmation -->
    <v-dialog v-model="showDeleteAnnouncementModal" max-width="420">
      <v-card border rounded="lg" class="pa-4 bg-white">
        <div class="text-subtitle-1 font-weight-black text-error mb-2 d-flex align-center ga-2">
          <v-icon color="error">mdi-alert</v-icon>
          <span>Confirm Delete Notice</span>
        </div>
        <div class="text-body-2 text-grey-darken-3 mb-4">
          Are you sure you want to delete this notice? It will no longer appear on the student noticeboard.
        </div>
        <div class="d-flex align-center justify-end ga-2">
          <v-btn variant="text" size="small" class="font-weight-bold text-none" @click="showDeleteAnnouncementModal = false">
            Cancel
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            size="small"
            class="font-weight-black text-none"
            :loading="isDeletingAnn"
            @click="submitDeleteAnnouncement"
          >
            Delete Notice
          </v-btn>
        </div>
      </v-card>
    </v-dialog>
    </div>
  </v-container>
  <AssessmentDialog :submission="selectedAssessment" :audio-url="selectedAssessment ? getMediaUrl(selectedAssessment.audio_url) : ''" @close="selectedAssessment = null" />
  <v-dialog v-model="showAssignmentReview" max-width="1100" scrollable>
    <v-card v-if="reviewAssignment">
      <v-card-title class="d-flex align-center justify-space-between">
        <div><div class="text-caption">Assignment Submissions</div>{{ reviewAssignment.title }}</div>
        <v-btn icon="mdi-close" variant="text" aria-label="Close submissions" @click="showAssignmentReview = false" />
      </v-card-title>
      <v-card-text>
        <p class="mb-3">{{ assignmentReviewRows.filter(r => r.submission).length }} / {{ gradebook.students.length }} students submitted. Latest submission shown for each student.</p>
        <div class="d-flex ga-3 flex-wrap mb-3">
          <v-text-field v-model="reviewSearch" label="Search student name or email" prepend-inner-icon="mdi-magnify" hide-details density="compact" />
          <v-select v-model="reviewStatus" :items="['All Students', 'Submitted', 'Not Submitted']" label="Submission Status" hide-details density="compact" style="max-width: 220px" />
          <v-btn variant="tonal" prepend-icon="mdi-refresh" @click="selectClass(selectedClassId)">Refresh</v-btn>
        </div>
        <v-card v-for="row in filteredAssignmentReviewRows" :key="row.student.id" variant="outlined" class="pa-3 mb-3">
          <div class="d-flex align-center justify-space-between flex-wrap ga-2 mb-2">
            <div><strong>{{ row.student.name }}</strong><div class="text-caption">{{ row.student.email }}</div></div>
            <v-chip :color="row.submission ? 'success' : 'warning'">{{ row.submission ? 'Submitted' : 'Not Submitted' }}</v-chip>
          </div>
          <template v-if="row.submission">
            <p class="text-caption mb-2">{{ row.submission.submitted_at || row.submission.created_at || '' }} · {{ row.attempts }} submission(s)</p>
            <audio v-if="row.submission.audio_url" controls preload="none" :src="getMediaUrl(row.submission.audio_url)" class="w-100 mb-2" />
            <v-alert v-else type="warning" variant="tonal" density="compact" class="mb-2">The recording is unavailable for this submission.</v-alert>
            <v-btn color="primary" variant="tonal" prepend-icon="mdi-text-box-search-outline" class="mb-3" @click="selectedAssessment = row.submission">Score: {{ row.submission.score_override ?? row.submission.score ?? 'Unavailable' }}/10 · View Assessment</v-btn>
            <v-expansion-panels v-if="row.attempts > 1" class="mb-3">
              <v-expansion-panel title="All Submission Attempts">
                <v-expansion-panel-text>
                  <v-btn v-for="attempt in row.history" :key="attempt.id" variant="text" class="ma-1" @click="selectedAssessment = attempt">{{ attempt.submitted_at || ('Submission #' + attempt.id) }} · {{ attempt.score_override ?? attempt.score ?? 'Unavailable' }}/10</v-btn>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
            <div class="d-flex ga-2 align-center">
              <v-textarea v-model="feedbackInputs[row.submission.id]" label="Educator Feedback" rows="2" auto-grow hide-details />
              <v-btn color="primary" @click="saveFeedback(row.submission.id)">Save Feedback</v-btn>
            </div>
          </template>
          <p v-else class="text-body-2 text-grey-darken-1">No recording or assessment has been submitted for this assignment.</p>
        </v-card>
        <p v-if="!filteredAssignmentReviewRows.length" class="text-center pa-4">No students match these filters.</p>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import AssessmentDialog from './AssessmentDialog.vue'
import { ref, computed, watch, onMounted } from 'vue'
const selectedAssessment = ref(null)
import { useRouter } from 'vue-router'
import SubmissionEvaluation from './SubmissionEvaluation.vue'
import { isMyHanhSite, isElementaryGrade, ELEMENTARY_GRADE, mediaUrl } from '@/utils/siteProfile.js'
import { GRADE_LEVELS } from '@/constants/topics.js'

const props = defineProps({
  backendUrl: String,
  userId: Number,
  userRole: String
})

const router = useRouter()

const activeUserRole = ref(props.userRole || localStorage.getItem('user_role') || 'student')

watch(() => props.userRole, (newRole) => {
  if (newRole) {
    activeUserRole.value = newRole
    if (['teacher', 'admin', 'super_admin'].includes(newRole)) {
      fetchClasses()
    }
  }
})

const localTeacherId = ref(Number(localStorage.getItem('user_id')) || null)
const loginEmail = ref('')
const loginPassword = ref('')
const isLoggingIn = ref(false)
const loginError = ref('')

const getActiveTeacherId = () => {
  return props.userId || localTeacherId.value || Number(localStorage.getItem('user_id')) || null
}

const toast = ref({ show: false, text: '', color: 'success', icon: 'mdi-check-circle' })
const notify = (text, color = 'success', icon = 'mdi-check-circle') => {
  toast.value = { show: true, text, color, icon }
}

const showLogoutDialog = ref(false)

const confirmSignOut = () => {
  showLogoutDialog.value = false
  handleTeacherSignOut()
}

const getTeacherAuthHeaders = () => {
  const token = localStorage.getItem('teacher_auth_token') || ''
  const headers = { 'Content-Type': 'application/json' }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

const handleTeacherSignOut = () => {
  activeUserRole.value = 'none'
  localStorage.removeItem('user_role')
  localStorage.removeItem('user_id')
  localStorage.removeItem('teacher_auth_token')
  localStorage.removeItem('teacher_token')
  localStorage.removeItem('speak_user_email')
  localStorage.removeItem('speak_user_name')
  loginEmail.value = ''
  loginPassword.value = ''
  notify('Signed out from Teacher Hub.', 'info', 'mdi-logout')
  window.location.href = '/'
}

const handleTeacherSignIn = async () => {
  if (!loginEmail.value.trim() || !loginPassword.value.trim()) return
  isLoggingIn.value = true
  loginError.value = ''
  try {
    const res = await fetch(`${props.backendUrl}/api/teacher/login`, {
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
        localStorage.setItem('teacher_auth_token', data.token)
      }
      activeUserRole.value = data.user.role || 'teacher'
      localStorage.setItem('user_role', data.user.role || 'teacher')
      if (data.user?.id) {
        localTeacherId.value = data.user.id
        localStorage.setItem('user_id', data.user.id)
      }
      if (data.user?.email) {
        localStorage.setItem('speak_user_email', data.user.email)
      }
      if (data.user?.name) {
        localStorage.setItem('speak_user_name', data.user.name)
      }
      notify(`Welcome! Signed in as ${data.user.name}`, 'success', 'mdi-school')
      await fetchClasses()
    } else {
      const err = await res.json()
      loginError.value = err.detail || 'Invalid Teacher Credentials.'
    }
  } catch (e) {
    loginError.value = 'Sign in error: ' + e.message
  } finally {
    isLoggingIn.value = false
  }
}

const allClasses = ref([])
const isMyHanh = isMyHanhSite()
const classGradeOptions = GRADE_LEVELS.filter(g => !isMyHanh || g.id === 'primary').map(g => g.name)
const classes = computed(() => allClasses.value.filter(c => !isMyHanh || isElementaryGrade(c.grade_level)))
const getMediaUrl = (url) => mediaUrl(url, props.backendUrl)
const assignmentPreviewUrl = ref('')
const selectedClassId = ref(null)
const activeTab = ref('gradebook')
const gradebook = ref({ classroom: null, students: [], assignments: [], submissions: [] })

const showCreateClassModal = ref(false)
const newClassName = ref('')
const newClassGrade = ref('Elementary (Grades 1 - 5)')
const isCreatingClass = ref(false)
const teacherQuota = ref(null)
const showPlanDetailsModal = ref(false)

// P2 Analytics & Insights state
const analyticsData = ref(null)
const isFetchingAnalytics = ref(false)

// P2 Noticeboard state
const announcements = ref([])
const isFetchingAnnouncements = ref(false)
const showPostAnnouncementModal = ref(false)
const postAnnTitle = ref('')
const postAnnContent = ref('')
const postAnnType = ref('general')
const isPostingAnn = ref(false)
const showDeleteAnnouncementModal = ref(false)
const annToDelete = ref(null)
const isDeletingAnn = ref(false)

// P2 Remind Non-Submitters state
const showRemindModal = ref(false)
const remindAsg = ref(null)
const remindCustomMessage = ref('')
const isSendingRemind = ref(false)

// P2 Duplicate Assignment state
const showDuplicateModal = ref(false)
const duplicateAsg = ref(null)
const dupTargetClassId = ref(null)
const dupTitle = ref('')
const dupDueDate = ref('')
const isDuplicating = ref(false)

// P2 Reopen / Extend Deadline state
const showReopenModal = ref(false)
const reopenAsg = ref(null)
const reopenDueDate = ref('')
const reopenNote = ref('')
const isReopening = ref(false)

const showQrModal = ref(false)
const qrClass = ref(null)

const getFullClassLink = (joinCode) => {
  const origin = window.location.origin || 'https://fluent.augusttrung.com'
  return `${origin}${isMyHanhSite() ? "/join" : "/homework"}?join_code=${encodeURIComponent(joinCode)}`
}

const getQrCodeUrl = (joinCode) => {
  const fullLink = getFullClassLink(joinCode)
  return `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(fullLink)}`
}

const exportGradebookCSV = async () => {
  if (!selectedClassId.value) {
    notify('Please select a classroom first.', 'warning')
    return
  }
  const selectedClassName = selectedClass.value ? selectedClass.value.name : 'Class'

  try {
    const res = await fetch(`${props.backendUrl}/api/classes/${selectedClassId.value}/export-gradebook`, {
      headers: getTeacherAuthHeaders()
    })
    if (res.ok) {
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      const dateStr = new Date().toISOString().slice(0, 10)
      link.setAttribute('href', url)
      link.setAttribute('download', `Gradebook_${selectedClassName.replace(/[^a-zA-Z0-9]/g, '_')}_${dateStr}.csv`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      notify(`Official Gradebook exported for ${selectedClassName}!`, 'success', 'mdi-file-excel')
      return
    }
  } catch (err) {
    console.warn('Backend CSV export failed, falling back to client generation', err)
  }

  // Fallback client CSV in 100% Academic English
  const headers = ['"Student Name"', '"Email"', '"Submissions"', '"Average Score (/10)"', '"Academic Standing"']
  const rows = (filteredStudents.value || []).map(std => {
    const name = `"${(std.name || 'Learner').replace(/"/g, '""')}"`
    const email = `"${(std.email || '--').replace(/"/g, '""')}"`
    const count = std.submission_count || std.total_submissions || 0
    const scoreNum = std.avg_score || 0
    let standing = '"Needs Support"'
    if (scoreNum >= 8.5) standing = '"High Distinction"'
    else if (scoreNum >= 7.0) standing = '"Proficient"'
    else if (scoreNum >= 5.0) standing = '"Developing"'
    return [name, email, count, `"${scoreNum.toFixed(1)}"`, standing].join(',')
  })
  const csvContent = '\uFEFF' + [headers.join(','), ...rows].join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  const dateStr = new Date().toISOString().slice(0, 10)
  link.setAttribute('href', url)
  link.setAttribute('download', `Gradebook_${selectedClassName.replace(/[^a-zA-Z0-9]/g, '_')}_${dateStr}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  notify(`Gradebook exported successfully for ${selectedClassName}!`, 'success', 'mdi-file-excel')
}

const openQrPosterModal = (cls) => {
  qrClass.value = cls
  showQrModal.value = true
}

const copyFullClassLink = (joinCode) => {
  const fullLink = getFullClassLink(joinCode)
  navigator.clipboard.writeText(fullLink)
  notify(`Full domain link copied: ${fullLink}`, 'success', 'mdi-content-copy')
}

const printQrPoster = () => {
  window.print()
}

const showCreateAssignmentModal = ref(false)
const newAsgType = ref('sentence')
const newAsgTitle = ref('')
const newAsgSentence = ref('')
const newAsgPictureTopic = ref('')
const newAsgImageUrl = ref('')
const newAsgGuidingQuestionsText = ref('')
const newAsgGuidingQuestionsList = ref([])
const newAsgQuestionsMode = ref('list')
const newAsgTargetKeywordsText = ref('')
const isGeneratingAsgPicture = ref(false)
const newAsgDueDate = ref('')
const isCreatingAsg = ref(false)

const syncNewAsgQuestionsFromText = () => {
  newAsgGuidingQuestionsList.value = newAsgGuidingQuestionsText.value
    ? newAsgGuidingQuestionsText.value.split('\n').map(q => q.trim()).filter(Boolean)
    : []
}

const syncNewAsgQuestionsToText = () => {
  newAsgGuidingQuestionsText.value = newAsgGuidingQuestionsList.value.join('\n')
}

const addNewAsgQuestion = () => {
  newAsgGuidingQuestionsList.value.push('')
  syncNewAsgQuestionsToText()
}

const removeNewAsgQuestion = (index) => {
  newAsgGuidingQuestionsList.value.splice(index, 1)
  syncNewAsgQuestionsToText()
}

const teacherTopicIdeas = isMyHanh ? ['My Classroom', 'Family Breakfast', 'At the Playground', 'A Visit to the Zoo', 'My Pets', 'A School Picnic'] : [
  'Hospital Emergency Hallway',
  'A University Science Research Lab',
  'Airport Departure Terminal',
  'Professional Job Interview',
  'A Bustling Urban Coffee Shop',
  'Modern Collaborative Office'
]

const teacherPictureMode = ref('ai_gen')
const teacherFileInputRef = ref(null)

const handleTeacherUploadImageChange = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  isGeneratingAsgPicture.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const uploadRes = await fetch(`${props.backendUrl}/api/picture-practice/upload-image`, {
      method: 'POST',
      body: formData
    })
    if (!uploadRes.ok) throw new Error('Failed to upload image')
    const uploadData = await uploadRes.json()
    newAsgImageUrl.value = uploadData.image_url
    
    // Call scenario creation with mode=upload
    const topic = newAsgPictureTopic.value.trim() || file.name.replace(/\.[^/.]+$/, '')
    const scRes = await fetch(`${props.backendUrl}/api/picture-practice/create-scenario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topic,
        level: isMyHanh ? 'beginner' : 'intermediate',
        mode: 'upload',
        image_url: uploadData.image_url,
        user_id: props.userId || 1
      })
    })
    if (scRes.ok) {
      const data = await scRes.json()
      if (!newAsgTitle.value.trim() || newAsgTitle.value.startsWith('Speaking Practice:')) {
        newAsgTitle.value = data.title || `Describe the Picture: ${topic}`
      }
      if (Array.isArray(data.guiding_questions)) {
        newAsgGuidingQuestionsList.value = [...data.guiding_questions]
        newAsgGuidingQuestionsText.value = data.guiding_questions.join('\n')
      }
      if (Array.isArray(data.keywords)) {
        newAsgTargetKeywordsText.value = data.keywords.join(', ')
      }
      notify('Exam picture uploaded & visual questions formulated!', 'success')
    }
  } catch (err) {
    console.error('Error uploading teacher picture:', err)
    notify('Failed to upload exam picture: ' + err.message, 'error')
  } finally {
    isGeneratingAsgPicture.value = false
  }
}

const selectTeacherTopicIdea = (theme) => {
  newAsgPictureTopic.value = theme
  if (!newAsgTitle.value.trim() || newAsgTitle.value.startsWith('Speaking Practice:')) {
    newAsgTitle.value = `Speaking Practice: ${theme}`
  }
}

const generateAIPictureScenario = async () => {
  const topic = newAsgPictureTopic.value.trim() || 'Daily Life'
  isGeneratingAsgPicture.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/picture-practice/create-scenario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topic,
        level: isMyHanh ? 'beginner' : 'intermediate',
        user_id: props.userId || 1
      })
    })
    if (res.ok) {
      const data = await res.json()
      newAsgImageUrl.value = data.image_url || ''
      if (!newAsgTitle.value.trim() || newAsgTitle.value.startsWith('Speaking Practice:')) {
        newAsgTitle.value = data.title || `Describe the Picture: ${topic}`
      }
      if (Array.isArray(data.guiding_questions)) {
        newAsgGuidingQuestionsList.value = [...data.guiding_questions]
        newAsgGuidingQuestionsText.value = data.guiding_questions.join('\n')
      }
      if (Array.isArray(data.keywords)) {
        newAsgTargetKeywordsText.value = data.keywords.join(', ')
      }
      notify('AI picture scenario generated with authentic visual questions!', 'success')
    } else {
      const error = await res.json().catch(() => ({}))
      notify(error.detail || 'Failed to generate picture scenario. Your previous image has been kept.', 'error')
    }
  } catch (err) {
    console.error('Error generating picture scenario:', err)
    notify('Network error generating picture scenario.', 'error')
  } finally {
    isGeneratingAsgPicture.value = false
  }
}

const showSubmissionsModal = ref(false)
const selectedStudent = ref(null)
const feedbackInputs = ref({})

const searchStudentText = ref('')
const filteredStudents = computed(() => {
  const stds = gradebook.value.students || []
  if (!searchStudentText.value.trim()) return stds
  const q = searchStudentText.value.toLowerCase().trim()
  return stds.filter(s => (s.name || '').toLowerCase().includes(q) || (s.email || '').toLowerCase().includes(q))
})

const searchClassText = ref('')
const filteredClasses = computed(() => {
  if (!searchClassText.value?.trim()) return classes.value
  const q = searchClassText.value.toLowerCase().trim()
  return classes.value.filter(c => 
    (c.name || '').toLowerCase().includes(q) ||
    (c.join_code || '').toLowerCase().includes(q) ||
    (c.grade_level || '').toLowerCase().includes(q)
  )
})

// Edit / Delete Class states
const showEditClassModal = ref(false)
const editClassName = ref('')
const editClassGrade = ref('Elementary (Grades 1 - 5)')
const isUpdatingClass = ref(false)

const showDeleteClassModal = ref(false)
const isDeletingClass = ref(false)

// Remove Student states
const showRemoveStudentModal = ref(false)
const studentToRemove = ref(null)
const isRemovingStudent = ref(false)

// Edit / Delete Assignment states
const showEditAssignmentModal = ref(false)
const editingAsg = ref(null)
const editAsgTitle = ref('')
const editAsgSentence = ref('')
const editAsgDueDate = ref('')
const isUpdatingAsg = ref(false)

const showDeleteAssignmentModal = ref(false)
const asgToDelete = ref(null)
const isDeletingAsg = ref(false)

const openEditClassModal = () => {
  if (!selectedClass.value) return
  editClassName.value = selectedClass.value.name
  editClassGrade.value = isMyHanh ? ELEMENTARY_GRADE : selectedClass.value.grade_level
  showEditClassModal.value = true
}

const submitEditClass = async () => {
  if (!editClassName.value.trim() || !selectedClassId.value) return
  isUpdatingClass.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/${selectedClassId.value}/update`, {
      method: 'POST',
      headers: getTeacherAuthHeaders(),
      body: JSON.stringify({
        name: editClassName.value.trim(),
        grade_level: editClassGrade.value
      })
    })
    if (res.ok) {
      showEditClassModal.value = false
      notify('Classroom updated successfully!', 'success', 'mdi-check-circle')
      await fetchClasses()
    }
  } catch (err) {
    notify('Failed to update class: ' + err.message, 'error', 'mdi-alert-circle')
  } finally {
    isUpdatingClass.value = false
  }
}

const submitDeleteClass = async () => {
  if (!selectedClassId.value) return
  isDeletingClass.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/${selectedClassId.value}`, {
      method: 'DELETE',
      headers: getTeacherAuthHeaders()
    })
    if (res.ok) {
      showDeleteClassModal.value = false
      selectedClassId.value = null
      notify('Classroom deleted successfully!', 'info', 'mdi-delete')
      await fetchClasses()
    }
  } catch (err) {
    notify('Failed to delete class: ' + err.message, 'error', 'mdi-alert-circle')
  } finally {
    isDeletingClass.value = false
  }
}

const confirmRemoveStudent = (std) => {
  studentToRemove.value = std
  showRemoveStudentModal.value = true
}

const submitRemoveStudent = async () => {
  if (!studentToRemove.value || !selectedClassId.value) return
  isRemovingStudent.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/${selectedClassId.value}/remove-student`, {
      method: 'POST',
      headers: getTeacherAuthHeaders(),
      body: JSON.stringify({ student_id: studentToRemove.value.id })
    })
    if (res.ok) {
      showRemoveStudentModal.value = false
      notify(`Removed ${studentToRemove.value.name} from class.`, 'info')
      await selectClass(selectedClassId.value)
    }
  } catch (err) {
    notify('Failed to remove student: ' + err.message, 'error', 'mdi-alert-circle')
  } finally {
    isRemovingStudent.value = false
  }
}

const editAsgImageUrl = ref('')
const editAsgGuidingQuestionsList = ref([])
const editAsgTargetKeywordsText = ref('')

const addEditAsgQuestion = () => {
  editAsgGuidingQuestionsList.value.push('')
}

const removeEditAsgQuestion = (index) => {
  editAsgGuidingQuestionsList.value.splice(index, 1)
}

const openEditAssignmentModal = (asg) => {
  editingAsg.value = asg
  editAsgTitle.value = asg.title || ''
  editAsgSentence.value = asg.topic_sentence || ''
  editAsgDueDate.value = asg.due_date || ''
  editAsgImageUrl.value = asg.image_url || ''
  
  const gq = Array.isArray(asg.guiding_questions) ? asg.guiding_questions : []
  editAsgGuidingQuestionsList.value = gq.length > 0 ? [...gq] : ['What is the primary subject in this scene?']
  
  const tk = Array.isArray(asg.target_keywords) ? asg.target_keywords : []
  editAsgTargetKeywordsText.value = tk.join(', ')
  
  showEditAssignmentModal.value = true
}

const submitEditAssignment = async () => {
  if (!editingAsg.value || !editAsgTitle.value.trim()) return
  const isPicture = editingAsg.value.assignment_type === 'picture'
  isUpdatingAsg.value = true
  try {
    const payload = {
      title: editAsgTitle.value.trim(),
      topic_sentence: editAsgSentence.value.trim(),
      due_date: editAsgDueDate.value.trim()
    }
    if (isPicture) {
      payload.assignment_type = 'picture'
      payload.image_url = editAsgImageUrl.value.trim()
      payload.guiding_questions = editAsgGuidingQuestionsList.value.map(q => q.trim()).filter(Boolean)
      payload.target_keywords = editAsgTargetKeywordsText.value.split(',').map(k => k.trim()).filter(Boolean)
      payload.time_limit_seconds = 0
    }
    const res = await fetch(`${props.backendUrl}/api/assignments/${editingAsg.value.id}/update`, {
      method: 'POST',
      headers: getTeacherAuthHeaders(),
      body: JSON.stringify(payload)
    })
    if (res.ok) {
      showEditAssignmentModal.value = false
      notify('Assignment updated successfully!', 'success')
      await selectClass(selectedClassId.value)
    } else {
      const errData = await res.json().catch(() => ({}))
      notify('Failed to update assignment: ' + (errData.detail || 'Unknown error'), 'error', 'mdi-alert-circle')
    }
  } catch (err) {
    notify('Failed to update assignment: ' + err.message, 'error', 'mdi-alert-circle')
  } finally {
    isUpdatingAsg.value = false
  }
}

const confirmDeleteAssignment = (asg) => {
  asgToDelete.value = asg
  showDeleteAssignmentModal.value = true
}

const submitDeleteAssignment = async () => {
  if (!asgToDelete.value) return
  isDeletingAsg.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/assignments/${asgToDelete.value.id}`, {
      method: 'DELETE',
      headers: getTeacherAuthHeaders()
    })
    if (res.ok) {
      showDeleteAssignmentModal.value = false
      notify('Assignment deleted.', 'info')
      await selectClass(selectedClassId.value)
    }
  } catch (err) {
    notify('Failed to delete assignment: ' + err.message, 'error', 'mdi-alert-circle')
  } finally {
    isDeletingAsg.value = false
  }
}

const selectedClass = computed(() => {
  return classes.value.find(c => c.id === selectedClassId.value)
})

const totalStudentsCount = computed(() => {
  return classes.value.reduce((acc, c) => acc + (c.student_count || 0), 0)
})

const totalSubmissionsCount = computed(() => {
  return gradebook.value.submissions?.length || 0
})

const fetchClasses = async () => {
  const tid = getActiveTeacherId()
  if (!tid) return
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/teacher/${tid}`, {
      headers: getTeacherAuthHeaders()
    })
    if (res.status === 401) {
      handleTeacherSignOut()
      return
    }
    if (res.ok) {
      const data = await res.json()
      allClasses.value = data.classes || []
      teacherQuota.value = data.quota || null
      if (classes.value.length && !selectedClassId.value) {
        selectClass(classes.value[0].id)
      }
    }
  } catch (err) {
    console.error('Fetch classes error:', err)
  }
}

const fetchClassAnalytics = async (classId) => {
  if (!classId) return
  isFetchingAnalytics.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/${classId}/analytics`, {
      headers: getTeacherAuthHeaders()
    })
    if (res.ok) {
      analyticsData.value = await res.json()
    }
  } catch (err) {
    console.error('Fetch analytics error:', err)
  } finally {
    isFetchingAnalytics.value = false
  }
}

const fetchClassAnnouncements = async (classId) => {
  if (!classId) return
  isFetchingAnnouncements.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/${classId}/announcements`, {
      headers: getTeacherAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      announcements.value = data.announcements || []
    }
  } catch (err) {
    console.error('Fetch announcements error:', err)
  } finally {
    isFetchingAnnouncements.value = false
  }
}

const selectClass = async (classId) => {
  selectedClassId.value = classId
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/${classId}/gradebook`, {
      headers: getTeacherAuthHeaders()
    })
    if (res.status === 401) {
      handleTeacherSignOut()
      return
    }
    if (res.ok) {
      gradebook.value = await res.json()
    }
  } catch (err) {
    console.error('Fetch gradebook error:', err)
  }
  await Promise.all([
    fetchClassAnalytics(classId),
    fetchClassAnnouncements(classId)
  ])
}

// Remind handlers
const openRemindModal = (asg) => {
  remindAsg.value = asg
  remindCustomMessage.value = ''
  showRemindModal.value = true
}

const submitRemind = async () => {
  if (!remindAsg.value) return
  isSendingRemind.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/assignments/${remindAsg.value.id}/remind`, {
      method: 'POST',
      headers: getTeacherAuthHeaders(),
      body: JSON.stringify({ custom_message: remindCustomMessage.value.trim() })
    })
    if (res.ok) {
      const data = await res.json()
      showRemindModal.value = false
      notify(`Reminder sent to ${data.reminded_count} non-submitter students!`, 'success', 'mdi-bell-ring')
      await fetchClassAnnouncements(selectedClassId.value)
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to dispatch reminders.', 'error')
    }
  } catch (e) {
    notify('Reminder dispatch error: ' + e.message, 'error')
  } finally {
    isSendingRemind.value = false
  }
}

// Duplicate handlers
const openDuplicateModal = (asg) => {
  duplicateAsg.value = asg
  dupTargetClassId.value = selectedClassId.value
  dupTitle.value = `Copy of ${asg.title}`
  const future = new Date()
  future.setDate(future.getDate() + 7)
  dupDueDate.value = future.toISOString().slice(0, 10)
  showDuplicateModal.value = true
}

const submitDuplicate = async () => {
  if (!duplicateAsg.value || !dupTitle.value.trim()) return
  isDuplicating.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/assignments/${duplicateAsg.value.id}/duplicate`, {
      method: 'POST',
      headers: getTeacherAuthHeaders(),
      body: JSON.stringify({
        target_class_id: dupTargetClassId.value,
        new_title: dupTitle.value.trim(),
        new_due_date: dupDueDate.value
      })
    })
    if (res.ok) {
      showDuplicateModal.value = false
      notify('Assignment duplicated successfully!', 'success', 'mdi-content-copy')
      await selectClass(selectedClassId.value)
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to duplicate assignment.', 'error')
    }
  } catch (e) {
    notify('Duplicate error: ' + e.message, 'error')
  } finally {
    isDuplicating.value = false
  }
}

// Re-open handlers
const openReopenModal = (asg) => {
  reopenAsg.value = asg
  const future = new Date()
  future.setDate(future.getDate() + 3)
  reopenDueDate.value = asg.due_date || future.toISOString().slice(0, 10)
  reopenNote.value = ''
  showReopenModal.value = true
}

const submitReopen = async () => {
  if (!reopenAsg.value || !reopenDueDate.value) return
  isReopening.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/assignments/${reopenAsg.value.id}/reopen`, {
      method: 'POST',
      headers: getTeacherAuthHeaders(),
      body: JSON.stringify({
        new_due_date: reopenDueDate.value,
        extension_note: reopenNote.value.trim()
      })
    })
    if (res.ok) {
      showReopenModal.value = false
      notify(`Deadline extended to ${reopenDueDate.value}!`, 'success', 'mdi-clock-fast')
      await selectClass(selectedClassId.value)
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to extend deadline.', 'error')
    }
  } catch (e) {
    notify('Extension error: ' + e.message, 'error')
  } finally {
    isReopening.value = false
  }
}

// Noticeboard handlers
const submitPostAnnouncement = async () => {
  if (!postAnnTitle.value.trim() || !postAnnContent.value.trim() || !selectedClassId.value) return
  isPostingAnn.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/${selectedClassId.value}/announcements`, {
      method: 'POST',
      headers: getTeacherAuthHeaders(),
      body: JSON.stringify({
        title: postAnnTitle.value.trim(),
        content: postAnnContent.value.trim(),
        announcement_type: postAnnType.value
      })
    })
    if (res.ok) {
      showPostAnnouncementModal.value = false
      postAnnTitle.value = ''
      postAnnContent.value = ''
      notify('Notice posted to classroom noticeboard!', 'success', 'mdi-bullhorn')
      await fetchClassAnnouncements(selectedClassId.value)
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to publish notice.', 'error')
    }
  } catch (e) {
    notify('Publish notice error: ' + e.message, 'error')
  } finally {
    isPostingAnn.value = false
  }
}

const confirmDeleteAnnouncement = (ann) => {
  annToDelete.value = ann
  showDeleteAnnouncementModal.value = true
}

const submitDeleteAnnouncement = async () => {
  if (!annToDelete.value || !selectedClassId.value) return
  isDeletingAnn.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/${selectedClassId.value}/announcements/${annToDelete.value.id}`, {
      method: 'DELETE',
      headers: getTeacherAuthHeaders()
    })
    if (res.ok) {
      showDeleteAnnouncementModal.value = false
      notify('Announcement deleted from noticeboard.', 'info')
      await fetchClassAnnouncements(selectedClassId.value)
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to delete announcement.', 'error')
    }
  } catch (e) {
    notify('Delete error: ' + e.message, 'error')
  } finally {
    isDeletingAnn.value = false
  }
}

const submitCreateClass = async () => {
  if (!newClassName.value.trim()) return
  const tid = getActiveTeacherId()
  if (!tid) {
    notify('Please sign in as a teacher to create a classroom.', 'warning', 'mdi-school')
    return
  }
  isCreatingClass.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/create`, {
      method: 'POST',
      headers: getTeacherAuthHeaders(),
      body: JSON.stringify({
        teacher_id: tid,
        name: newClassName.value.trim(),
        grade_level: newClassGrade.value
      })
    })
    if (res.ok) {
      newClassName.value = ''
      showCreateClassModal.value = false
      notify('New class created successfully!', 'success')
      await fetchClasses()
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to create class.', 'error')
    }
  } catch (err) {
    notify('Failed to create class: ' + err.message, 'error', 'mdi-alert-circle')
  } finally {
    isCreatingClass.value = false
  }
}

const submitCreateAssignment = async () => {
  const isPicture = newAsgType.value === 'picture'
  if (!newAsgTitle.value.trim()) {
    notify('Please enter an assignment title.', 'warning')
    return
  }
  if (!isPicture && !newAsgSentence.value.trim()) {
    notify('Please enter the model reading sentence.', 'warning')
    return
  }
  if (isPicture && !newAsgImageUrl.value) {
    notify('Please generate or upload an image before assigning picture homework.', 'warning')
    return
  }
  const tid = getActiveTeacherId()
  if (!tid) {
    notify('Please sign in as a teacher to assign homework.', 'warning', 'mdi-school')
    return
  }
  isCreatingAsg.value = true
  try {
    const gQuestions = newAsgGuidingQuestionsList.value.length > 0
      ? newAsgGuidingQuestionsList.value.map(q => q.trim()).filter(Boolean)
      : (newAsgGuidingQuestionsText.value ? newAsgGuidingQuestionsText.value.split('\n').map(q => q.trim()).filter(Boolean) : [])
    const tKeywords = newAsgTargetKeywordsText.value
      ? newAsgTargetKeywordsText.value.split(',').map(k => k.trim()).filter(Boolean)
      : []

    const res = await fetch(`${props.backendUrl}/api/assignments/create`, {
      method: 'POST',
      headers: getTeacherAuthHeaders(),
      body: JSON.stringify({
        class_id: selectedClassId.value,
        teacher_id: tid,
        title: newAsgTitle.value.trim(),
        topic_sentence: (isPicture ? (newAsgPictureTopic.value.trim() || newAsgTitle.value.trim()) : newAsgSentence.value.trim()),
        due_date: newAsgDueDate.value.trim(),
        assignment_type: newAsgType.value,
        image_url: newAsgImageUrl.value.trim(),
        guiding_questions: gQuestions,
        target_keywords: tKeywords,
        time_limit_seconds: 0
      })
    })
    if (res.ok) {
      newAsgTitle.value = ''
      newAsgSentence.value = ''
      newAsgPictureTopic.value = ''
      newAsgImageUrl.value = ''
      newAsgGuidingQuestionsText.value = ''
      newAsgGuidingQuestionsList.value = []
      newAsgTargetKeywordsText.value = ''
      newAsgDueDate.value = ''
      showCreateAssignmentModal.value = false
      notify('Homework assigned to classroom!', 'success')
      await selectClass(selectedClassId.value)
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to create assignment.', 'error')
    }
  } catch (err) {
    notify('Failed to create assignment: ' + err.message, 'error', 'mdi-alert-circle')
  } finally {
    isCreatingAsg.value = false
  }
}

const getStudentSubmissions = (studentId) => {
  return (gradebook.value.submissions || []).filter(s => s.student_id === studentId)
}

const getStudentAvgScore = (studentId) => {
  const subs = getStudentSubmissions(studentId)
  if (!subs.length) return 0
  const sum = subs.reduce((acc, s) => acc + (s.score_override ?? s.score ?? 0), 0)
  return sum / subs.length
}

const getAssignmentSubmissionsCount = (asgId) => {
  return new Set((gradebook.value.submissions || []).filter(s => s.assignment_id === asgId).map(s => s.student_id)).size
}

const showAssignmentReview = ref(false)
const reviewAssignment = ref(null)
const reviewSearch = ref('')
const reviewStatus = ref('All Students')
const assignmentReviewRows = computed(() => (gradebook.value.students || []).map(student => {
  const attempts = (gradebook.value.submissions || []).filter(s => s.assignment_id === reviewAssignment.value?.id && s.student_id === student.id).sort((a, b) => b.id - a.id)
  return { student, submission: attempts[0] || null, attempts: attempts.length, history: attempts }
}))
const filteredAssignmentReviewRows = computed(() => assignmentReviewRows.value.filter(row => {
  const query = reviewSearch.value.trim().toLowerCase()
  return `${row.student.name} ${row.student.email}`.toLowerCase().includes(query)
    && (reviewStatus.value === 'All Students' || Boolean(row.submission) === (reviewStatus.value === 'Submitted'))
}))
const openAssignmentReview = (assignment) => {
  reviewAssignment.value = assignment
  reviewSearch.value = ''
  reviewStatus.value = 'All Students'
  for (const sub of gradebook.value.submissions || []) feedbackInputs.value[sub.id] = sub.teacher_feedback || ''
  showAssignmentReview.value = true
}

const getAssignmentTitle = (asgId) => {
  const asg = (gradebook.value.assignments || []).find(a => a.id === asgId)
  return asg ? asg.title : 'Assignment'
}

const selectedStudentSubmissions = computed(() => {
  if (!selectedStudent.value) return []
  return getStudentSubmissions(selectedStudent.value.id)
})

const openStudentSubmissionsModal = (student) => {
  selectedStudent.value = student
  const subs = getStudentSubmissions(student.id)
  subs.forEach(s => {
    feedbackInputs.value[s.id] = s.teacher_feedback || ''
  })
  showSubmissionsModal.value = true
}

const saveFeedback = async (subId) => {
  try {
    const res = await fetch(`${props.backendUrl}/api/submissions/feedback`, {
      method: 'POST',
      headers: getTeacherAuthHeaders(),
      body: JSON.stringify({
        submission_id: subId,
        feedback: feedbackInputs.value[subId] || ''
      })
    })
    if (res.ok) {
      notify('Pedagogical feedback saved successfully!', 'success')
      await selectClass(selectedClassId.value)
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to save feedback.', 'error')
    }
  } catch (err) {
    notify('Failed to save feedback: ' + err.message, 'error', 'mdi-alert-circle')
  }
}

const copyJoinCode = (code) => {
  navigator.clipboard.writeText(code)
  notify(`Copied Join Code: ${code}`, 'info', 'mdi-content-copy')
}

onMounted(() => {
  fetchClasses()
})
</script>

<style scoped>
.bg-gradient-indigo {
  background: linear-gradient(135deg, #3f51b5 0%, #1a237e 100%);
}

.class-sidebar-sticky {
  position: sticky;
  top: 76px;
  max-height: calc(100vh - 96px);
  display: flex;
  flex-direction: column;
}

.class-list-scroll {
  overflow-y: auto;
  max-height: calc(100vh - 280px);
  padding-right: 2px;
}

.class-list-scroll::-webkit-scrollbar {
  width: 5px;
}

.class-list-scroll::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.class-list-scroll::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 4px;
}

.class-list-scroll::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}

.hover-item:hover {
  background-color: #f8fafc;
}
</style>
