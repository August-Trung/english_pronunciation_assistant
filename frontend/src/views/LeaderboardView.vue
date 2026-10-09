<template>
  <LeaderboardTab
    :backend-url="backendUrl"
    :current-user-id="userId"
  />
</template>

<script setup>
import LeaderboardTab from '@/components/LeaderboardTab.vue'

defineProps({
  backendUrl: String,
  userId: Number
})
</script>
