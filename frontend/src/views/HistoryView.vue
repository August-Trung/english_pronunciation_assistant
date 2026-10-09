<template>
  <HistoryTab
    :backend-url="backendUrl"
    :user-id="userId"
    :user-name="userName"
    :user-email="userEmail"
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
  },
  userName: {
    type: String,
    default: ''
  },
  userEmail: {
    type: String,
    default: ''
  }
})
</script>
