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
      <!-- Header Title Banner -->
      <v-card border flat class="pa-4 mb-4 bg-gradient-indigo text-white rounded-xl elevation-2">
        <div class="d-flex align-center justify-space-between flex-wrap ga-3">
          <div class="d-flex align-center ga-3">
            <v-avatar color="white" size="48" class="elevation-2">
              <v-icon color="indigo-darken-3" size="large">mdi-school-outline</v-icon>
            </v-avatar>
            <div>
              <div class="text-h6 font-weight-black tracking-tight">TEACHER HUB & GRADEBOOK</div>
              <div class="text-caption opacity-90 font-weight-medium">
                Manage classes, monitor student IPA scores, listen to Supabase audio recordings, & assign homework
              </div>
            </div>
          </div>

          <div class="d-flex align-center ga-2">
            <v-btn
              color="white"
              variant="flat"
              class="font-weight-black text-indigo-darken-3 text-none"
              prepend-icon="mdi-plus-box"
              @click="showCreateClassModal = true"
            >
              Create New Class
            </v-btn>
            <v-btn
              color="white"
              variant="outlined"
              size="small"
              class="font-weight-bold text-none"
              prepend-icon="mdi-logout"
              @click="showLogoutDialog = true"
            >
              Sign Out
            </v-btn>
          </div>
        </div>
      </v-card>

    <!-- Top KPI Cards -->
    <v-row class="mb-4" density="comfortable">
      <v-col cols="12" sm="4">
        <v-card border flat class="pa-3 bg-white rounded-lg d-flex align-center ga-3">
          <v-avatar color="indigo-lighten-5" size="42" class="text-indigo">
            <v-icon size="default">mdi-google-classroom</v-icon>
          </v-avatar>
          <div>
            <div class="text-caption font-weight-bold text-grey">Total Active Classes</div>
            <div class="text-h6 font-weight-black text-secondary">{{ classes.length }}</div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="4">
        <v-card border flat class="pa-3 bg-white rounded-lg d-flex align-center ga-3">
          <v-avatar color="teal-lighten-5" size="42" class="text-teal-darken-3">
            <v-icon size="default">mdi-account-group-outline</v-icon>
          </v-avatar>
          <div>
            <div class="text-caption font-weight-bold text-grey">Enrolled Students</div>
            <div class="text-h6 font-weight-black text-teal-darken-3">{{ totalStudentsCount }}</div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="4">
        <v-card border flat class="pa-3 bg-white rounded-lg d-flex align-center ga-3">
          <v-avatar color="purple-lighten-5" size="42" class="text-purple-darken-3">
            <v-icon size="default">mdi-file-document-check-outline</v-icon>
          </v-avatar>
          <div>
            <div class="text-caption font-weight-bold text-grey">Homework Submissions</div>
            <div class="text-h6 font-weight-black text-purple-darken-3">{{ totalSubmissionsCount }}</div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Main Content Area -->
    <v-row density="comfortable">
      <!-- Left Column: Class Selector Tabs -->
      <v-col cols="12" md="3">
        <v-card border flat class="pa-3 bg-white rounded-lg">
          <div class="text-subtitle-2 font-weight-black text-secondary mb-2 d-flex align-center justify-space-between">
            <span>MY CLASSES</span>
            <v-btn icon="mdi-refresh" variant="text" density="compact" size="x-small" @click="fetchClasses" />
          </div>

          <v-list density="compact" class="pa-0">
            <v-list-item
              v-for="cls in classes"
              :key="cls.id"
              :active="selectedClassId === cls.id"
              active-color="primary"
              class="rounded-lg mb-1 border"
              @click="selectClass(cls.id)"
            >
              <template #prepend>
                <v-avatar color="indigo-lighten-5" size="32" class="mr-2 text-indigo font-weight-black text-caption">
                  {{ cls.name.slice(0, 2).toUpperCase() }}
                </v-avatar>
              </template>
              <v-list-item-title class="font-weight-black text-body-2">{{ cls.name }}</v-list-item-title>
              <v-list-item-subtitle class="text-caption d-flex align-center ga-1">
                <span>Code:</span>
                <v-chip size="x-small" color="primary" variant="flat" class="font-weight-mono font-weight-black" style="height: 16px;">
                  {{ cls.join_code }}
                </v-chip>
              </v-list-item-subtitle>
            </v-list-item>

            <div v-if="!classes.length" class="text-center pa-4 text-caption text-grey">
              No classes created yet. Click "Create New Class" to start!
            </div>
          </v-list>
        </v-card>
      </v-col>

      <!-- Right Column: Gradebook & Assignments for Selected Class -->
      <v-col cols="12" md="9">
        <v-card v-if="selectedClass" border flat class="pa-4 bg-white rounded-lg">
          <!-- Class Header Banner -->
          <div class="d-flex align-center justify-space-between flex-wrap ga-2 border-b pb-3 mb-3">
            <div>
              <div class="d-flex align-center ga-2 flex-wrap">
                <span class="text-h6 font-weight-black text-primary">{{ selectedClass.name }}</span>
                <v-chip color="indigo" size="small" variant="flat" class="font-weight-bold">
                  {{ selectedClass.grade_level }}
                </v-chip>
                <v-btn icon="mdi-pencil-outline" size="x-small" color="primary" variant="tonal" title="Edit Class Information" @click="openEditClassModal" />
                <v-btn icon="mdi-delete-outline" size="x-small" color="error" variant="tonal" title="Delete Classroom" @click="showDeleteClassModal = true" />
              </div>
              <div class="text-caption text-grey-darken-2 font-weight-bold d-flex align-center flex-wrap ga-2 mt-1">
                <span>Student Join Code:</span>
                <v-chip color="primary" size="small" variant="tonal" class="font-weight-mono font-weight-black" prepend-icon="mdi-key-variant">
                  {{ selectedClass.join_code }}
                </v-chip>

                <!-- Full Domain Link & QR Code Buttons -->
                <v-btn size="small" color="primary" variant="outlined" class="font-weight-bold text-none" prepend-icon="mdi-link-variant" @click="copyFullClassLink(selectedClass.join_code)">
                  Copy Full Link
                </v-btn>

                <v-btn size="small" color="indigo-darken-2" variant="flat" class="font-weight-bold text-none" prepend-icon="mdi-qrcode" @click="openQrPosterModal(selectedClass)">
                  Show Class QR Code
                </v-btn>
              </div>
            </div>

            <div class="d-flex align-center ga-2">
              <v-btn
                color="secondary"
                variant="flat"
                density="comfortable"
                class="font-weight-bold text-caption text-none"
                prepend-icon="mdi-send-outline"
                @click="showCreateAssignmentModal = true"
              >
                1-Click Assign Homework
              </v-btn>
            </div>
          </div>

          <!-- Class Tabs: Gradebook Roster vs Assignments List -->
          <v-tabs v-model="activeTab" color="primary" density="compact" class="mb-3">
            <v-tab value="gradebook" class="font-weight-black text-none" prepend-icon="mdi-table-account">
              Gradebook Roster ({{ filteredStudents.length }})
            </v-tab>
            <v-tab value="assignments" class="font-weight-black text-none" prepend-icon="mdi-clipboard-text-outline">
              Assignments ({{ gradebook.assignments?.length || 0 }})
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
                          Review Audio
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
                    <div>
                      <div class="text-subtitle-2 font-weight-black text-primary">{{ asg.title }}</div>
                      <div class="text-caption font-weight-bold text-grey-darken-3 font-italic mt-0.5">
                        "{{ asg.topic_sentence }}"
                      </div>
                      <div class="text-caption text-grey mt-1">
                        Due Date: {{ asg.due_date || 'No deadline' }} • Created: {{ asg.created_at }}
                      </div>
                    </div>

                    <div class="d-flex align-center ga-2">
                      <v-btn size="x-small" icon="mdi-pencil-outline" color="primary" variant="tonal" title="Edit Assignment" @click="openEditAssignmentModal(asg)" />
                      <v-btn size="x-small" icon="mdi-delete-outline" color="error" variant="tonal" title="Delete Assignment" @click="confirmDeleteAssignment(asg)" />
                      <v-chip color="teal" size="small" variant="flat" class="font-weight-bold">
                        Submissions: {{ getAssignmentSubmissionsCount(asg.id) }}/{{ gradebook.students?.length || 0 }}
                      </v-chip>
                    </div>
                  </div>
                </v-card>

                <div v-if="!gradebook.assignments?.length" class="text-center pa-6 text-caption text-grey border rounded-lg">
                  No assignments posted for this class yet. Click "1-Click Assign Homework" above!
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
          :items="['Elementary (Grades 1 - 5)', 'Middle School (Grades 6 - 9)', 'High School & IELTS (Grades 10 - 12)']"
          label="Grade Level Category:"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          prepend-inner-icon="mdi-notebook"
        />

        <v-card-actions class="px-0 pb-0">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showCreateClassModal = false">Cancel</v-btn>
          <v-btn color="primary" variant="flat" class="text-none font-weight-bold" :loading="isCreatingClass" @click="submitCreateClass">
            Generate Class & Join Code
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
          :items="['Elementary (Grades 1 - 5)', 'Middle School (Grades 6 - 9)', 'High School & IELTS (Grades 10 - 12)']"
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
    <v-dialog v-model="showEditAssignmentModal" max-width="500">
      <v-card border rounded="lg" class="pa-4">
        <div class="text-subtitle-1 font-weight-black text-primary mb-3 d-flex align-center ga-2">
          <v-icon color="primary">mdi-pencil</v-icon>
          <span>Edit Homework Assignment</span>
        </div>

        <v-text-field
          v-model="editAsgTitle"
          label="Assignment Title:"
          variant="outlined"
          density="comfortable"
          class="mb-2"
          prepend-inner-icon="mdi-format-title"
        />

        <v-textarea
          v-model="editAsgSentence"
          label="Model Reading Sentence:"
          variant="outlined"
          density="comfortable"
          rows="3"
          class="mb-2"
          prepend-inner-icon="mdi-subtitles"
        />

        <v-text-field
          v-model="editAsgDueDate"
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

    <!-- Modal: 1-Click Assignment Creation -->
    <v-dialog v-model="showCreateAssignmentModal" max-width="500">
      <v-card border rounded="lg" class="pa-4">
        <div class="text-subtitle-1 font-weight-black text-secondary mb-3 d-flex align-center ga-2">
          <v-icon color="secondary">mdi-send</v-icon>
          <span>Assign Homework to {{ selectedClass?.name }}</span>
        </div>

        <v-text-field
          v-model="newAsgTitle"
          label="Assignment Title:"
          placeholder="Example: Unit 3 - Practice Daily Routine Sentence"
          variant="outlined"
          density="comfortable"
          class="mb-2"
          prepend-inner-icon="mdi-format-title"
        />

        <v-textarea
          v-model="newAsgSentence"
          label="Model Reading Sentence:"
          placeholder="Example: Learning a new language opens up a world of opportunities."
          variant="outlined"
          density="comfortable"
          rows="3"
          class="mb-2"
          prepend-inner-icon="mdi-subtitles"
        />

        <v-text-field
          v-model="newAsgDueDate"
          label="Due Date (Optional):"
          placeholder="Example: 2026-08-05"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          prepend-inner-icon="mdi-calendar-clock"
        />

        <v-card-actions class="px-0 pb-0">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showCreateAssignmentModal = false">Cancel</v-btn>
          <v-btn color="secondary" variant="flat" class="text-none font-weight-bold" :loading="isCreatingAsg" @click="submitCreateAssignment">
            Assign Homework
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Modal: Review Student Audio Submissions from Supabase -->
    <v-dialog v-model="showSubmissionsModal" max-width="650">
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
              <v-chip color="success" size="small" variant="flat" class="font-weight-black">
                Score: {{ (sub.score_override ?? sub.score).toFixed(1) }}/10
              </v-chip>
            </div>

            <div class="text-caption font-italic text-grey-darken-3 bg-white pa-2 rounded border mb-2">
              "{{ sub.transcribed_text }}"
            </div>

            <!-- Supabase Audio Stream Player -->
            <div v-if="sub.audio_url" class="bg-white pa-2 rounded border d-flex align-center ga-2 mb-2">
              <v-icon color="primary">mdi-volume-high</v-icon>
              <audio controls :src="sub.audio_url" class="w-100" style="height: 32px;" />
            </div>
            <div v-else class="text-caption text-warning font-weight-bold mb-2">
              <v-icon size="x-small">mdi-alert</v-icon> Audio file processing on Supabase
            </div>

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
    </div>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  backendUrl: String,
  userId: Number
})

