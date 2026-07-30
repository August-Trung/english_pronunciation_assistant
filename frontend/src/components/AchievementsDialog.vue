<template>
  <v-dialog v-model="dialog" max-width="500" scrollable>
    <v-card rounded="lg">
      <v-card-title class="d-flex align-center justify-space-between flex-nowrap bg-primary text-white py-2 px-3">
        <div class="d-flex align-center ga-2 text-truncate mr-2">
          <v-icon color="amber" size="small">mdi-trophy-award</v-icon>
          <span class="text-subtitle-2 text-sm-subtitle-1 font-weight-black text-truncate">ACHIEVEMENTS & BADGES</span>
        </div>
        <v-btn icon="mdi-close" variant="text" size="small" color="white" class="flex-shrink-0" @click="dialog = false" />
      </v-card-title>

      <v-card-text class="pa-4">
        <div class="text-caption text-grey-darken-1 mb-3">
          Unlock badges by practicing consistently. You can <strong>Equip</strong> a badge title to display next to your name on the Leaderboard!
        </div>

        <div v-if="isLoading" class="text-center py-6">
          <v-progress-circular indeterminate color="primary" size="32" />
        </div>

        <v-row v-else class="ma-0 ga-2">
          <v-col v-for="item in achievements" :key="item.code" cols="12" class="pa-1">
            <v-card
              border
              flat
              class="pa-3 rounded-lg d-flex align-center justify-space-between ga-2"
              :class="item.unlocked ? 'bg-white border-primary' : 'bg-grey-lighten-4 opacity-70'"
            >
              <div class="d-flex align-center ga-3 overflow-hidden">
                <v-avatar :color="item.unlocked ? item.color : 'grey-lighten-2'" size="36" class="elevation-1 flex-shrink-0">
                  <v-icon :color="item.unlocked ? 'white' : 'grey-darken-1'" size="small">{{ item.icon }}</v-icon>
                </v-avatar>
                <div class="overflow-hidden">
                  <div class="text-caption text-sm-subtitle-2 font-weight-black d-flex align-center flex-wrap ga-1">
                    <span :class="item.unlocked ? 'text-grey-darken-4' : 'text-grey'">{{ item.title }}</span>
                    <v-chip v-if="item.equipped" size="x-small" color="success" variant="flat" class="font-weight-black" style="font-size: 9px;">
                      Equipped
                    </v-chip>
                  </div>
                  <div class="text-caption text-grey-darken-1" style="font-size: 11px; line-height: 1.25;">{{ item.description }}</div>
                </div>
              </div>

              <!-- Equip / Unequip Action -->
              <div v-if="item.unlocked" class="flex-shrink-0">
                <v-btn
                  v-if="item.equipped"
                  color="grey"
                  variant="outlined"
                  size="small"
                  class="font-weight-bold text-none"
                  @click="toggleEquip('')"
                >
                  Unequip
                </v-btn>
                <v-btn
                  v-else
                  color="primary"
                  variant="flat"
                  size="small"
                  class="font-weight-bold text-none"
                  @click="toggleEquip(item.code)"
                >
                  Equip
                </v-btn>
              </div>
              <div v-else class="text-caption text-grey font-weight-bold flex-shrink-0 d-flex align-center ga-1">
                <v-icon size="x-small">mdi-lock-outline</v-icon> Locked
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  backendUrl: String,
  userId: Number
})

const emit = defineEmits(['update:modelValue', 'badge-updated'])

const dialog = ref(props.modelValue)
const achievements = ref([])
const isLoading = ref(false)

watch(() => props.modelValue, (val) => {
  dialog.value = val
  if (val && props.userId) {
    fetchAchievements()
  }
})

watch(dialog, (val) => {
  emit('update:modelValue', val)
})

const fetchAchievements = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/users/${props.userId}/achievements`)
    if (res.ok) {
      achievements.value = await res.json()
    }
  } catch (err) {
    console.error('Error fetching achievements:', err)
  } finally {
    isLoading.value = false
  }
}

const toggleEquip = async (code) => {
  try {
    const res = await fetch(`${props.backendUrl}/api/users/${props.userId}/equip-badge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ badge_code: code })
    })
    if (res.ok) {
      await fetchAchievements()
      emit('badge-updated')
    }
  } catch (err) {
    console.error('Error equipping badge:', err)
  }
}
</script>
