<template>
  <v-container fluid class="pa-4 pa-md-6" style="max-width: 1400px;">
    <!-- Vuetify Toast Notification -->
    <v-snackbar
      v-model="toast.show"
      :color="toast.color"
      location="top"
      timeout="4000"
      rounded="lg"
      elevation="4"
    >
      <div class="d-flex align-center ga-2 text-subtitle-2 font-weight-bold text-white">
        <v-icon>{{ toast.icon }}</v-icon>
        <span>{{ toast.text }}</span>
      </div>
    </v-snackbar>

    <!-- Homework Banner -->
    <v-card border flat class="pa-4 mb-4 bg-gradient-purple text-white rounded-lg elevation-1">
      <div class="d-flex align-center justify-space-between flex-wrap ga-3">
        <div class="d-flex align-center ga-3">
          <v-avatar color="white" size="48" class="elevation-1">
            <v-icon color="purple-darken-3" size="large">mdi-clipboard-text-outline</v-icon>
          </v-avatar>
          <div>
            <div class="text-h6 font-weight-black tracking-tight">CLASSROOM ASSIGNED HOMEWORK</div>
            <div class="text-caption opacity-90 font-weight-medium">
              Complete pronunciation reading exercises assigned by your teacher
            </div>
          </div>
        </div>

        <div class="d-flex flex-wrap ga-2 align-center">
          <v-btn
            icon="mdi-lightbulb-on-outline"
            variant="tonal"
            color="white"
            size="small"
            title="Hướng dẫn làm bài tập về nhà"
            @click="replayStudentHwTour"
          />
          <v-btn color="white" variant="outlined" prepend-icon="mdi-refresh" :loading="isRefreshing" class="text-none" @click="refreshHomework">Refresh All Assignments</v-btn>
        <v-btn
          color="white"
          variant="flat"
          class="font-weight-black text-purple-darken-3 text-none"
          prepend-icon="mdi-key-variant"
          @click="showJoinClassModal = true"
        >
          Enter Class Join Code
        </v-btn>
        </div>
      </div>
    </v-card>

    <!-- Inline Deadline Alerts -->
    <v-alert
      v-if="dueSoonAssignments.length > 0"
      type="warning"
      variant="tonal"
      density="comfortable"
      rounded="lg"
      class="mb-4 border-warning font-weight-medium"
      closable
      icon="mdi-clock-alert-outline"
    >
      <div>
        <div class="text-subtitle-2 font-weight-black">
          {{ dueSoonAssignments.length }} assignment{{ dueSoonAssignments.length > 1 ? 's' : '' }} due within 24 hours!
        </div>
        <div class="text-caption text-grey-darken-3">
          Please record and submit your exercises before the deadline to ensure your scores are recorded on time.
        </div>
      </div>
    </v-alert>

    <v-alert
      v-if="overdueAssignments.length > 0"
      type="error"
      variant="tonal"
      density="comfortable"
      rounded="lg"
      class="mb-4 border-error font-weight-medium"
      closable
      icon="mdi-alert-circle-outline"
    >
      <div>
        <div class="text-subtitle-2 font-weight-black">
          {{ overdueAssignments.length }} past-due assignment{{ overdueAssignments.length > 1 ? 's' : '' }}
        </div>
        <div class="text-caption text-grey-darken-3">
          These assignments have passed their deadline. Check with your educator if late submissions are accepted.
        </div>
      </div>
    </v-alert>

    <!-- 2-Column Responsive Workspace -->
    <v-row class="ma-0 ga-3">
      <!-- Left Column: Filter & Assignments Feed (Cols 12, md 8) -->
      <v-col cols="12" md="8" class="pa-0">

    <!-- Filter Tabs by Classroom if Student is in Multiple Classes -->
    <div v-if="enrolledClasses.length > 1" class="d-flex align-center ga-2 overflow-x-auto pb-2 mb-3">
      <v-chip
        :color="selectedClassFilter === 'all' ? 'primary' : 'grey-lighten-4'"
        :variant="selectedClassFilter === 'all' ? 'flat' : 'tonal'"
        size="small"
        class="font-weight-bold flex-shrink-0 cursor-pointer"
        @click="selectedClassFilter = 'all'"
      >
        All Classrooms ({{ assignments.length }})
      </v-chip>
      <v-chip
        v-for="cls in enrolledClasses"
        :key="cls.class_id"
        :color="selectedClassFilter === cls.class_id ? 'primary' : 'grey-lighten-4'"
        :variant="selectedClassFilter === cls.class_id ? 'flat' : 'tonal'"
        size="small"
        class="font-weight-bold flex-shrink-0 cursor-pointer"
        @click="selectedClassFilter = cls.class_id"
      >
        {{ cls.class_name }} ({{ getAssignmentsCountForClass(cls.class_id) }})
      </v-chip>
    </div>

    <!-- Assignments List -->
    <div id="tour-student-hw-list" class="d-flex flex-column ga-3">
      <v-card
        v-for="asg in filteredAssignments"
        :key="asg.assignment_id"
        border
        flat
        class="pa-4 bg-white rounded-lg"
      >
        <div class="d-flex align-center justify-space-between flex-wrap ga-2 mb-2">
          <div>
            <div class="d-flex align-center ga-2 flex-wrap">
              <span class="text-subtitle-1 font-weight-black text-primary">{{ asg.title }}</span>
              <v-chip color="indigo" size="x-small" variant="flat" class="font-weight-bold">
                {{ asg.class_name }}
              </v-chip>
              <v-chip
                size="x-small"
                :color="asg.assignment_type === 'picture' ? 'purple-darken-2' : 'teal-darken-2'"
                variant="tonal"
                class="font-weight-bold"
                :prepend-icon="asg.assignment_type === 'picture' ? 'mdi-image-filter-frames' : 'mdi-waveform'"
              >
                {{ asg.assignment_type === 'picture' ? 'Describe Picture' : 'Sentence Reading' }}
              </v-chip>
            </div>
            <div class="text-caption text-grey">Due Date: {{ asg.due_date || 'No Deadline' }}</div>
          </div>

          <v-chip
            @click="asg.is_submitted && (selectedAssessment = asg)"
            :color="getDeadlineStatus(asg).color"
            :variant="getDeadlineStatus(asg).status === 'due_soon' ? 'flat' : 'tonal'"
            size="small"
            class="font-weight-black"
            :prepend-icon="getDeadlineStatus(asg).icon"
          >
            {{ getDeadlineStatus(asg).label }}
          </v-chip>
        </div>

        <!-- Format Branch 1: Picture Speaking Challenge -->
        <div v-if="asg.assignment_type === 'picture'" class="mb-3">
          <div class="d-flex ga-3 flex-column flex-md-row mb-2">
            <!-- Scene Image -->
            <div v-if="asg.image_url" class="rounded overflow-hidden border flex-shrink-0 cursor-pointer" style="width: 320px; max-width: 100%;" @click="previewImage(asg.image_url)">
              <v-img
                :src="getImageUrl(asg.image_url)"
                height="240"
                contain
                class="bg-grey-lighten-4"
              />
            </div>

            <!-- Guiding Questions & Target Keywords -->
            <div class="flex-grow-1 d-flex flex-column justify-space-between ga-2">
              <div v-if="asg.guiding_questions && asg.guiding_questions.length" class="bg-blue-lighten-5 pa-3 rounded border border-blue">
                <div class="text-caption font-weight-black text-blue-darken-3 mb-1 d-flex align-center ga-1">
                  <v-icon size="x-small">mdi-help-circle-outline</v-icon>
                  <span>GUIDING QUESTIONS (STRUCTURE YOUR TALK):</span>
                </div>
                <ul class="text-caption text-grey-darken-3 pl-4 mb-0">
                  <li v-for="(q, idx) in asg.guiding_questions" :key="idx" class="mb-1">
                    {{ q }}
                  </li>
                </ul>
              </div>

              <div v-if="asg.target_keywords && asg.target_keywords.length">
                <div class="text-caption font-weight-black text-grey-darken-3 mb-1 d-flex align-center ga-1">
                  <v-icon size="x-small">mdi-format-list-checks</v-icon>
                  <span>TARGET KEYWORDS (TRY TO INCLUDE):</span>
                </div>
                <div class="d-flex flex-wrap ga-1">
                  <v-chip
                    v-for="kw in asg.target_keywords"
                    :key="kw"
                    size="x-small"
                    color="grey-darken-2"
                    variant="outlined"
                    class="font-weight-bold"
                  >
                    {{ kw }}
                  </v-chip>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Format Branch 2: Standard Sentence Reading -->
        <div v-else-if="asg.assignment_type === 'sentence'" class="pa-3 bg-purple-lighten-5 rounded border border-purple mb-3">
          <div class="text-caption font-weight-bold text-purple-darken-3 mb-1">Assigned Model Reading Sentence:</div>
          <div class="text-body-1 font-weight-black text-secondary" style="white-space: pre-wrap;">"{{ asg.topic_sentence }}"</div>
        </div>

        <!-- Format Branch 3: Dynamic Vocab Worksheet -->
        <div v-else-if="asg.assignment_type === 'worksheet'" class="mb-3">
          <div class="d-flex align-center justify-space-between mb-2 pb-2 border-b">
            <div class="d-flex align-center ga-1">
              <v-chip size="x-small" color="teal-darken-2" variant="tonal" class="font-weight-black" prepend-icon="mdi-format-list-checks">
                DYNAMIC WORKSHEET
              </v-chip>
              <span class="text-caption font-weight-bold text-grey-darken-2">
                {{ parseExercises(asg.content_json).length }} Interactive Questions
              </span>
            </div>
            <v-chip size="x-small" color="indigo" variant="flat" class="font-weight-bold" prepend-icon="mdi-account-voice">
              British Accent (en-GB)
            </v-chip>
          </div>

          <!-- Submitted View for Worksheet: Question-by-question breakdown -->
          <div v-if="asg.is_submitted && parseGradingResult(asg.answers_json)" class="mt-2">
            <div class="d-flex align-center justify-space-between bg-teal-lighten-5 pa-3 rounded border border-teal mb-3">
              <div class="d-flex align-center ga-2">
                <v-icon color="teal-darken-2" size="28">mdi-check-decagram</v-icon>
                <div>
                  <div class="text-subtitle-2 font-weight-black text-teal-darken-3">Worksheet Completed & Graded</div>
                  <div class="text-caption text-grey-darken-3">
                    Score: <strong>{{ asg.score }}/10</strong> ({{ parseGradingResult(asg.answers_json).earned_points }}/{{ parseGradingResult(asg.answers_json).total_points }} points)
                  </div>
                </div>
              </div>
            </div>

            <div class="d-flex flex-column ga-2">
              <div
                v-for="(detail, qIdx) in parseGradingResult(asg.answers_json).details || []"
                :key="detail.exercise_id || qIdx"
                class="pa-3 rounded border"
                :class="detail.is_correct ? 'bg-green-lighten-5 border-green' : 'bg-red-lighten-5 border-red'"
              >
                <div class="d-flex align-center justify-space-between mb-1">
                  <span class="text-caption font-weight-black text-secondary">
                    Question #{{ qIdx + 1 }}: {{ detail.instruction }}
                  </span>
                  <v-chip size="x-small" :color="detail.is_correct ? 'success' : 'error'" variant="flat" class="font-weight-bold">
                    {{ detail.is_correct ? '✓ Correct (+ ' + detail.earned + ')' : '✗ Incorrect' }}
                  </v-chip>
                </div>
                <div v-if="detail.audio_text" class="d-flex align-center ga-2 mb-1">
                  <v-btn size="x-small" color="indigo" variant="flat" prepend-icon="mdi-volume-high" @click="playWorksheetAudio(detail.audio_text)">
                    Listen Audio (en-GB)
                  </v-btn>
                  <span class="text-caption text-grey-darken-3 font-italic">"{{ detail.audio_text }}"</span>
                </div>
                <div v-if="detail.question_text" class="text-caption font-weight-bold text-grey-darken-4 mb-1">
                  {{ detail.question_text }}
                </div>
                <div class="text-caption mt-1 d-flex flex-column ga-0.5">
                  <div>Your Answer: <strong :class="detail.is_correct ? 'text-success' : 'text-error'">{{ typeof detail.student_answer === 'object' ? JSON.stringify(detail.student_answer) : (detail.student_answer || 'No answer') }}</strong></div>
                  <div v-if="!detail.is_correct" class="text-grey-darken-2">Correct Key: <strong class="text-success">{{ typeof detail.correct_answer === 'object' ? JSON.stringify(detail.correct_answer) : detail.correct_answer }}</strong></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Unsubmitted View: Interactive Question Player -->
          <div v-else id="tour-student-hw-interactive-area" class="d-flex flex-column ga-3 mt-2">
            <div
              v-for="(ex, exIdx) in parseExercises(asg.content_json)"
              :key="ex.id || exIdx"
              class="pa-3 rounded border bg-white"
            >
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="d-flex align-center ga-1">
                  <v-chip size="x-small" color="secondary" variant="flat" class="font-weight-black">
                    #{{ exIdx + 1 }}
                  </v-chip>
                  <span class="text-caption font-weight-black text-grey-darken-3">
                    {{ ex.instruction }}
                  </span>
                </div>
                <v-chip size="x-small" color="grey" variant="tonal">
                  {{ ex.points || 1 }} pt
                </v-chip>
              </div>

              <!-- Audio Player Button for Listening Questions -->
              <div v-if="ex.audio_text || (ex.type && ex.type.startsWith('listen_'))" class="mb-2 pa-2 rounded bg-indigo-lighten-5 border border-indigo d-flex align-center justify-space-between flex-wrap ga-2">
                <div class="d-flex align-center ga-2">
                  <v-btn
                    id="tour-student-hw-audio-btn"
                    color="indigo-darken-2"
                    variant="flat"
                    size="small"
                    prepend-icon="mdi-volume-high"
                    class="text-none font-weight-bold"
                    @click="playWorksheetAudio(ex.audio_text || ex.question_text)"
                  >
                    Play Audio Clip (UK)
                  </v-btn>
                  <span class="text-caption text-indigo-darken-3 font-weight-medium">
                    Tap to hear native British pronunciation
                  </span>
                </div>
              </div>

              <!-- Question context / prompt text -->
              <div v-if="ex.question_text" class="text-subtitle-2 font-weight-bold text-grey-darken-4 mb-2">
                {{ ex.question_text }}
              </div>

              <!-- Interactive Format 1: Tick or Cross -->
              <div v-if="ex.type === 'listen_and_tick_or_cross'" class="d-flex ga-2 mt-1">
                <v-btn
                  size="small"
                  :color="getWorksheetAnswer(asg.assignment_id, ex.id) === 'tick' ? 'success' : 'grey-lighten-3'"
                  :variant="getWorksheetAnswer(asg.assignment_id, ex.id) === 'tick' ? 'flat' : 'outlined'"
                  class="text-none font-weight-bold flex-grow-1"
                  prepend-icon="mdi-check"
                  @click="setWorksheetAnswer(asg.assignment_id, ex.id, 'tick')"
                >
                  Tick (✓ True)
                </v-btn>
                <v-btn
                  size="small"
                  :color="getWorksheetAnswer(asg.assignment_id, ex.id) === 'cross' ? 'error' : 'grey-lighten-3'"
                  :variant="getWorksheetAnswer(asg.assignment_id, ex.id) === 'cross' ? 'flat' : 'outlined'"
                  class="text-none font-weight-bold flex-grow-1"
                  prepend-icon="mdi-close"
                  @click="setWorksheetAnswer(asg.assignment_id, ex.id, 'cross')"
                >
                  Cross (✗ False)
                </v-btn>
              </div>

              <!-- Interactive Format 2: Unscramble Words -->
              <div v-else-if="ex.type === 'unscramble_words'" class="mt-1">
                <div class="pa-2 bg-grey-lighten-4 rounded border mb-2 d-flex align-center justify-space-between">
                  <div>
                    <span class="text-caption font-weight-bold text-grey-darken-2 mr-2">Your Sentence:</span>
                    <span class="text-subtitle-2 font-weight-black text-primary">
                      {{ (getWorksheetAnswer(asg.assignment_id, ex.id) || []).join(' ') || '(Tap words below in order)' }}
                    </span>
                  </div>
                  <v-btn size="x-small" color="grey" variant="text" @click="resetUnscramble(asg.assignment_id, ex.id)">
                    Reset
                  </v-btn>
                </div>
                <div class="d-flex flex-wrap ga-1">
                  <v-chip
                    v-for="(tok, tIdx) in (ex.options || [])"
                    :key="tIdx"
                    size="small"
                    color="primary"
                    variant="outlined"
                    class="font-weight-bold"
                    @click="toggleUnscrambleToken(asg.assignment_id, ex.id, tok)"
                  >
                    {{ tok }}
                  </v-chip>
                </div>
              </div>

              <!-- Interactive Format 3: Fill in Blank / Spelling / Missing Word -->
              <div v-else-if="ex.type === 'read_and_fill_in_the_blank' || ex.type === 'write_the_missing_word'" class="mt-1">
                <div v-if="ex.options && ex.options.length" class="mb-2">
                  <span class="text-caption font-weight-bold text-grey-darken-2 mr-1">Word Bank:</span>
                  <v-chip
                    v-for="opt in ex.options"
                    :key="opt"
                    size="x-small"
                    color="indigo"
                    variant="tonal"
                    class="mr-1 font-weight-bold cursor-pointer"
                    @click="setWorksheetAnswer(asg.assignment_id, ex.id, opt)"
                  >
                    {{ opt }}
                  </v-chip>
                </div>
                <v-text-field
                  :model-value="getWorksheetAnswer(asg.assignment_id, ex.id)"
                  label="Type your answer here:"
                  placeholder="Type missing word..."
                  density="compact"
                  variant="outlined"
                  hide-details
                  @update:model-value="val => setWorksheetAnswer(asg.assignment_id, ex.id, val)"
                />
              </div>

              <!-- Interactive Format 4: Options Picker (Circle, Tick, Multiple Choice) -->
              <div v-else-if="ex.options && ex.options.length" class="d-flex flex-wrap ga-2 mt-1">
                <v-btn
                  v-for="(opt, oIdx) in ex.options"
                  :key="oIdx"
                  size="small"
                  :color="getWorksheetAnswer(asg.assignment_id, ex.id) === opt ? 'primary' : 'grey-lighten-4'"
                  :variant="getWorksheetAnswer(asg.assignment_id, ex.id) === opt ? 'flat' : 'outlined'"
                  class="text-none font-weight-bold flex-grow-1"
                  @click="setWorksheetAnswer(asg.assignment_id, ex.id, opt)"
                >
                  {{ opt }}
                </v-btn>
              </div>

              <!-- Interactive Format 5: Generic Text input -->
              <div v-else class="mt-1">
                <v-text-field
                  :model-value="getWorksheetAnswer(asg.assignment_id, ex.id)"
                  label="Your Answer:"
                  density="compact"
                  variant="outlined"
                  hide-details
                  @update:model-value="val => setWorksheetAnswer(asg.assignment_id, ex.id, val)"
                />
              </div>
            </div>

            <!-- Submit Worksheet Button -->
            <v-btn
              id="tour-student-hw-submit-btn"
              color="success"
              variant="flat"
              size="large"
              block
              class="text-none font-weight-black mt-2"
              prepend-icon="mdi-send-check"
              :loading="isSubmittingWorksheet"
              @click="submitWorksheet(asg)"
            >
              Submit Worksheet & Grade
            </v-btn>
          </div>
        </div>


        <template v-if="asg.assignment_type !== 'worksheet'">
          <div v-if="drafts[asg.assignment_id]" class="mb-3 pa-3 border rounded">
            <div class="text-subtitle-2 mb-2">Review Your Recording</div>
            <audio controls :src="drafts[asg.assignment_id].url" class="w-100" />
            <v-btn class="mt-2 text-none" color="success" :loading="submittingId === asg.assignment_id" :disabled="isSubmitting || isStartingRecording || currentRecordingAsgId !== null" @click="uploadSubmission(asg)">Submit Recording</v-btn>
          </div>
          <!-- Submission Controls or Result -->
          <div v-if="!asg.is_submitted" class="d-flex align-center flex-wrap ga-2">
          <v-btn
            :color="currentRecordingAsgId === asg.assignment_id ? 'error' : 'primary'"
            variant="flat"
            class="font-weight-black text-none"
            :prepend-icon="currentRecordingAsgId === asg.assignment_id ? 'mdi-stop' : 'mdi-microphone'"
            :disabled="isStartingRecording || isSubmitting || (currentRecordingAsgId !== null && currentRecordingAsgId !== asg.assignment_id)"
            @click="requestRecording(asg)"
          >
            {{ currentRecordingAsgId === asg.assignment_id ? 'Stop Recording' : (drafts[asg.assignment_id] ? 'Record Again' : 'Start Voice Recording') }}
          </v-btn>
          <span v-if="currentRecordingAsgId === asg.assignment_id" class="text-caption text-error font-weight-bold">
            Recording: {{ elapsedSeconds }} seconds. Select Stop Recording when finished.
          </span>
        </div>

        <div v-else class="bg-grey-lighten-5 pa-3 rounded border">
          <div class="d-flex align-center justify-space-between mb-1">
            <span class="text-caption font-weight-bold text-grey-darken-3">Submitted Audio:</span>
            <v-chip @click="selectedAssessment = asg" aria-label="View AI assessment details" size="x-small" color="success" variant="flat" class="font-weight-bold">Score: {{ asg.score?.toFixed(1) }}/10</v-chip>
          </div>
          <div v-if="asg.audio_url" class="d-flex align-center ga-2 mb-2">
            <audio controls :src="getImageUrl(asg.audio_url)" class="w-100" style="height: 32px;" />
          </div>
          <p v-else class="text-caption text-grey">The audio file was not retained for this earlier submission.</p>
          <SubmissionEvaluation :evaluation="asg.evaluation || {}" :transcript="asg.transcribed_text || ''" />
          <p v-if="asg.score_override != null" class="text-caption">Educator-adjusted score: {{ asg.score_override }}/10. Original AI score: {{ asg.ai_score }}/10.</p>
          <div v-if="asg.teacher_feedback" class="text-caption text-grey-darken-3 bg-white pa-2 rounded border" style="white-space: pre-line;">
            <div class="font-weight-bold text-indigo mb-1">Assessment & Feedback:</div>
            {{ asg.teacher_feedback }}
          </div>
        </div>
        </template>
      </v-card>

      <div v-if="!filteredAssignments.length" class="text-center pa-8 bg-white border rounded-lg">
        <v-icon size="48" color="grey-lighten-1">mdi-clipboard-check-outline</v-icon>
        <template v-if="enrolledClasses.length">
          <div class="text-subtitle-1 font-weight-black text-indigo-darken-2 mt-2">
            You're all caught up!
          </div>
          <div class="text-subtitle-2 font-weight-medium text-grey-darken-1 mt-1">
            Your teacher has not assigned any homework for your classroom yet. Check back soon!
          </div>
        </template>
        <template v-else>
          <div class="text-subtitle-2 font-weight-bold text-grey-darken-1 mt-2">
            You are not enrolled in any classroom yet.
          </div>
          <div class="text-caption text-grey mt-1">
            Enter a classroom join code provided by your teacher to access class homework.
          </div>
          <v-btn
            color="primary"
            variant="tonal"
            class="mt-3 text-none font-weight-bold"
            prepend-icon="mdi-key-variant"
            @click="showJoinClassModal = true"
          >
            Enter Join Code (Example: CLS-836-58)
          </v-btn>
        </template>
      </div>
    </div>
  </v-col>

  <!-- Right Column: Classrooms & Performance Sidebar (Cols 12, md 4) -->
  <v-col cols="12" md="4" class="pa-0">
    <div class="sticky-side d-flex flex-column ga-3">
      <!-- Summary Metrics Card -->
      <v-card border flat class="pa-4 bg-white rounded-lg">
        <div class="text-caption font-weight-black text-secondary mb-2 d-flex align-center ga-1">
          <v-icon size="small" color="secondary">mdi-chart-pie</v-icon>
          <span>HOMEWORK PROGRESS</span>
        </div>
        <div class="d-flex align-center justify-space-between mb-2">
          <span class="text-caption font-weight-bold text-grey-darken-2">Submitted Rate:</span>
          <span class="text-subtitle-2 font-weight-black text-primary">
            {{ assignments.filter(a => a.is_submitted).length }} / {{ assignments.length }}
          </span>
        </div>
        <v-progress-linear
          :model-value="assignments.length ? (assignments.filter(a => a.is_submitted).length / assignments.length) * 100 : 0"
          color="primary"
          height="8"
          rounded
          class="mb-3"
        />
      </v-card>

      <!-- Enrolled Classes Card -->
      <v-card v-if="enrolledClasses.length" border flat class="pa-4 bg-white rounded-lg">
        <div class="text-caption font-weight-black text-secondary mb-3 d-flex align-center justify-space-between">
          <span>MY CLASSROOMS ({{ enrolledClasses.length }})</span>
          <v-btn size="x-small" variant="text" color="primary" @click="showJoinClassModal = true">
            + Join Another
          </v-btn>
        </div>
        <div class="d-flex flex-column ga-2">
          <div
            v-for="cls in enrolledClasses"
            :key="cls.class_id"
            class="pa-2.5 rounded-lg border bg-grey-lighten-5 d-flex align-center justify-space-between"
          >
            <div>
              <div class="font-weight-black text-caption text-indigo-darken-3 d-flex align-center ga-1">
                <v-icon size="x-small" color="indigo">mdi-google-classroom</v-icon>
                <span>{{ cls.class_name }}</span>
              </div>
              <div class="text-caption text-grey" style="font-size: 10px;">
                Code: <strong>{{ cls.join_code || 'Enrolled' }}</strong>
                <span v-if="cls.teacher_name"> &bull; Teacher: {{ cls.teacher_name }}</span>
              </div>
            </div>

            <v-btn
              icon="mdi-exit-to-app"
              variant="text"
              size="small"
              color="error"
              title="Leave Class"
              @click.stop="openLeaveClassModal(cls)"
            />
          </div>
        </div>
      </v-card>
    </div>
  </v-col>
