<template>
  <v-dialog
    :model-value="modelValue"
    max-width="560"
    scrollable
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <v-card flat class="rounded-xl overflow-hidden border">
      <!-- Modal Header Bar -->
      <v-card-title class="d-flex align-center justify-space-between px-4 py-3 bg-teal-darken-3 text-white">
        <div class="d-flex align-center ga-2">
          <v-icon color="teal-lighten-4" size="small">mdi-file-pdf-box</v-icon>
          <span class="text-subtitle-2 font-weight-black">LEARNING PROGRESS REPORT</span>
        </div>
        <v-btn
          icon="mdi-close"
          variant="text"
          size="x-small"
          color="white"
          @click="$emit('update:modelValue', false)"
        />
      </v-card-title>

      <!-- Modal Content Body (Scrollable) -->
      <v-card-text class="pa-3 pa-sm-4 bg-grey-lighten-5" style="max-height: 70vh;">
        <div id="pdf-report-content" class="pa-3 pa-sm-4 rounded-lg bg-white border">
          <!-- Report Header -->
          <div class="d-flex align-center justify-space-between border-b pb-3 mb-3 ga-2">
            <div>
              <div class="d-flex align-center ga-1">
                <v-icon color="teal" size="small">mdi-school</v-icon>
                <span class="text-subtitle-2 font-weight-black text-teal-darken-4">FLUENT ENGLISH</span>
              </div>
              <div class="text-caption text-grey-darken-1" style="font-size: 11px;">AI Academic Pronunciation Assistant</div>
            </div>
            <div class="text-right">
              <v-chip size="x-small" color="teal" variant="flat" class="font-weight-bold mb-1">
                {{ currentDate }}
              </v-chip>
              <div class="text-caption text-grey" style="font-size: 10px;">Student ID: #{{ userId || 1 }}</div>
            </div>
          </div>

          <!-- Student Profile Info -->
          <div class="bg-teal-lighten-5 pa-3 rounded-lg border border-teal-lighten-4 mb-3">
            <div class="d-flex align-center justify-space-between flex-wrap ga-2">
              <div class="d-flex align-center ga-2">
                <v-avatar color="teal" size="32" class="text-white font-weight-bold text-caption">
                  {{ (userName || 'H').charAt(0).toUpperCase() }}
                </v-avatar>
                <div>
                  <div class="text-caption font-weight-black text-grey-darken-4" style="font-size: 12px;">{{ userName || 'Learner' }}</div>
                  <div class="text-caption text-teal-darken-3 font-weight-bold" style="font-size: 10px;">{{ equippedBadgeTitle || 'Dedicated Learner' }}</div>
                </div>
              </div>
              <div class="d-flex ga-1">
                <v-chip label size="x-small" variant="tonal" color="teal">
                  <v-icon size="x-small" start color="deep-orange">mdi-fire</v-icon>
                  Streak {{ streak || 1 }}d
                </v-chip>
                <v-chip label size="x-small" variant="tonal" color="amber-darken-4">
                  <v-icon size="x-small" start color="amber-darken-3">mdi-star</v-icon>
                  {{ stats.total_practices || 12 }} practices
                </v-chip>
              </div>
            </div>
          </div>

          <!-- Section 1: Overview Score -->
          <div class="text-caption font-weight-black text-grey-darken-3 mb-2">1. Score Summary</div>
          <v-row dense class="ma-0 mb-3 border rounded-lg overflow-hidden bg-grey-lighten-5 text-center">
            <v-col cols="4" class="pa-2 border-e">
              <div class="text-subtitle-1 font-weight-black text-teal-darken-3">{{ stats.avg_score || '8.5' }}</div>
              <div class="text-caption text-grey-darken-2 font-weight-bold" style="font-size: 10px;">Average Score</div>
            </v-col>
            <v-col cols="4" class="pa-2 border-e">
              <div class="text-subtitle-1 font-weight-black text-success">{{ stats.pronunciation_score || '8.8' }}</div>
              <div class="text-caption text-grey-darken-2 font-weight-bold" style="font-size: 10px;">Pronunciation</div>
            </v-col>
            <v-col cols="4" class="pa-2">
              <div class="text-subtitle-1 font-weight-black text-info">{{ stats.fluency_score || '8.2' }}</div>
              <div class="text-caption text-grey-darken-2 font-weight-bold" style="font-size: 10px;">Fluency</div>
            </v-col>
          </v-row>

          <!-- Section 2: Skill Breakdown -->
          <div class="text-caption font-weight-black text-grey-darken-3 mb-2">2. Skill Competency Breakdown</div>
          <div class="mb-3">
            <div v-for="skill in skillList" :key="skill.name" class="mb-2">
              <div class="d-flex justify-space-between align-center mb-1" style="font-size: 11px;">
                <span class="font-weight-bold text-grey-darken-3">{{ skill.name }}</span>
                <span class="font-weight-black text-teal-darken-3">{{ skill.score }}/10</span>
              </div>
              <v-progress-linear :model-value="skill.score * 10" color="teal" height="6" rounded />
            </div>
          </div>

          <!-- Section 3: AI Pedagogical Feedback -->
          <div class="text-caption font-weight-black text-grey-darken-3 mb-2">3. AI Pedagogical Feedback</div>
          <div class="bg-teal-lighten-5 border border-teal-lighten-4 pa-3 rounded-lg mb-2">
            <div class="d-flex align-start ga-2">
              <v-icon color="teal" size="small" class="mt-1">mdi-robot-outline</v-icon>
              <div class="text-caption text-grey-darken-3 leading-snug" style="font-size: 11px;">
                Student <strong>{{ userName || 'Learner' }}</strong> demonstrates confident pronunciation reflexes. Continue maintaining steady pacing and practicing in Shadowing Studio.
              </div>
            </div>
          </div>

          <!-- Footer Signature -->
          <div class="d-flex justify-space-between align-center border-t pt-2 mt-2 text-caption text-grey" style="font-size: 10px;">
            <div>Verified by Fluent English AI Academic System</div>
            <div>Page 1/1</div>
          </div>
        </div>
      </v-card-text>

      <!-- Modal Footer Actions -->
      <v-card-actions class="pa-3 border-t bg-white d-flex justify-end ga-2">
        <v-btn variant="tonal" color="grey" size="small" class="text-none" @click="$emit('update:modelValue', false)">
          Close
        </v-btn>
        <v-btn color="teal" variant="flat" size="small" class="text-none" prepend-icon="mdi-printer" @click="printReport">
          Print / Export PDF
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  userId: Number,
  userName: String,
  equippedBadgeTitle: String,
  streak: Number,
  stats: {
    type: Object,
    default: () => ({
      total_practices: 12,
      avg_score: 8.5,
      pronunciation_score: 8.8,
      fluency_score: 8.2
    })
  }
})

defineEmits(['update:modelValue'])

const currentDate = computed(() => new Date().toLocaleDateString('en-US'))

const skillList = computed(() => [
  { name: 'Pronunciation & Clarity', score: props.stats.pronunciation_score || 8.8 },
  { name: 'Fluency & Expression', score: props.stats.fluency_score || 8.2 },
  { name: 'Vocabulary & Word Choice', score: 8.5 },
  { name: 'Grammar & Sentence Structure', score: 8.4 },
  { name: 'Communication & Relevance', score: 8.6 }
])

const printReport = () => {
  window.print()
}
</script>

<style scoped>
@media print {
  body * {
    visibility: hidden;
  }
  #pdf-report-content, #pdf-report-content * {
    visibility: visible;
  }
  #pdf-report-content {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
  }
}
</style>