const router = useRouter()

const activeUserRole = ref(localStorage.getItem('user_role') || 'student')
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

const handleTeacherSignOut = () => {
  activeUserRole.value = 'student'
  localStorage.setItem('user_role', 'student')
  localStorage.removeItem('user_id')
  loginEmail.value = ''
  loginPassword.value = ''
  notify('Signed out from Teacher Hub.', 'info', 'mdi-logout')
  router.push('/')
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
      activeUserRole.value = data.user.role || 'teacher'
      localStorage.setItem('user_role', data.user.role || 'teacher')
      if (data.user?.id) {
        localTeacherId.value = data.user.id
        localStorage.setItem('user_id', data.user.id)
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

const classes = ref([])
const selectedClassId = ref(null)
const activeTab = ref('gradebook')
const gradebook = ref({ classroom: null, students: [], assignments: [], submissions: [] })

const showCreateClassModal = ref(false)
const newClassName = ref('')
const newClassGrade = ref('Elementary (Grades 1 - 5)')
const isCreatingClass = ref(false)

const showQrModal = ref(false)
const qrClass = ref(null)

const getFullClassLink = (joinCode) => {
  const origin = window.location.origin || 'https://fluent.augusttrung.com'
  return `${origin}/homework?join_code=${joinCode}`
}

const getQrCodeUrl = (joinCode) => {
  const fullLink = getFullClassLink(joinCode)
  return `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(fullLink)}`
}

const exportGradebookCSV = () => {
  if (!filteredStudents.value || filteredStudents.value.length === 0) {
    notify('No student roster records to export.', 'warning', 'mdi-alert-circle')
    return
  }

  const selectedClassName = selectedClass.value ? selectedClass.value.name : 'Class'
  const headers = ['"Họ và Tên"', '"Email"', '"Số Bài Nộp"', '"Điểm Trung Bình (10)"', '"Đánh Giá Xếp Loại"']
  
  const rows = filteredStudents.value.map(std => {
    const name = `"${(std.name || 'Học sinh').replace(/"/g, '""')}"`
    const email = `"${(std.email || '--').replace(/"/g, '""')}"`
    const count = std.submission_count || std.total_submissions || 0
    const scoreNum = std.avg_score || 0
    const scoreVal = scoreNum.toFixed(1).replace('.', ',')
    let tier = '"Cần cố gắng"'
    if (scoreNum >= 8.5) tier = '"Xuất sắc"'
    else if (scoreNum >= 7.0) tier = '"Giỏi"'
    else if (scoreNum >= 5.0) tier = '"Khá"'
    
    return [name, email, count, `"${scoreVal}"`, tier].join(',')
  })

  const csvContent = '\uFEFF' + [headers.join(','), ...rows].join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  const dateStr = new Date().toISOString().slice(0, 10)
  link.setAttribute('href', url)
  link.setAttribute('download', `BangDiem_${selectedClassName.replace(/[^a-zA-Z0-9]/g, '_')}_${dateStr}.csv`)
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
const newAsgTitle = ref('')
const newAsgSentence = ref('')
const newAsgDueDate = ref('')
const isCreatingAsg = ref(false)

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
  editClassGrade.value = selectedClass.value.grade_level
  showEditClassModal.value = true
}

const submitEditClass = async () => {
  if (!editClassName.value.trim() || !selectedClassId.value) return
  isUpdatingClass.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/${selectedClassId.value}/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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
      method: 'DELETE'
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
      headers: { 'Content-Type': 'application/json' },
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

const openEditAssignmentModal = (asg) => {
  editingAsg.value = asg
  editAsgTitle.value = asg.title
  editAsgSentence.value = asg.topic_sentence
  editAsgDueDate.value = asg.due_date || ''
  showEditAssignmentModal.value = true
}

const submitEditAssignment = async () => {
  if (!editingAsg.value || !editAsgTitle.value.trim()) return
  isUpdatingAsg.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/assignments/${editingAsg.value.id}/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: editAsgTitle.value.trim(),
        topic_sentence: editAsgSentence.value.trim(),
        due_date: editAsgDueDate.value.trim()
      })
    })
    if (res.ok) {
      showEditAssignmentModal.value = false
      notify('Assignment updated successfully!', 'success')
      await selectClass(selectedClassId.value)
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
      method: 'DELETE'
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
    const res = await fetch(`${props.backendUrl}/api/classes/teacher/${tid}`)
    if (res.ok) {
      const data = await res.json()
      classes.value = data.classes || []
      if (classes.value.length && !selectedClassId.value) {
        selectClass(classes.value[0].id)
      }
    }
  } catch (err) {
    console.error('Fetch classes error:', err)
  }
}