</v-row>

    <!-- Modal 1: Join Class Dialog -->
    <v-dialog v-model="showJoinClassModal" max-width="450">
      <v-card border rounded="lg" class="pa-4">
        <div class="text-subtitle-1 font-weight-black text-primary mb-2 d-flex align-center ga-2">
          <v-icon color="primary">mdi-key-variant</v-icon>
          <span>Join New Classroom</span>
        </div>

        <v-text-field
          v-model="joinCodeInput"
          label="6-Digit Join Code:"
          placeholder="Example: CLS-524-89"
          variant="outlined"
          density="comfortable"
          class="mb-3"
          prepend-inner-icon="mdi-google-classroom"
        />

        <v-card-actions class="px-0 pb-0">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showJoinClassModal = false">Cancel</v-btn>
          <v-btn color="primary" variant="flat" class="text-none font-weight-bold" :loading="isJoining" @click="submitJoinClass">
            Join Class
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Modal 2: Git-Style Safety Confirmation for Leaving Classroom -->
    <v-dialog v-model="showLeaveModal" max-width="480">
      <v-card v-if="targetLeaveClass" border rounded="lg" class="pa-5 bg-white">
        <div class="text-subtitle-1 font-weight-black text-error mb-2 d-flex align-center ga-2 border-b pb-2">
          <v-icon color="error">mdi-shield-alert-outline</v-icon>
          <span>SAFE UNENROLLMENT CONFIRMATION</span>
        </div>

        <div class="text-body-2 font-weight-bold text-grey-darken-3 mb-2">
          You are about to leave <strong>{{ targetLeaveClass.class_name }}</strong>.
        </div>

        <div class="bg-red-lighten-5 pa-3 rounded border border-red text-caption text-red-darken-4 font-weight-bold mb-3">
          To prevent accidental unenrollment, please type the exact Join Code of this class below:
          <div class="text-subtitle-2 font-weight-mono font-weight-black mt-1 text-center bg-white py-1 rounded border">
            {{ targetLeaveClass.join_code }}
          </div>
        </div>

        <v-text-field
          v-model="leaveInput"
          label="Type Join Code to confirm:"
          :placeholder="targetLeaveClass.join_code"
          variant="outlined"
          density="comfortable"
          class="mb-2"
          prepend-inner-icon="mdi-shield-check"
          hide-details
        />

        <v-card-actions class="px-0 pt-4 pb-0">
          <v-spacer />
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showLeaveModal = false">
            Cancel
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            class="text-none font-weight-bold"
            :disabled="leaveInput.trim().toUpperCase() !== targetLeaveClass.join_code.toUpperCase()"
            :loading="isLeaving"
            @click="confirmLeaveClass"
          >
            Confirm Leave Classroom
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog :model-value="Boolean(replaceRecordingTarget)" max-width="480" @update:model-value="replaceRecordingTarget = null">
      <v-card class="pa-4">
        <v-card-title>Replace Your Recording?</v-card-title>
        <v-card-text>Recording again will replace the current draft after you stop. The current draft remains available if recording cannot start.</v-card-text>
        <v-card-actions>
          <v-btn @click="replaceRecordingTarget = null">Cancel</v-btn>
          <v-btn color="primary" @click="confirmRecordAgain">Record Again</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- Dialog: Homework Picture Zoom -->
    <v-dialog v-model="showImageModal" max-width="850">
      <v-card class="pa-2 bg-black text-right" rounded="lg">
        <v-btn icon="mdi-close" variant="text" color="white" size="small" @click="showImageModal = false" />
        <v-img :src="getImageUrl(previewImageUrl)" max-height="650" contain />
      </v-card>
    </v-dialog>
  </v-container>
  <AssessmentDialog :submission="selectedAssessment" :audio-url="selectedAssessment ? getImageUrl(selectedAssessment.audio_url) : ''" @close="selectedAssessment = null" />
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import AssessmentDialog from '@/components/AssessmentDialog.vue'
import SubmissionEvaluation from '@/components/SubmissionEvaluation.vue'
import { isMyHanhSite, isElementaryGrade, mediaUrl } from '@/utils/siteProfile.js'
import { speakBritishText } from '@/utils/tts.js'
import {
  runTour,
  TOUR_KEYS,
  STUDENT_HOMEWORK_TOUR_STEPS
} from '@/utils/tours.js'

