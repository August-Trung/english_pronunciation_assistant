<template>
  <PracticeTab
    :backend-url="backendUrl"
    :user-id="userId"
    @history-updated="$emit('history-updated')"
  />
</template>

<script setup>
import PracticeTab from '@/components/PracticeTab.vue'

defineProps({
  backendUrl: String,
  userId: Number
})

defineEmits(['history-updated'])
</script>
