<template>
  <HistoryTab
    :backend-url="backendUrl"
    :user-id="userId"
  />
</template>

<script setup>
import HistoryTab from '@/components/HistoryTab.vue'

defineProps({
  backendUrl: {
    type: String,
    required: true
  },
  userId: {
    type: Number,
    default: null
  }
})
</script>