const selectedAssessment = ref(null)

const props = defineProps({
  backendUrl: String,
  userId: Number
})

const getImageUrl = (url) => mediaUrl(url, props.backendUrl)

const showImageModal = ref(false)
const previewImageUrl = ref('')
const previewImage = (url) => {
  if (!url) return
  previewImageUrl.value = url
  showImageModal.value = true
}

const toast = ref({ show: false, text: '', color: 'success', icon: 'mdi-check-circle' })
const notify = (text, color = 'success', icon = 'mdi-check-circle') => {
  toast.value = { show: true, text, color, icon }
}


const worksheetAnswers = ref({})
const isSubmittingWorksheet = ref(false)

const parseExercises = (contentJson) => {
  if (!contentJson) return []
  try {
    const parsed = typeof contentJson === 'string' ? JSON.parse(contentJson) : contentJson
    return Array.isArray(parsed) ? parsed : (parsed.exercises || [])
  } catch (e) {
    return []
  }
}

const parseGradingResult = (answersJson) => {
  if (!answersJson) return null
  try {
    return typeof answersJson === 'string' ? JSON.parse(answersJson) : answersJson
  } catch (e) {
    return null
  }
}

const getWorksheetAnswer = (asgId, exId) => {
  const key = `${asgId}_${exId}`
  return worksheetAnswers.value[key]
}

