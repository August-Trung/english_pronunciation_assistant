<template>
  <v-container fluid class="pa-0 max-width-1100">
    <!-- Header Banner -->
    <v-card border flat class="pa-3 pa-sm-4 mb-4 text-white rounded-lg" style="background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);">
      <div class="d-flex align-center ga-3">
        <v-avatar color="white" size="44" class="elevation-1">
          <v-icon color="blue-darken-3" size="default">mdi-account-circle</v-icon>
        </v-avatar>
        <div>
          <div class="text-subtitle-1 text-sm-h6 font-weight-black tracking-tight leading-tight">
            STUDENT PROFILE & SETTINGS
          </div>
          <div class="text-caption text-blue-lighten-4">
            Manage your personal learning parameters, daily goals, and parent progress reports
          </div>
        </div>
      </div>
    </v-card>

    <v-row class="ma-0 ga-3">
      <!-- Left Column: User Identity & Summary Card (Cols 12, md 5) -->
      <v-col cols="12" md="5" class="pa-0">
        <v-card border flat class="pa-4 bg-white rounded-lg h-100 d-flex flex-column justify-space-between">
          <div class="text-center mb-4">
            <v-avatar size="80" color="primary" class="mb-3 border border-2 elevation-2">
              <v-img v-if="userAvatar" :src="userAvatar" alt="Avatar" />
              <v-icon v-else size="x-large" color="white">mdi-account</v-icon>
            </v-avatar>

            <div class="text-h6 font-weight-black text-grey-darken-4 d-flex align-center justify-center ga-1">
              <span>{{ formatDisplayName(userName) }}</span>
              <v-chip v-if="equippedBadgeTitle" size="x-small" color="primary" variant="flat" class="font-weight-black">
                {{ equippedBadgeTitle }}
              </v-chip>
            </div>

            <div class="text-caption text-grey-darken-1 font-weight-bold mb-3">
              <v-icon size="x-small" color="primary">mdi-email-outline</v-icon> {{ userEmail || 'Guest Learner Account (Unlinked)' }}
            </div>

            <!-- Classroom Affiliation Status -->
            <div class="d-flex align-center justify-center mb-4">
              <v-chip
                v-if="enrolledClass"
                color="indigo-darken-1"
                variant="tonal"
                size="small"
                class="font-weight-black"
                prepend-icon="mdi-google-classroom"
              >
                Classroom Student: {{ enrolledClass.class_name }} ({{ enrolledClass.join_code }})
              </v-chip>
              <v-chip
                v-else
                color="teal-darken-1"
                variant="tonal"
                size="small"
                class="font-weight-black"
                prepend-icon="mdi-earth"
              >
                Independent Learner
              </v-chip>
            </div>

            <!-- Metrics -->
            <v-row class="ma-0 ga-2 text-center">
              <v-col class="pa-3 bg-blue-lighten-5 border rounded-lg">
                <div class="text-subtitle-1 font-weight-black text-primary">{{ streak }}d</div>
                <div class="text-caption text-grey-darken-1">Learning Streak</div>
              </v-col>
              <v-col class="pa-3 bg-amber-lighten-5 border rounded-lg">
                <div class="text-subtitle-1 font-weight-black text-amber-darken-4">{{ dailyGoal }} / day</div>
                <div class="text-caption text-grey-darken-1">Daily Target</div>
              </v-col>
            </v-row>
          </div>

          <v-btn
            color="teal"
            variant="tonal"
            block
            height="44"
            class="font-weight-black text-none mt-2"
            prepend-icon="mdi-file-pdf-box"
            @click="showPdfReport = true"
          >
            Export Progress PDF Report (For Parents)
          </v-btn>
        </v-card>
      </v-col>

      <!-- Right Column: Settings Form & Goals (Cols 12, md 7) -->
      <v-col cols="12" md="7" class="pa-0">
        <v-card border flat class="pa-4 bg-white rounded-lg h-100 d-flex flex-column justify-space-between">
          <div>
            <div class="text-subtitle-2 font-weight-black text-secondary mb-3 d-flex align-center ga-1 border-b pb-2">
              <v-icon size="small" color="secondary">mdi-account-cog-outline</v-icon>
              <span>ACCOUNT PARAMETERS & DAILY GOALS</span>
            </div>

            <div class="mb-4">
              <div class="text-caption font-weight-bold text-grey-darken-2 mb-1">Display Name:</div>
              <v-text-field
                v-model="editName"
                label="Full Name:"
                variant="outlined"
                density="comfortable"
                hide-details
                color="primary"
                class="mb-3"
              />
            </div>

            <div class="mb-4 pa-3 bg-grey-lighten-5 rounded-lg border">
              <div class="d-flex align-center justify-space-between mb-1">
                <span class="text-caption font-weight-bold text-grey-darken-2">Daily Practice Goal:</span>
                <span class="text-subtitle-2 font-weight-black text-primary">{{ editGoal }} practices / day</span>
              </div>
              <v-slider
                v-model="editGoal"
                :min="1"
                :max="20"
                :step="1"
                color="primary"
                hide-details
                density="compact"
              />
              <div class="text-caption text-grey mt-1" style="font-size: 11px;">
                Consistent daily sessions reinforce muscle memory and improve speech intonation faster.
              </div>
            </div>

            <div class="pa-3 bg-blue-lighten-5 rounded-lg border border-blue text-caption text-grey-darken-3 d-flex align-center ga-2">
              <v-icon color="primary" size="small">mdi-shield-check</v-icon>
              <span>Your progress and evaluation scores are automatically backed up to your learner profile.</span>
            </div>
          </div>

          <v-btn
            color="primary"
            variant="flat"
            block
            height="44"
            class="font-weight-black text-none mt-4"
            prepend-icon="mdi-content-save"
            :loading="isSaving"
            @click="saveProfile"
          >
            Save Profile Changes
          </v-btn>
        </v-card>
      </v-col>
    </v-row>

    <!-- PDF Report Dialog -->
    <PdfReportDialog
      v-model="showPdfReport"
      :user-id="userId"
      :user-name="userName"
      :equipped-badge-title="equippedBadgeTitle"
      :streak="streak"
    />
  </v-container>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import PdfReportDialog from '@/components/PdfReportDialog.vue'

