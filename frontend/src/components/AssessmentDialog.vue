<template>
  <v-dialog :model-value="Boolean(submission)" max-width="1000" scrollable @update:model-value="!$event && $emit('close')">
    <v-card v-if="submission">
      <v-card-title class="d-flex align-center justify-space-between">
        AI Assessment Details
        <v-btn icon="mdi-close" variant="text" aria-label="Close assessment" @click="$emit('close')" />
      </v-card-title>
      <v-card-text>
        <p class="font-weight-bold mb-3">Recorded Score: {{ submission.score_override ?? submission.score ?? 'Unavailable' }}/10</p>
        <p v-if="submission.score_override != null" class="mb-3">This score was adjusted by the educator. The original AI assessment appears below.</p>
        <audio v-if="submission.audio_url" controls :src="audioUrl" class="w-100 mb-3" />
        <SubmissionEvaluation :evaluation="submission.evaluation || {}" :transcript="submission.transcribed_text || ''" initially-expanded />
        <p v-if="submission.teacher_feedback" class="mt-3" style="white-space: pre-wrap">Educator Feedback: {{ submission.teacher_feedback }}</p>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>
<script setup>
import SubmissionEvaluation from './SubmissionEvaluation.vue'
defineProps({ submission: { type: Object, default: null }, audioUrl: { type: String, default: '' } })
defineEmits(['close'])
</script>