const setWorksheetAnswer = (asgId, exId, val) => {
  const key = `${asgId}_${exId}`
  worksheetAnswers.value[key] = val
}

const toggleUnscrambleToken = (asgId, exId, token) => {
  const key = `${asgId}_${exId}`
  const current = worksheetAnswers.value[key] || []
  const list = Array.isArray(current) ? [...current] : []
  list.push(token)
  worksheetAnswers.value[key] = list
}

const resetUnscramble = (asgId, exId) => {
  const key = `${asgId}_${exId}`
  worksheetAnswers.value[key] = []
}

const playWorksheetAudio = (text) => {
  if (text) {
    speakBritishText(text, 0.9)
  }
}


// Trigger Student Homework Tour once
onMounted(() => {
  setTimeout(() => {
    runTour(TOUR_KEYS.STUDENT_HOMEWORK, STUDENT_HOMEWORK_TOUR_STEPS)
  }, 1200)
})

const replayStudentHwTour = () => {
  runTour(TOUR_KEYS.STUDENT_HOMEWORK, STUDENT_HOMEWORK_TOUR_STEPS, true)
}

const submitWorksheet = async (asg) => {
  const uid = getActiveStudentId()
  if (!uid) {
    showToast('Please sign in as a student to submit homework.', 'warning')
    return
  }
  const exercises = parseExercises(asg.content_json)
  if (!exercises.length) {
    showToast('No exercises found in this worksheet.', 'warning')
    return
  }
  
  const answersMap = {}
  let answeredCount = 0
  for (const ex of exercises) {
    const val = getWorksheetAnswer(asg.assignment_id, ex.id)
    if (val !== undefined && val !== null && val !== '') {
      answersMap[ex.id] = val
      answeredCount++
    }
  }

  if (answeredCount < exercises.length) {
    if (!confirm(`You have completed ${answeredCount} of ${exercises.length} questions. Are you sure you want to submit now?`)) {
      return
    }
  }

  isSubmittingWorksheet.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/assignments/submit-worksheet`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        assignment_id: asg.assignment_id,
        student_id: uid,
        student_name: props.userName || 'Student',
        answers: answersMap
      })
    })

    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Failed to submit worksheet')
    }

    const data = await res.json()
    asg.is_submitted = true
    asg.score = data.score
    asg.answers_json = JSON.stringify(data.grading_result)
    asg.transcribed_text = `Worksheet completed: ${data.grading_result?.earned_points}/${data.grading_result?.total_points} correct`
    showToast(`Worksheet submitted successfully! Your score: ${data.score}/10`, 'success')
  } catch (e) {
    showToast(e.message || 'Error submitting worksheet.', 'error')
  } finally {
    isSubmittingWorksheet.value = false
  }
}

const assignments = ref([])
const classesList = ref([])
const showJoinClassModal = ref(false)
const joinCodeInput = ref('')
const isJoining = ref(false)

const showLeaveModal = ref(false)
const targetLeaveClass = ref(null)
const leaveInput = ref('')
const isLeaving = ref(false)

const currentRecordingAsgId = ref(null)
const isStartingRecording = ref(false)
let disposed = false
const elapsedSeconds = ref(0)
const drafts = ref({})
const submittingId = ref(null)
const isSubmitting = computed(() => submittingId.value !== null)
const isRefreshing = ref(false)
const refreshHomework = async () => {
  isRefreshing.value = true
  try { await Promise.all([fetchEnrolledClasses(), fetchStudentAssignments()]) }
  finally { isRefreshing.value = false }
}
let timerInterval = null
let mediaRecorder = null

const enrolledClasses = computed(() => {
  if (classesList.value?.length) {
    return classesList.value
  }
  const map = {}
  assignments.value?.forEach(a => {
    if (a.class_id && !map[a.class_id]) {
      map[a.class_id] = {
        class_id: a.class_id,
        class_name: a.class_name,
        join_code: a.join_code || `CLS-${a.class_id}`
      }
    }
  })
  return Object.values(map)
})

const selectedClassFilter = ref('all')
const filteredAssignments = computed(() => {
  if (selectedClassFilter.value === 'all') return assignments.value
  return assignments.value.filter(a => a.class_id === selectedClassFilter.value)
})

const getAssignmentsCountForClass = (classId) => {
  return assignments.value.filter(a => a.class_id === classId).length
}

const parseDueDate = (dueStr) => {
  if (!dueStr) return null
  const str = String(dueStr).trim()
  if (/^\d{4}-\d{2}-\d{2}$/.test(str)) {
    return new Date(`${str}T23:59:59`)
  }
  return new Date(str.replace(' ', 'T'))
}

const getDeadlineStatus = (asg) => {
  if (asg.is_submitted) {
    return { status: 'submitted', label: asg.score != null ? `Submitted (${asg.score.toFixed(1)}/10)` : 'Submitted (Assessment unavailable)', color: 'success', icon: 'mdi-check-circle' }
  }
  if (!asg.due_date) {
    return { status: 'pending', label: 'Pending', color: 'warning', icon: undefined }
  }
  const dueDate = parseDueDate(asg.due_date)
  if (!dueDate || isNaN(dueDate.getTime())) {
    return { status: 'pending', label: 'Pending', color: 'warning', icon: undefined }
  }
  const now = Date.now()
  const diffHours = (dueDate.getTime() - now) / (1000 * 60 * 60)
  
  if (diffHours < 0) {
    return { status: 'overdue', label: 'Past Due', color: 'error', icon: 'mdi-alert-circle' }
  }
  if (diffHours <= 24) {
    const totalMinutes = Math.max(1, Math.round((dueDate.getTime() - now) / (1000 * 60)))
    const hrs = Math.floor(totalMinutes / 60)
    const mins = totalMinutes % 60
    const timeText = hrs > 0 ? `${hrs}h left` : `${mins}m left`
    return { status: 'due_soon', label: `Due Soon (${timeText})`, color: 'warning', icon: 'mdi-clock-fast' }
  }
  return { status: 'pending', label: 'Pending', color: 'warning', icon: undefined }
}

const dueSoonAssignments = computed(() => {
  return assignments.value.filter(a => getDeadlineStatus(a).status === 'due_soon')
})

const overdueAssignments = computed(() => {
  return assignments.value.filter(a => getDeadlineStatus(a).status === 'overdue')
})

const getActiveStudentId = () => {
  return props.userId || Number(localStorage.getItem('user_id')) || null
}

const fetchEnrolledClasses = async () => {
  const uid = getActiveStudentId()
  if (!uid) return
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/student/${uid}`)
    if (res.ok) {
      const data = await res.json()
      classesList.value = (data.classes || []).filter(c => !isMyHanhSite() || isElementaryGrade(c.grade_level))
    }
  } catch (e) {
    console.error('Fetch student classes error:', e)
  }
}

