<template>
  <div>
    <TeacherDashboard :backend-url="backendUrl" :user-id="userId" />
  </div>
</template>

<script setup>
import TeacherDashboard from '@/components/TeacherDashboard.vue'

defineProps({
  backendUrl: String,
  userId: Number
})
</script>
