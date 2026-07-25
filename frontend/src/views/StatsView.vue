<template>
  <StatsTab
    :backend-url="backendUrl"
    :user-id="userId"
    :history="history"
    :daily-goal="dailyGoal"
    @clear-history="$emit('clear-history')"
  />
</template>

<script setup>
import StatsTab from '@/components/StatsTab.vue'

defineProps({
  backendUrl: String,
  userId: Number,
  history: Array,
  dailyGoal: Number
})

defineEmits(['clear-history'])
</script>