const fetchStudentAssignments = async () => {
  const uid = getActiveStudentId()
  if (!uid) return
  try {
    const res = await fetch(`${props.backendUrl}/api/assignments/student/${uid}`)
    if (res.ok) {
      const data = await res.json()
      assignments.value = (data.assignments || []).filter(a => !isMyHanhSite() || isElementaryGrade(a.grade_level))
    }
    else throw new Error('Unable to refresh assignments.')
  } catch (e) {
    notify(e.message, 'error')
    console.error('Fetch student assignments error:', e)
  }
}

const submitJoinClass = async (codeToJoin = null) => {
  const code = (codeToJoin || joinCodeInput.value || '').trim()
  if (!code) return
  const uid = getActiveStudentId()
  if (!uid) {
    notify('Please sign in to join a classroom.', 'warning', 'mdi-account-lock')
    return
  }
  isJoining.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
      body: JSON.stringify({
        student_id: uid,
        join_code: code
      })
    })
    if (res.ok) {
      const data = await res.json()
      notify(`Success! You joined ${data.class_name}`, 'success', 'mdi-google-classroom')
      showJoinClassModal.value = false
      joinCodeInput.value = ''
      localStorage.removeItem('pending_join_code')
      await fetchEnrolledClasses()
      await fetchStudentAssignments()
    } else {
      const err = await res.json()
      notify(err.detail || 'Invalid Class Join Code.', 'error', 'mdi-alert-circle')
    }
  } catch (e) {
    notify('Failed to join class: ' + e.message, 'error', 'mdi-alert-circle')
  } finally {
    isJoining.value = false
  }
}

