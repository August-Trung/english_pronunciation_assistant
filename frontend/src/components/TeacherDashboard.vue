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
              <div class="d-flex align-center ga-2">
                <span class="text-h6 font-weight-black text-primary">{{ selectedClass.name }}</span>
                <v-chip color="indigo" size="small" variant="flat" class="font-weight-bold">
                  {{ selectedClass.grade_level }}
                </v-chip>
              </div>
              <div class="text-caption text-grey-darken-2 font-weight-bold d-flex align-center ga-2 mt-1">
                <span>Student Join Code:</span>
                <v-chip color="primary" size="small" variant="tonal" class="font-weight-mono font-weight-black" prepend-icon="mdi-key-variant">
                  {{ selectedClass.join_code }}
                </v-chip>
                <v-btn size="x-small" variant="text" icon="mdi-content-copy" title="Copy Join Code" @click="copyJoinCode(selectedClass.join_code)" />
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
              Gradebook Roster ({{ gradebook.students?.length || 0 }})
            </v-tab>
            <v-tab value="assignments" class="font-weight-black text-none" prepend-icon="mdi-clipboard-text-outline">
              Assignments ({{ gradebook.assignments?.length || 0 }})
            </v-tab>
          </v-tabs>

          <v-window v-model="activeTab">
            <!-- Tab 1: Gradebook Roster Table -->
            <v-window-item value="gradebook">
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
                  <tr v-for="std in gradebook.students" :key="std.id">
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
                    </td>
                  </tr>

                  <tr v-if="!gradebook.students?.length">
                    <td colspan="5" class="text-center pa-6 text-caption text-grey">
                      No students enrolled yet. Share join code <strong>{{ selectedClass.join_code }}</strong> with your class!
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

                    <v-chip color="teal" size="small" variant="flat" class="font-weight-bold">
                      Submissions: {{ getAssignmentSubmissionsCount(asg.id) }}/{{ gradebook.students?.length || 0 }}
                    </v-chip>
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
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  backendUrl: String,
  userId: Number
})

const toast = ref({ show: false, text: '', color: 'success', icon: 'mdi-check-circle' })
const notify = (text, color = 'success', icon = 'mdi-check-circle') => {
  toast.value = { show: true, text, color, icon }
}

const classes = ref([])
const selectedClassId = ref(null)
const activeTab = ref('gradebook')
const gradebook = ref({ classroom: null, students: [], assignments: [], submissions: [] })

const showCreateClassModal = ref(false)
const newClassName = ref('')
const newClassGrade = ref('Elementary (Grades 1 - 5)')
const isCreatingClass = ref(false)

const showCreateAssignmentModal = ref(false)
const newAsgTitle = ref('')
const newAsgSentence = ref('')
const newAsgDueDate = ref('')
const isCreatingAsg = ref(false)

const showSubmissionsModal = ref(false)
const selectedStudent = ref(null)
const feedbackInputs = ref({})

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
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/teacher/${props.userId || 1}`)
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
  isCreatingClass.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        teacher_id: props.userId || 1,
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
  isCreatingAsg.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/assignments/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        class_id: selectedClassId.value,
        teacher_id: props.userId || 1,
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
