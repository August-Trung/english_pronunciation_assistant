<template>
  <v-container fluid class="pa-0 max-width-600">
    <v-card border flat class="pa-4 bg-white rounded-lg elevation-1">
      <div class="text-center mb-4">
        <v-avatar size="72" color="primary" class="mb-2 border border-2 elevation-2">
          <v-img v-if="userAvatar" :src="userAvatar" alt="Avatar" />
          <v-icon v-else size="large" color="white">mdi-account</v-icon>
        </v-avatar>

        <div class="text-h6 font-weight-black text-grey-darken-4 d-flex align-center justify-center ga-1">
          <span>{{ formatDisplayName(userName) }}</span>
          <v-chip v-if="equippedBadgeTitle" size="x-small" color="primary" variant="flat" class="font-weight-black">
            {{ equippedBadgeTitle }}
          </v-chip>
        </div>

        <div class="text-caption text-grey-darken-1 font-weight-bold">
          <v-icon size="x-small" color="primary">mdi-email-outline</v-icon> {{ userEmail || 'Guest Learner Account (Unlinked)' }}
        </div>
      </div>

      <!-- Metrics -->
      <v-row class="ma-0 mb-4 ga-2 text-center">
        <v-col class="pa-3 bg-blue-lighten-5 border rounded-lg">
          <div class="text-subtitle-1 font-weight-black text-primary">{{ streak }}d</div>
          <div class="text-caption text-grey-darken-1">Learning Streak</div>
        </v-col>
        <v-col class="pa-3 bg-amber-lighten-5 border rounded-lg">
          <div class="text-subtitle-1 font-weight-black text-amber-darken-4">{{ dailyGoal }} / day</div>
          <div class="text-caption text-grey-darken-1">Daily Target</div>
        </v-col>
      </v-row>

      <!-- Edit Form -->
      <v-card border flat class="pa-3 bg-grey-lighten-5 rounded-lg mb-3">
        <div class="text-subtitle-2 font-weight-black text-secondary mb-2">Edit Profile Details:</div>
        <v-text-field
          v-model="editName"
          label="Full Name:"
          variant="outlined"
          density="comfortable"
          hide-details
          color="primary"
          class="mb-3"
        />

        <div class="d-flex align-center justify-space-between mb-1">
          <span class="text-caption font-weight-bold text-grey-darken-2">Daily Practice Goal:</span>
          <span class="text-subtitle-2 font-weight-black text-primary">{{ editGoal }} practices</span>
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
      </v-card>

      <v-btn
        color="primary"
        variant="flat"
        block
        height="44"
        class="font-weight-black text-none mb-3"
        prepend-icon="mdi-content-save"
        :loading="isSaving"
        @click="saveProfile"
      >
        Save Profile Changes
      </v-btn>

      <v-btn
        color="teal"
        variant="tonal"
        block
        height="44"
        class="font-weight-black text-none"
        prepend-icon="mdi-file-pdf-box"
        @click="showPdfReport = true"
      >
        Export Progress PDF Report (For Parents)
      </v-btn>
    </v-card>

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
import { ref, watch } from 'vue'
import PdfReportDialog from '@/components/PdfReportDialog.vue'

const showPdfReport = ref(false)

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

const formatDisplayName = (name) => {
  if (!name) return 'Học Sinh'
  if (name.startsWith('guest_')) {
    const num = name.replace('guest_', '')
    return `Học Sinh Khách #${num.slice(-5)}`
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
.max-width-600 {
  max-width: 600px;
  margin: 0 auto;
}
</style>