const openLeaveClassModal = (cls) => {
  targetLeaveClass.value = cls
  leaveInput.value = ''
  showLeaveModal.value = true
}

const confirmLeaveClass = async () => {
  if (!targetLeaveClass.value) return
  const uid = getActiveStudentId()
  if (!uid) return
  isLeaving.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/classes/leave`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: uid,
        class_id: targetLeaveClass.value.class_id
      })
    })
    if (res.ok) {
      notify(`Successfully left ${targetLeaveClass.value.class_name}`, 'success', 'mdi-exit-to-app')
      showLeaveModal.value = false
      targetLeaveClass.value = null
      leaveInput.value = ''
      await fetchEnrolledClasses()
      await fetchStudentAssignments()
    } else {
      const err = await res.json()
      notify(err.detail || 'Failed to leave class.', 'error', 'mdi-alert-circle')
    }
  } catch (e) {
    notify('Error leaving class: ' + e.message, 'error', 'mdi-alert-circle')
  } finally {
    isLeaving.value = false
  }
}

const handleUrlJoinCode = async () => {
  const urlParams = new URLSearchParams(window.location.search)
  let code = urlParams.get('join_code') || localStorage.getItem('pending_join_code')
  
  if (code && code.trim()) {
    code = code.trim()
    const uid = getActiveStudentId()
    if (!uid) {
      localStorage.setItem('pending_join_code', code)
      notify('QR Code detected! Please Sign In or Register to auto-join class.', 'info', 'mdi-qrcode-scan')
    } else {
      await submitJoinClass(code)
      // Clean query parameter from address bar
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }
}

const replaceRecordingTarget = ref(null)
const requestRecording = (asg) => {
  if (drafts.value[asg.assignment_id] && currentRecordingAsgId.value !== asg.assignment_id) {
    replaceRecordingTarget.value = asg
  } else toggleRecording(asg)
}
const confirmRecordAgain = () => {
  const asg = replaceRecordingTarget.value
  replaceRecordingTarget.value = null
  if (asg) toggleRecording(asg)
}
const toggleRecording = async (asg) => {
  if (currentRecordingAsgId.value === asg.assignment_id) {
    if (mediaRecorder?.state === 'recording') mediaRecorder.stop()
    return
  }
  if (currentRecordingAsgId.value !== null || isSubmitting.value || isStartingRecording.value) return
  isStartingRecording.value = true
  let stream
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    if (disposed) { stream.getTracks().forEach(track => track.stop()); return }
    const recorder = new MediaRecorder(stream)
    const chunks = []
    mediaRecorder = recorder
    recorder.ondataavailable = (event) => { if (event.data.size) chunks.push(event.data) }
    recorder.onstop = () => {
      stream.getTracks().forEach(track => track.stop())
      clearInterval(timerInterval)
      currentRecordingAsgId.value = null
      const blob = new Blob(chunks, { type: recorder.mimeType || 'audio/webm' })
      if (drafts.value[asg.assignment_id]) URL.revokeObjectURL(drafts.value[asg.assignment_id].url)
      drafts.value[asg.assignment_id] = { blob, url: URL.createObjectURL(blob) }
    }
    recorder.start()
    currentRecordingAsgId.value = asg.assignment_id
    const started = Date.now()
    elapsedSeconds.value = 0
    timerInterval = setInterval(() => { elapsedSeconds.value = Math.floor((Date.now() - started) / 1000) }, 1000)
  } catch (error) {
    stream?.getTracks().forEach(track => track.stop())
    notify('Could not start recording: ' + error.message, 'error', 'mdi-microphone-off')
  } finally { isStartingRecording.value = false }
}

const uploadSubmission = async (asg) => {
  const uid = getActiveStudentId()
  const draft = drafts.value[asg.assignment_id]
  if (!uid || !draft || isSubmitting.value) return
  submittingId.value = asg.assignment_id
  const formData = new FormData()
  formData.append('assignment_id', asg.assignment_id)
  formData.append('student_id', uid)
  formData.append('student_name', localStorage.getItem('user_name') || 'Learner')
  const extension = draft.blob.type.includes('mp4') ? 'mp4' : draft.blob.type.includes('ogg') ? 'ogg' : 'webm'
  formData.append('audio', draft.blob, `submission.${extension}`)
  try {
    const res = await fetch(`${props.backendUrl}/api/assignments/submit`, { method: 'POST', body: formData })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Submission failed. Your recording is available to retry.')
    notify('Submission successful. Your recording and AI assessment have been saved.', 'success')
    URL.revokeObjectURL(draft.url)
    delete drafts.value[asg.assignment_id]
    await fetchStudentAssignments()
  } catch (error) {
    notify('Submission error: ' + error.message, 'error', 'mdi-alert-circle')
  } finally { submittingId.value = null }
}

onBeforeUnmount(() => {
  disposed = true
  clearInterval(timerInterval)
  if (mediaRecorder) {
    mediaRecorder.onstop = null
    if (mediaRecorder.state !== 'inactive') mediaRecorder.stop()
    mediaRecorder.stream.getTracks().forEach(track => track.stop())
  }
  Object.values(drafts.value).forEach(draft => URL.revokeObjectURL(draft.url))
})

onMounted(async () => {
  await fetchEnrolledClasses()
  await fetchStudentAssignments()
  await handleUrlJoinCode()
})
</script>

<style scoped>
.bg-gradient-purple {
  background: linear-gradient(135deg, #7b1fa2 0%, #4a148c 100%);
}
</style>