const selectClass = async (classId) => {
  selectedClassId.value = classId
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/${classId}/gradebook`)
    if (res.ok) {
      gradebook.value = await res.json()
    }
  } catch (err) {
    console.error('Fetch gradebook error:', err)
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
      headers: { 'Content-Type': 'application/json' },
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
    }
  } catch (err) {
    notify('Failed to create class: ' + err.message, 'error', 'mdi-alert-circle')
  } finally {
    isCreatingClass.value = false
  }
}

const submitCreateAssignment = async () => {
  if (!newAsgTitle.value.trim() || !newAsgSentence.value.trim()) return
  const tid = getActiveTeacherId()
  if (!tid) {
    notify('Please sign in as a teacher to assign homework.', 'warning', 'mdi-school')
    return
  }
  isCreatingAsg.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/assignments/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        class_id: selectedClassId.value,
        teacher_id: tid,
        title: newAsgTitle.value.trim(),
        topic_sentence: newAsgSentence.value.trim(),
        due_date: newAsgDueDate.value.trim()
      })
    })
    if (res.ok) {
      newAsgTitle.value = ''
      newAsgSentence.value = ''
      newAsgDueDate.value = ''
      showCreateAssignmentModal.value = false
      notify('Homework assigned to classroom!', 'success')
      await selectClass(selectedClassId.value)
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
  return (gradebook.value.submissions || []).filter(s => s.assignment_id === asgId).length
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
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        submission_id: subId,
        feedback: feedbackInputs.value[subId] || ''
      })
    })
    if (res.ok) {
      notify('Pedagogical feedback saved successfully!', 'success')
      await selectClass(selectedClassId.value)
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
</style>
