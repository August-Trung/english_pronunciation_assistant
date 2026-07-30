<template>
  <v-dialog v-model="dialog" max-width="500" scrollable>
    <v-card rounded="lg">
      <v-card-title class="d-flex align-center justify-space-between flex-nowrap bg-primary text-white py-2 px-3">
        <div class="d-flex align-center ga-2 text-truncate mr-2">
          <v-icon color="white" size="small">mdi-account-circle-outline</v-icon>
          <span class="text-subtitle-2 text-sm-subtitle-1 font-weight-black text-truncate">USER PROFILE</span>
        </div>
        <v-btn icon="mdi-close" variant="text" size="small" color="white" class="flex-shrink-0" @click="dialog = false" />
      </v-card-title>

      <v-card-text class="pa-4">
        <!-- User Avatar & Info Header -->
        <div class="text-center mb-4">
          <v-avatar size="64" color="primary" class="mb-2 border border-2 elevation-2">
            <v-img v-if="userAvatar" :src="userAvatar" alt="Avatar" />
            <v-icon v-else size="large" color="white">mdi-account</v-icon>
          </v-avatar>

          <div class="text-h6 font-weight-black text-grey-darken-4 d-flex align-center justify-center ga-1">
            <span>{{ userName }}</span>
            <v-chip v-if="equippedBadgeTitle" size="x-small" color="primary" variant="flat" class="font-weight-black">
              {{ equippedBadgeTitle }}
            </v-chip>
          </div>

          <div class="text-caption text-grey-darken-1 font-weight-bold">
            <v-icon size="x-small" color="primary">mdi-email-outline</v-icon> {{ userEmail || 'Guest Learner Account' }}
          </div>
        </div>

        <!-- Metric Badges Row -->
        <v-row class="ma-0 mb-4 ga-2 text-center">
          <v-col class="pa-2 bg-blue-lighten-5 border rounded-lg">
            <div class="text-subtitle-1 font-weight-black text-primary">{{ streak }}d</div>
            <div class="text-caption text-grey-darken-1">Learning Streak</div>
          </v-col>
          <v-col class="pa-2 bg-amber-lighten-5 border rounded-lg">
            <div class="text-subtitle-1 font-weight-black text-amber-darken-4">{{ dailyGoal }} / day</div>
            <div class="text-caption text-grey-darken-1">Daily Target</div>
          </v-col>
        </v-row>

        <!-- Form Edit User Settings -->
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
          height="40"
          class="font-weight-black text-none"
          prepend-icon="mdi-content-save"
          :loading="isSaving"
          @click="saveProfile"
        >
          Save Changes
        </v-btn>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  backendUrl: String,
  userId: Number,
  userName: String,
  userEmail: String,
  userAvatar: String,
  equippedBadgeTitle: String,
  streak: Number,
  dailyGoal: Number
})

const emit = defineEmits(['update:modelValue', 'update-profile'])

const dialog = ref(props.modelValue)
const editName = ref(props.userName)
const editGoal = ref(props.dailyGoal)
const isSaving = ref(false)

watch(() => props.modelValue, (val) => {
  dialog.value = val
  if (val) {
    editName.value = props.userName
    editGoal.value = props.dailyGoal
  }
})

watch(dialog, (val) => {
  emit('update:modelValue', val)
})

const saveProfile = async () => {
  isSaving.value = true
  try {
    emit('update-profile', {
      userName: editName.value.trim() || props.userName,
      dailyGoal: editGoal.value
    })
    dialog.value = false
  } catch (err) {
    console.error('Error saving profile:', err)
  } finally {
    isSaving.value = false
  }
}
</script>
