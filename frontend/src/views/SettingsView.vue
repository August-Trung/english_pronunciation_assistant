<template>
  <SettingsTab
    :backend-url="backendUrl"
    :user-id="userId"
    :user-name="userName"
    :daily-goal="dailyGoal"
    @update-settings="$emit('update-settings', $event)"
  />
</template>

<script setup>
import SettingsTab from '@/components/SettingsTab.vue'

defineProps({
  backendUrl: String,
  userId: Number,
  userName: String,
  dailyGoal: Number
})

defineEmits(['update-settings'])
</script>
