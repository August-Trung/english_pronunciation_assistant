<template>
  <v-expansion-panels :model-value="initiallyExpanded ? 0 : undefined" variant="accordion" class="my-2">
    <v-expansion-panel :title="evaluation.worksheet_result ? 'View Worksheet Auto-Grading Details' : 'View AI Assessment Details'">
      <v-expansion-panel-text>
        <!-- Case 1: Dynamic Worksheet Auto-Grading Report -->
        <template v-if="evaluation.worksheet_result">
          <div class="mb-3 pa-3 bg-teal-lighten-5 rounded border border-teal">
            <div class="d-flex align-center justify-space-between flex-wrap ga-2">
              <div>
                <h3 class="text-subtitle-2 font-weight-black text-teal-darken-3">Worksheet Auto-Grading Report</h3>
                <div class="text-caption text-grey-darken-3">
                  Score: <strong>{{ evaluation.score }}/10</strong> (Earned: {{ evaluation.worksheet_result.earned_points }}/{{ evaluation.worksheet_result.total_points }} points)
                </div>
              </div>
              <v-chip size="small" color="teal" variant="flat" class="font-weight-bold">
                Auto-Graded
              </v-chip>
            </div>
          </div>

          <div class="d-flex flex-column ga-2 mb-3">
            <div
              v-for="(item, idx) in evaluation.worksheet_result.details || []"
              :key="item.exercise_id || idx"
              class="pa-3 rounded border"
              :class="item.is_correct ? 'bg-green-lighten-5 border-green' : 'bg-red-lighten-5 border-red'"
            >
              <div class="d-flex align-center justify-space-between mb-1">
                <span class="text-caption font-weight-black text-secondary">
                  #{{ idx + 1 }}. {{ item.instruction }}
                </span>
                <v-chip size="x-small" :color="item.is_correct ? 'success' : 'error'" variant="flat" class="font-weight-bold">
                  {{ item.is_correct ? '✓ Correct (+ ' + item.earned + ')' : '✗ Incorrect (0)' }}
                </v-chip>
              </div>

              <div v-if="item.audio_text" class="d-flex align-center ga-2 mb-1">
                <v-btn size="x-small" color="indigo" variant="flat" prepend-icon="mdi-volume-high" @click="speakBritish(item.audio_text)">
                  Listen Audio (UK)
                </v-btn>
                <span class="text-caption text-grey-darken-3 font-italic">"{{ item.audio_text }}"</span>
              </div>

              <div v-if="item.question_text" class="text-caption font-weight-bold text-grey-darken-4 mb-1">
                {{ item.question_text }}
              </div>

              <div class="text-caption mt-1">
                <div>Learner Answer: <strong :class="item.is_correct ? 'text-success' : 'text-error'">{{ typeof item.student_answer === 'object' ? JSON.stringify(item.student_answer) : (item.student_answer || 'No answer') }}</strong></div>
                <div v-if="!item.is_correct" class="text-grey-darken-2">Correct Key: <strong class="text-success">{{ typeof item.correct_answer === 'object' ? JSON.stringify(item.correct_answer) : item.correct_answer }}</strong></div>
              </div>
            </div>
          </div>
        </template>

        <!-- Case 2: Standard Audio Assessment Details -->
        <template v-else>
          <div v-if="transcript" class="mb-3">
            <h3 class="text-subtitle-2">Transcribed Spoken Text</h3>
            <p class="pa-3 bg-blue-lighten-5 rounded">{{ transcript }}</p>
          </div>
          <v-alert v-if="!evaluation.version" type="info" variant="tonal" class="mb-3">
            This earlier submission does not include a complete saved assessment. Only available details are shown.
          </v-alert>
          <p v-if="evaluation.score != null" class="font-weight-bold mb-2">AI Score: {{ evaluation.score }}/10</p>
          <p v-if="evaluation.duration_seconds" class="mb-2">Recording Duration: {{ evaluation.duration_seconds }} seconds</p>
          <template v-if="evaluation.reading_result">
            <h3 class="text-subtitle-2">Model Sentence Word Alignment</h3>
            <p class="mb-2">Word Match: {{ evaluation.reading_result.accuracy }}%. This score measures transcript alignment with the model sentence.</p>
            <div class="d-flex flex-wrap ga-2 mb-3">
              <v-chip v-for="(word, i) in evaluation.reading_result.word_analysis" :key="i"
                :color="word.status === 'correct' ? 'success' : word.status === 'partial' ? 'warning' : 'error'" size="small">
                {{ word.word }}: {{ word.status }}
              </v-chip>
            </div>
          </template>
          <template v-if="evaluation.picture_eval">
            <h3 class="text-subtitle-2">Picture Description Assessment</h3>
            <div v-for="key in ['fluency_score', 'vocabulary_score', 'grammar_score']" :key="key">
              <p v-if="evaluation.picture_eval[key] != null">{{ key.replace('_score', '').toUpperCase() }}: {{ evaluation.picture_eval[key] }}/100</p>
            </div>
            <p class="my-2">Matched Keywords: {{ evaluation.picture_eval.matched_keywords?.join(', ') || 'None' }}</p>
            <p v-if="evaluation.picture_eval.sample_response" class="pa-3 bg-purple-lighten-5 rounded mb-3">{{ evaluation.picture_eval.sample_response }}</p>
          </template>
          <template v-if="evaluation.breakdown">
            <h3 class="text-subtitle-2">Speech Indicators</h3>
            <p class="text-caption mb-2">Supporting indicators. The overall score uses {{ evaluation.reading_result ? 'model sentence alignment' : 'the picture description rubric' }}.</p>
            <div v-for="key in ['Pronunciation', 'Fluency', 'Grammar', 'Vocabulary', 'Communication']" :key="key">
              <p v-if="evaluation.breakdown[key] != null">{{ key }}: {{ evaluation.ai_analysis?.scores?.[key.toLowerCase()] ?? evaluation.breakdown[key] }}/2</p>
            </div>
          </template>
          <div v-if="evaluation.ipa_analysis?.words_ipa?.length" class="my-3">
            <h3 class="text-subtitle-2">Word and IPA Details</h3>
            <div v-for="(word, i) in evaluation.ipa_analysis.words_ipa" :key="i" class="py-1 border-b">
              <strong>{{ word.word }}</strong> {{ word.target_ipa }} — {{ word.status }}
              <p v-if="word.note" class="text-caption">{{ word.note }}</p>
            </div>
          </div>
          <p v-if="evaluation.feedback || evaluation.picture_eval?.feedback" class="mt-3" style="white-space: pre-line">{{ evaluation.feedback || evaluation.picture_eval.feedback }}</p>
          <div v-if="evaluation.ai_analysis?.pedagogical_feedback" class="mt-3">
            <h3 class="text-subtitle-2">Learning Feedback</h3>
            <p v-for="(comment, key) in evaluation.ai_analysis.pedagogical_feedback" :key="key" class="mb-2">{{ comment }}</p>
          </div>
          <div v-if="evaluation.ai_analysis?.grammar_fixes?.length" class="mt-3">
            <h3 class="text-subtitle-2">Grammar Suggestions</h3>
            <div v-for="(fix, i) in evaluation.ai_analysis.grammar_fixes" :key="i" class="mb-2">
              <p>Original: {{ fix.original }}</p>
              <p>Suggested: {{ fix.fixed }}</p>
              <p>{{ fix.reason }}</p>
            </div>
          </div>
          <div v-if="evaluation.ai_analysis?.native_suggestions?.length" class="mt-3">
            <h3 class="text-subtitle-2">Natural Expression Suggestions</h3>
            <p v-for="(suggestion, i) in evaluation.ai_analysis.native_suggestions" :key="i" class="mb-2">{{ suggestion.text }}<br>{{ suggestion.meaning }}</p>
          </div>
        </template>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script setup>
import { speakBritishText } from '@/utils/tts.js'

defineProps({
  initiallyExpanded: { type: Boolean, default: false },
  evaluation: { type: Object, default: () => ({}) },
  transcript: { type: String, default: '' }
})

const speakBritish = (text) => {
  if (text) {
    speakBritishText(text, 0.9)
  }
}
</script>