const showPdfReport = ref(false)
const enrolledClass = ref(null)

const props = defineProps({
  backendUrl: String,
  userId: Number,
  userName: String,
  userEmail: String,
  userAvatar: String,
  equippedBadgeTitle: String,
  streak: Number,
  dailyGoal: Number
})

const emit = defineEmits(['update-settings'])

const editName = ref(props.userName)
const editGoal = ref(props.dailyGoal)
const isSaving = ref(false)

const fetchStudentClassAffiliation = async () => {
  const uid = props.userId || Number(localStorage.getItem('user_id'))
  if (!uid || !props.backendUrl) return
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/student/${uid}`)
    if (res.ok) {
      const data = await res.json()
      if (data.classes?.length) {
        enrolledClass.value = data.classes[0]
      } else {
        enrolledClass.value = null
      }
    }
  } catch (e) {
    console.error('Fetch student class affiliation error:', e)
  }
}

onMounted(() => {
  fetchStudentClassAffiliation()
})

watch(() => props.userId, () => {
  fetchStudentClassAffiliation()
})

const formatDisplayName = (name) => {
  if (!name) return 'Learner'
  if (name.startsWith('guest_')) {
    const num = name.replace('guest_', '')
    return `Guest Learner #${num.slice(-5)}`
  }
  return name
}

watch(() => props.userName, (val) => editName.value = val)
watch(() => props.dailyGoal, (val) => editGoal.value = val)

const saveProfile = async () => {
  isSaving.value = true
  try {
    emit('update-settings', {
      userName: editName.value.trim() || props.userName,
      dailyGoal: editGoal.value
    })
  } catch (err) {
    console.error('Save profile error:', err)
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.max-width-1100 {
  max-width: 1100px;
  margin: 0 auto;
}
</style>
