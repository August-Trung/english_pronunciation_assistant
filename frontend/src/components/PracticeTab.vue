<template>
  <v-container fluid class="pa-0">
    <!-- HTTPS Warning -->
    <v-alert
      v-if="!isSecure"
      type="warning"
      density="compact"
      class="mb-3 border"
      variant="tonal"
      icon="mdi-shield-alert-outline"
      title="HTTPS Security Requirement"
      text="Microphone access requires a secure HTTPS connection. If hosting on a custom domain, please configure SSL."
    />

    <v-row class="ma-0 ga-2">
      <!-- Left column: Input, Mode selection, Library and Recording -->
      <v-col cols="12" md="6" class="pa-1">
        <v-card border flat class="pa-4 bg-white" rounded="lg">
          <!-- Step 1 Header & Mode Toggle -->
          <div class="d-flex flex-column flex-sm-row align-start align-sm-center justify-space-between mb-3 ga-2">
            <div class="d-flex align-center ga-2">
              <v-avatar color="blue-lighten-5" size="32" class="text-primary mr-1 border flex-shrink-0">
                <v-icon size="small">mdi-text-box-search-outline</v-icon>
              </v-avatar>
              <div class="text-subtitle-2 text-sm-subtitle-1 font-weight-black text-secondary">
                Step 1: {{ practiceMode === 'reading' ? 'Choose Model Sentence' : 'Choose Speaking Topic' }}
              </div>
            </div>
            <v-btn-toggle
              v-model="practiceMode"
              color="primary"
              density="compact"
              mandatory
              rounded="pill"
              variant="outlined"
              class="w-100 w-sm-auto"
            >
              <v-btn value="speaking" size="small" class="text-none font-weight-bold flex-grow-1 flex-sm-grow-0" prepend-icon="mdi-account-voice">
                Free Topic
              </v-btn>
              <v-btn value="reading" size="small" class="text-none font-weight-bold flex-grow-1 flex-sm-grow-0" prepend-icon="mdi-book-open-variant">
                Sentence Reading
              </v-btn>
            </v-btn-toggle>
          </div>

          <!-- Topic input with TTS button -->
          <v-text-field
            v-model="topic"
            :placeholder="practiceMode === 'reading' ? 'Select or enter model sentence to practice reading...' : 'Enter topic or question (e.g. What is your favorite color?)'"
            variant="outlined"
            density="comfortable"
            hide-details
            class="mb-3"
            color="primary"
          >
            <template #append-inner>
              <span class="d-inline-flex align-center cursor-pointer mr-1">
                <v-btn
                  icon="mdi-tune"
                  size="x-small"
                  variant="text"
                  color="grey-darken-1"
                  title="TTS Voice Settings (US/UK, Male/Female)"
                />
                <v-menu activator="parent" location="bottom end" :close-on-content-click="false">
                  <v-card class="pa-4 text-body-2" width="320" border elevation="4" rounded="lg">
                    <div class="text-subtitle-1 font-weight-black text-secondary mb-3 d-flex align-center justify-space-between border-bottom pb-2">
                      <span>TTS Voice Settings</span>
                      <v-icon color="primary">mdi-account-voice</v-icon>
                    </div>
                    
                    <div class="font-weight-bold text-grey-darken-3 mb-2 text-subtitle-2">1. Pronunciation Accent:</div>
                    <v-btn-toggle
                      v-model="ttsAccent"
                      color="primary"
                      density="comfortable"
                      mandatory
                      block
                      class="mb-3"
                      variant="outlined"
                      @update:model-value="saveTtsSettings"
                    >
                      <v-btn value="en-US" size="small" class="text-none font-weight-bold flex-grow-1" prepend-icon="mdi-earth">
                        US Accent
                      </v-btn>
                      <v-btn value="en-GB" size="small" class="text-none font-weight-bold flex-grow-1" prepend-icon="mdi-earth">
                        UK Accent
                      </v-btn>
                    </v-btn-toggle>

                    <div class="font-weight-bold text-grey-darken-3 mb-2 text-subtitle-2">2. Voice Gender:</div>
                    <v-btn-toggle
                      v-model="ttsGender"
                      color="primary"
                      density="comfortable"
                      mandatory
                      block
                      class="mb-4"
                      variant="outlined"
                      @update:model-value="saveTtsSettings"
                    >
                      <v-btn value="female" size="small" class="text-none font-weight-bold flex-grow-1" prepend-icon="mdi-gender-female">
                        Female Voice
                      </v-btn>
                      <v-btn value="male" size="small" class="text-none font-weight-bold flex-grow-1" prepend-icon="mdi-gender-male">
                        Male Voice
                      </v-btn>
                    </v-btn-toggle>

                    <v-btn
                      color="primary"
                      variant="tonal"
                      size="comfortable"
                      block
                      prepend-icon="mdi-volume-high"
                      class="font-weight-bold text-none"
                      @click="speakText('Hello! Welcome to Fluent English practice.')"
                    >
                      Test Selected Voice
                    </v-btn>
                  </v-card>
                </v-menu>
              </span>

              <v-btn
                v-if="topic.trim()"
                :color="isSpeaking ? 'success' : 'primary'"
                variant="text"
                density="compact"
                icon="mdi-volume-high"
                :title="isSpeaking ? 'Reading sample...' : 'Listen TTS Audio'"
                class="mr-1"
                @click="speakText(topic)"
              />
              <v-btn
                color="secondary"
                variant="text"
                density="compact"
                icon="mdi-dice-5-outline"
                :title="practiceMode === 'reading' ? 'Select Random Sentence' : 'Select Random Topic'"
                @click="getRandomTopic"
              />
            </template>
          </v-text-field>

          <!-- Dynamic Preset Library Section -->
          <div class="mb-3">
            <div class="text-caption font-weight-bold text-grey-darken-1 mb-1 d-flex align-center justify-space-between ga-2 flex-nowrap">
              <span class="d-flex align-center text-truncate">
                <v-icon color="primary" size="small" class="mr-1 flex-shrink-0">mdi-school-outline</v-icon>
                <span class="text-truncate">{{ practiceMode === 'reading' ? 'Model Sentence Library:' : 'Topic Suggestions:' }}</span>
              </span>
              <span class="text-caption text-primary font-weight-bold text-no-wrap flex-shrink-0">
                {{ GRADE_LEVELS.find(g => g.id === selectedGrade)?.badge }}
              </span>
            </div>

            <!-- Grade Tabs -->
            <v-tabs
              v-model="selectedGrade"
              color="primary"
              density="compact"
              align-tabs="start"
              class="mb-2 border-bottom"
            >
              <v-tab
                v-for="grade in GRADE_LEVELS"
                :key="grade.id"
                :value="grade.id"
                class="text-none font-weight-bold text-caption px-2 py-1"
                style="min-width: 0;"
              >
                <v-icon size="x-small" class="mr-1" :color="grade.color">{{ grade.icon }}</v-icon>
                <span class="d-none d-sm-inline">{{ grade.name }}</span>
                <span class="d-inline d-sm-none">{{ grade.shortName }}</span>
              </v-tab>
            </v-tabs>

            <!-- Mode 1: Speaking Mode Topic Chips -->
            <div v-if="practiceMode === 'speaking'" class="d-flex flex-wrap ga-1 my-2">
              <v-chip
                v-for="item in SPEAKING_TOPICS[selectedGrade]"
                :key="item"
                size="small"
                :color="topic === item ? 'primary' : 'secondary'"
                :variant="topic === item ? 'elevated' : 'tonal'"
                class="text-none"
                @click="topic = item"
              >
                <v-icon start size="x-small">mdi-comment-question-outline</v-icon>
                <span class="text-truncate" style="max-width: 220px;">{{ item }}</span>
              </v-chip>
            </div>

            <!-- Mode 2: Reading Mode Sentence Library -->
            <div v-else>
              <div v-for="cat in READING_LIBRARY[selectedGrade]" :key="cat.topic" class="mb-2">
                <div class="text-caption font-weight-black text-grey-darken-2 mb-1 d-flex align-center">
                  <v-icon size="x-small" color="primary" class="mr-1">mdi-folder-text-outline</v-icon>
                  {{ cat.topic }}
                </div>
                <div class="d-flex flex-wrap ga-1">
                  <v-chip
                    v-for="sent in cat.sentences"
                    :key="sent"
                    size="small"
                    :color="topic === sent ? 'primary' : 'grey-darken-3'"
                    :variant="topic === sent ? 'elevated' : 'tonal'"
                    class="text-none pr-1"
                    @click="topic = sent"
                  >
                    <span class="text-truncate" style="max-width: 200px;">{{ sent }}</span>
                    <v-btn
                      icon="mdi-volume-high"
                      size="x-small"
                      variant="text"
                      color="primary"
                      class="ml-1"
                      title="Listen Native Audio"
                      @click.stop="speakText(sent)"
                    />
                  </v-chip>
                </div>
              </div>
            </div>
          </div>

          <v-divider class="my-2" />

          <!-- Step 2: Voice Studio Console -->
          <div class="d-flex align-center ga-2 mb-2">
            <v-avatar color="error-lighten-5" size="32" class="text-error mr-1 border">
              <v-icon size="x-small">mdi-microphone-outline</v-icon>
            </v-avatar>
            <div class="text-subtitle-2 font-weight-black text-secondary">
              Step 2: {{ practiceMode === 'reading' ? 'Read Model Sentence Aloud' : 'Voice Speaking Response' }}
            </div>
          </div>

          <!-- Console Controls -->
          <div class="d-flex flex-column align-center justify-center py-1 w-100">
            <v-row class="ma-0 w-100 align-center justify-center mb-1" style="max-width: 320px;">
              <v-col cols="3" class="pa-0 d-flex justify-end"></v-col>
              <v-col cols="6" class="pa-0 d-flex justify-center">
                <div class="d-flex align-center justify-center position-relative" style="width: 76px; height: 76px;">
                  <v-progress-circular
                    v-if="isRecording"
                    indeterminate
                    color="error"
                    size="76"
                    width="3"
                    class="position-absolute"
                  />
                  <v-btn
                    :color="isRecording ? 'grey-darken-3' : 'error'"
                    size="large"
                    icon
                    class="elevation-2"
                    style="width: 60px; height: 60px; z-index: 2;"
                    :disabled="(!isSecure && !isLocalhost) || !topic.trim() || isAnalyzing"
                    @click="isRecording ? stopRecording() : startRecording()"
                  >
                    <v-icon size="medium">{{ isRecording ? 'mdi-stop' : 'mdi-microphone' }}</v-icon>
                  </v-btn>
                </div>
              </v-col>

              <v-col cols="3" class="pa-0 d-flex justify-start">
                <v-btn
                  v-if="!isRecording && audioUrl"
                  icon="mdi-delete-outline"
                  color="error"
                  variant="outlined"
                  density="comfortable"
                  title="Delete current recording"
                  :disabled="isAnalyzing"
                  @click="clearAudio"
                />
              </v-col>
            </v-row>

            <div class="text-center mb-2">
              <template v-if="isRecording">
                <div class="d-flex align-center justify-center text-error font-weight-black text-caption animate-pulse">
                  <v-icon color="error" class="mr-1 animate-pulse" size="x-small">mdi-record-rec</v-icon>
                  Recording in progress... ({{ formatTime(recordingDuration) }})
                </div>
              </template>
              <template v-else-if="!topic.trim()">
                <span class="text-caption font-weight-bold text-grey-darken-1" style="font-size: 11px;">
                  Please select or enter a topic first
                </span>
              </template>
            </div>

            <audio
              ref="audioPlayer"
              v-if="audioUrl"
              :src="audioUrl"
              class="d-none"
              @ended="onAudioEnded"
            />

            <!-- Custom Voice Pill Player -->
            <v-card
              v-if="audioUrl"
              border
              flat
              rounded="pill"
              class="pa-2 bg-grey-lighten-4 w-100 d-flex align-center ga-3 mb-2"
              max-width="500"
            >
              <v-btn
                :icon="isPlaying ? 'mdi-pause' : 'mdi-play'"
                color="primary"
                variant="flat"
                size="32"
                class="rounded-circle"
                title="Play / Pause"
                @click="togglePlay"
              />
              
              <v-slider
                v-model="currentTime"
                :max="audioDuration || 1"
                :step="0.05"
                color="primary"
                track-color="grey-lighten-3"
                hide-details
                density="compact"
                :thumb-size="6"
                class="ma-0 flex-grow-1"
                @update:model-value="seekAudio"
              />
              
              <div class="text-caption font-weight-black text-grey-darken-2 text-no-wrap px-2">
                {{ formatTime(currentTime) }} / {{ formatTime(audioDuration) }}
              </div>
            </v-card>

            <!-- Evaluate Action Button -->
            <v-btn
              color="success"
              variant="flat"
              block
              height="48"
              class="font-weight-black"
              prepend-icon="mdi-checkbox-marked-circle-outline"
              :disabled="!audioBlob || !topic.trim() || isAnalyzing"
              :loading="isAnalyzing"
              @click="analyzeSpeech"
            >
              Evaluate Pronunciation
            </v-btn>
          </div>
        </v-card>
      </v-col>

      <!-- Right column: Analysis Results -->
      <v-col cols="12" md="6" class="pa-1">
        <v-card border flat class="pa-4 bg-white min-h-100 d-flex flex-column" rounded="lg">
          <div class="d-flex align-center ga-2 mb-3">
            <v-avatar color="success-lighten-5" size="36" class="text-success mr-1 border">
              <v-icon size="small">mdi-trophy-outline</v-icon>
            </v-avatar>
            <div class="text-subtitle-1 font-weight-black text-secondary">Evaluation Results</div>
          </div>

          <!-- Error Alert Card -->
          <v-card v-if="errorMessage" border flat rounded="lg" class="pa-4 mb-3 bg-orange-lighten-5 text-center">
            <v-icon color="warning" size="36" class="mb-2">mdi-alert-circle-outline</v-icon>
            <div class="text-subtitle-2 font-weight-black text-warning-darken-3 mb-1">Evaluation Failed</div>
            <div class="text-caption text-grey-darken-2 mb-3">{{ errorMessage }}</div>
            <v-btn
              color="warning"
              variant="outlined"
              size="small"
              class="font-weight-bold text-none"
              prepend-icon="mdi-refresh"
              @click="errorMessage = null"
            >
              Try Again
            </v-btn>
          </v-card>

          <!-- Empty state -->
          <div v-else-if="!results && !isAnalyzing" class="d-flex flex-column align-center justify-center flex-grow-1 text-grey-darken-1 py-8">
            <v-icon size="48" color="grey-lighten-2" class="mb-2">mdi-comment-text-voice-outline</v-icon>
            <div class="text-subtitle-2 font-weight-bold text-grey">No Analysis Results Yet</div>
            <div class="text-caption text-center px-6">Complete your response on the left and click button to start evaluation!</div>
          </div>

          <!-- Loading state -->
          <div v-if="isAnalyzing" class="d-flex flex-column align-center justify-center flex-grow-1 py-8">
            <v-progress-circular indeterminate color="primary" size="48" width="4" class="mb-3" />
            <div class="text-subtitle-2 font-weight-black text-primary">{{ loadingText }}</div>
          </div>

          <!-- Score details -->
          <div v-if="results && !isAnalyzing" class="flex-grow-1">
            <!-- 1. TRANSCRIBED SPOKEN TEXT -->
            <div class="mb-3">
              <div class="text-caption font-weight-bold text-grey-darken-2 mb-1 d-flex align-center">
                <v-icon size="small" color="primary" class="mr-1">mdi-message-text-outline</v-icon>
                Transcribed Spoken Text:
              </div>
              <div class="pa-3 bg-blue-lighten-5 rounded-lg text-body-2 font-weight-bold text-primary border">
                "{{ results.transcribed_text }}"
              </div>
            </div>

            <!-- 2. OVERVIEW CARD & RELEVANCE -->
            <v-card border flat rounded="lg" class="pa-3 mb-3 bg-teal-lighten-5 border-teal">
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="d-flex align-center ga-2">
                  <v-chip color="teal" font-weight-bold size="small" variant="flat">
                    🎯 {{ practiceMode === 'reading' ? 'Accuracy' : 'Topic Relevance' }} {{ results.reading_result ? results.reading_result.accuracy.toFixed(0) : (results.ai_analysis?.topic_relevance_score || 92) }}%
                  </v-chip>
                  <span class="text-subtitle-2 font-weight-black text-teal-darken-4">
                    {{ results.score >= 8 ? 'Outstanding!' : results.score >= 6 ? 'Great Job!' : 'Keep Trying!' }}
                  </span>
                </div>
                <div :class="getScoreColorClass(results.score)" class="text-h5 font-weight-black">
                  {{ results.score.toFixed(1) }}/10
                </div>
              </div>
              <div class="text-caption text-teal-darken-4 font-weight-bold">
                {{ results.ai_analysis?.topic_comment || (practiceMode === 'reading' ? 'You completed reading the model sentence successfully!' : 'Your response stayed well on topic!') }}
              </div>
            </v-card>

            <!-- 2.1 WORD-BY-WORD READING ALIGNMENT CARD -->
            <v-card v-if="results.reading_result" border flat rounded="lg" class="pa-3 mb-3 bg-light-blue-lighten-5 border-blue">
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="text-subtitle-2 font-weight-black text-primary d-flex align-center ga-1">
                  <v-icon color="primary" size="small">mdi-bullseye-arrow</v-icon>
                  Model Sentence Word Alignment
                </div>
                <v-chip color="primary" font-weight-bold size="small" variant="flat">
                  {{ results.reading_result.spoken_words_count }}/{{ results.reading_result.target_words_count }} words
                </v-chip>
              </div>

              <div class="text-caption text-grey-darken-2 mb-2 font-weight-bold">
                Word details (Green = Correct, Yellow = Partial, Red = Missing/Incorrect):
              </div>

              <div class="d-flex flex-wrap ga-1 bg-white pa-2 rounded border">
                <v-chip
                  v-for="(item, idx) in results.reading_result.word_analysis"
                  :key="idx"
                  size="small"
                  :color="item.status === 'correct' ? 'success' : item.status === 'partial' ? 'warning' : 'error'"
                  :variant="item.status === 'missing' ? 'outlined' : 'flat'"
                  class="font-weight-bold text-none"
                >
                  <v-icon start size="x-small">
                    {{ item.status === 'correct' ? 'mdi-check' : item.status === 'partial' ? 'mdi-alert-circle-outline' : 'mdi-close' }}
                  </v-icon>
                  <span :class="{'text-decoration-line-through': item.status === 'missing'}">
                    {{ item.word }}
                  </span>
                </v-chip>
              </div>
            </v-card>

            <!-- 3. NATIVE EXPRESSIONS (3 LEVELS) -->
            <v-card v-if="results.ai_analysis?.native_suggestion || results.ai_analysis?.native_suggestions" border flat rounded="lg" class="pa-3 mb-3 bg-purple-lighten-5 border-purple">
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="text-subtitle-2 font-weight-black text-purple-darken-3 d-flex align-center ga-1">
                  <v-icon color="purple" size="small">mdi-star-face</v-icon>
                  Native Expressions (3 Levels)
                </div>
              </div>

              <!-- Rich 3-Level Native Suggestions -->
              <div v-if="results.ai_analysis.native_suggestions?.length" class="d-flex flex-column ga-2">
                <div
                  v-for="(sug, idx) in results.ai_analysis.native_suggestions"
                  :key="idx"
                  class="pa-2 pa-sm-3 bg-white rounded border d-flex align-center justify-space-between flex-wrap ga-2"
                >
                  <div class="flex-grow-1 pr-2">
                    <div class="d-flex align-center ga-2 mb-1">
                      <v-chip
                        size="x-small"
                        :color="idx === 0 ? 'success' : idx === 1 ? 'info' : 'secondary'"
                        variant="flat"
                        class="font-weight-black"
                        style="font-size: 10px; height: 18px;"
                      >
                        {{ sug.style }}
                      </v-chip>
                    </div>
                    <div class="text-subtitle-2 font-weight-black text-purple-darken-4 mb-0.5">
                      "{{ sug.text }}"
                    </div>
                    <div class="text-caption text-grey-darken-2 font-weight-bold d-flex align-center ga-1" style="font-size: 11px;">
                      <v-icon size="x-small" color="amber-darken-3">mdi-lightbulb-on-outline</v-icon>
                      <span>{{ sug.meaning }}</span>
                    </div>
                  </div>

                  <v-btn
                    color="purple"
                    variant="tonal"
                    size="small"
                    class="font-weight-bold text-none flex-shrink-0"
                    prepend-icon="mdi-volume-high"
                    @click="speakText(sug.text)"
                  >
                    Listen Audio
                  </v-btn>
                </div>
              </div>

              <!-- Single String Fallback -->
              <div v-else-if="typeof results.ai_analysis.native_suggestion === 'string'" class="pa-2 bg-white rounded border d-flex align-center justify-space-between ga-2">
                <span class="text-subtitle-2 font-weight-black text-purple-darken-4">"{{ results.ai_analysis.native_suggestion }}"</span>
                <v-btn
                  color="purple"
                  variant="flat"
                  size="small"
                  class="text-none font-weight-bold"
                  prepend-icon="mdi-volume-high"
                  @click="speakText(results.ai_analysis.native_suggestion)"
                />
              </div>
            </v-card>

            <!-- IPA PHONETIC EVALUATION (INTERNATIONAL STANDARD) -->
            <v-card v-if="results.ipa_analysis" border flat rounded="lg" class="pa-3 mb-3 bg-teal-lighten-5 border-teal">
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="text-subtitle-2 font-weight-black text-teal-darken-4 d-flex align-center ga-1">
                  <v-icon color="teal-darken-3" size="small">mdi-phonetics</v-icon>
                  <span>IPA Phonetic Evaluation (International Standard)</span>
                </div>
                <v-chip color="teal-darken-3" font-weight-bold size="small" variant="flat">
                  IPA {{ results.ipa_analysis.ipa_accuracy }}%
                </v-chip>
              </div>

              <!-- Full IPA sentence comparison -->
              <div class="bg-white pa-2 rounded border mb-2 text-caption">
                <div class="d-flex align-center ga-2 mb-1">
                  <span class="font-weight-black text-primary">Target IPA:</span>
                  <span class="font-weight-bold text-teal-darken-4 font-mono">{{ results.ipa_analysis.target_full_ipa }}</span>
                </div>
                <div class="d-flex align-center ga-2">
                  <span class="font-weight-black text-secondary">Spoken IPA:</span>
                  <span class="font-weight-bold text-indigo-darken-3 font-mono">{{ results.ipa_analysis.spoken_full_ipa }}</span>
                </div>
              </div>

              <!-- Pitch Intonation Chart F0 -->
              <div v-if="results.ipa_analysis.pitch_analysis?.pitch_points?.length" class="bg-white pa-3 rounded border mb-3">
                <div class="d-flex align-center justify-space-between mb-2">
                  <div class="text-caption font-weight-black text-indigo-darken-3 d-flex align-center ga-1">
                    <v-icon color="indigo" size="x-small">mdi-chart-bell-curve-cumulative</v-icon>
                    <span>Pitch Contour & Intonation Chart (F0)</span>
                  </div>
                  <v-chip size="x-small" color="indigo" variant="tonal" class="font-weight-black">
                    Intonation Match {{ results.ipa_analysis.pitch_analysis.pitch_accuracy }}%
                  </v-chip>
                </div>
                <div class="d-flex align-center justify-space-between text-caption text-grey mb-1" style="font-size: 10px;">
                  <span><v-icon size="x-small" color="primary">mdi-minus</v-icon> Native Speaker</span>
                  <span><v-icon size="x-small" color="amber-darken-3">mdi-minus</v-icon> Learner Voice</span>
                </div>
                <!-- SVG Pitch Chart -->
                <div class="w-100 bg-grey-lighten-4 rounded pa-2 d-flex align-end justify-space-between" style="height: 60px; position: relative;">
                  <div
                    v-for="(pt, p_idx) in results.ipa_analysis.pitch_analysis.pitch_points"
                    :key="p_idx"
                    class="d-flex flex-column align-center justify-end h-100"
                    style="flex: 1;"
                  >
                    <div
                      v-if="pt.student_f0"
                      class="bg-amber-darken-3 rounded-circle"
                      :style="{ height: `${Math.min(48, Math.max(6, (pt.student_f0 - 70) / 4))}px`, width: '4px' }"
                    ></div>
                    <div
                      class="bg-primary rounded-circle mt-1"
                      :style="{ height: `${Math.min(48, Math.max(6, (pt.native_f0 - 70) / 4))}px`, width: '3px', opacity: 0.6 }"
                    ></div>
                  </div>
                </div>
              </div>

              <!-- Connected Speech & Liaisons -->
              <div v-if="results.ipa_analysis.linking_pairs?.length" class="bg-amber-lighten-5 pa-2.5 rounded border border-amber mb-3">
                <div class="text-caption font-weight-black text-amber-darken-4 mb-1 d-flex align-center ga-1">
                  <v-icon color="amber-darken-4" size="x-small">mdi-link-variant</v-icon>
                  <span>Connected Speech & Liaisons:</span>
                </div>
                <div class="d-flex flex-wrap ga-2 mt-1">
                  <v-chip
                    v-for="(pair, l_idx) in results.ipa_analysis.linking_pairs"
                    :key="l_idx"
                    size="x-small"
                    color="amber-darken-4"
                    variant="flat"
                    class="font-weight-black"
                  >
                    {{ pair.word1 }} <v-icon size="x-small" class="mx-0.5">mdi-link-variant</v-icon> {{ pair.word2 }} ({{ pair.ipa_link }})
                  </v-chip>
                </div>
              </div>

              <!-- Word by word IPA breakdown chips -->
              <div class="d-flex flex-wrap ga-2">
                <div
                  v-for="(w_ipa, idx) in (results.ipa_analysis.words_ipa || [])"
                  :key="idx"
                  class="pa-2 bg-white rounded border d-flex flex-column align-center flex-grow-1"
                  style="min-width: 95px; position: relative;"
                >
                  <div class="text-caption font-weight-black text-grey-darken-3 d-flex align-center ga-0.5">
                    <span>{{ w_ipa.word }}</span>
                    <v-icon v-if="w_ipa.stress_note" size="x-small" color="deep-orange">mdi-fire</v-icon>
                  </div>
                  <v-chip
                    size="x-small"
                    variant="flat"
                    :color="w_ipa.status === 'correct' ? 'success' : w_ipa.status === 'partial' ? 'warning' : 'error'"
                    class="font-weight-bold mt-1"
                    style="font-size: 10px;"
                  >
                    {{ w_ipa.target_ipa }}
                  </v-chip>
                  <div v-if="w_ipa.note" class="text-caption text-error font-weight-bold text-center mt-1 d-flex align-center ga-0.5" style="font-size: 9px; line-height: 1.1;">
                    <v-icon size="x-small" color="error">mdi-alert-circle-outline</v-icon>
                    <span>{{ w_ipa.note }}</span>
                  </div>

                  <!-- Button Xem Khẩu Hình 2D/3D -->
                  <v-btn
                    density="compact"
                    size="x-small"
                    variant="tonal"
                    color="teal-darken-3"
                    class="mt-1 font-weight-bold text-none"
                    style="font-size: 8.5px; height: 18px;"
                    prepend-icon="mdi-lips"
                    @click="openArticulationGuide(w_ipa.word, w_ipa.target_ipa)"
                  >
                    Articulation
                  </v-btn>
                </div>
              </div>
            </v-card>

            <!-- 4. GRAMMAR & VOCABULARY VISUAL FIXES -->
            <v-card border flat rounded="lg" class="pa-3 mb-3" :class="validGrammarFixes.length ? 'bg-orange-lighten-5 border-orange' : 'bg-green-lighten-5 border-green'">
              <div class="text-subtitle-2 font-weight-black mb-2 d-flex align-center ga-1" :class="validGrammarFixes.length ? 'text-orange-darken-4' : 'text-success'">
                <v-icon :color="validGrammarFixes.length ? 'orange-darken-3' : 'success'" size="small">
                  {{ validGrammarFixes.length ? 'mdi-auto-fix' : 'mdi-check-decagram-outline' }}
                </v-icon>
                Grammar & Vocabulary Visual Fixes
              </div>
              <template v-if="validGrammarFixes.length > 0">
                <div v-for="(fix, idx) in validGrammarFixes" :key="idx" class="mb-2 pa-3 bg-white rounded-lg border">
                  <!-- Type Badge -->
                  <div class="d-flex align-center ga-2 mb-2">
                    <v-chip v-if="fix.type" color="orange-darken-3" size="x-small" variant="flat" class="font-weight-black" style="font-size: 10.5px; height: 20px;">
                      <v-icon size="x-small" start>mdi-tag-outline</v-icon>
                      {{ fix.type }}
                    </v-chip>
                  </div>

                  <!-- Text rows for original vs fixed English sentences -->
                  <div class="d-flex flex-column ga-2 mb-2 pl-1">
                    <div class="d-flex align-center ga-2 text-body-2 font-weight-bold text-error flex-wrap">
                      <v-chip color="error" size="x-small" variant="tonal" class="font-weight-black flex-shrink-0" style="font-size: 10px; height: 20px;">
                        <v-icon size="x-small" start>mdi-close-circle-outline</v-icon>
                        Needs Fix
                      </v-chip>
                      <span class="text-body-2 font-weight-bold text-error">"{{ fix.original }}"</span>
                    </div>

                    <div class="d-flex align-center ga-2 text-body-2 font-weight-bold text-success flex-wrap">
                      <v-chip color="success" size="x-small" variant="flat" class="font-weight-black flex-shrink-0" style="font-size: 10px; height: 20px;">
                        <v-icon size="x-small" start>mdi-check-circle-outline</v-icon>
                        Corrected
                      </v-chip>
                      <span class="text-body-2 font-weight-black text-success text-decoration-underline">"{{ fix.fixed }}"</span>
                    </div>
                  </div>

                  <!-- Reason explanation -->
                  <div v-if="fix.reason" class="text-caption text-grey-darken-3 pl-1 pt-2 border-t mt-2" style="line-height: 1.5;">
                    <v-icon size="x-small" color="amber-darken-3" class="mr-1">mdi-lightbulb-on-outline</v-icon>
                    <strong>Explanation:</strong> {{ fix.reason }}
                  </div>
                </div>
              </template>
              <template v-else>
                <div class="d-flex align-center ga-2 text-caption text-success font-weight-bold bg-white pa-2 rounded border">
                  <v-icon color="success" size="small">mdi-check-circle-outline</v-icon>
                  <span>Perfect grammar and vocabulary structure with zero errors!</span>
                </div>
              </template>
            </v-card>

            <!-- 5. DETAILED SKILL SCORES TABLE -->
            <div class="mb-3">
              <div class="text-caption font-weight-bold text-grey-darken-1 mb-2">
                <v-icon size="small" color="primary" class="mr-1">mdi-chart-bar</v-icon>
                Detailed Skill Scores:
              </div>
              
              <v-row class="ma-0 bg-grey-lighten-5 rounded-lg border pa-2 align-center justify-space-between" no-gutters>
                <v-col
                  v-for="item in scoreCriteria"
                  :key="item.key"
                  cols="4"
                  sm="2"
                  class="pa-1 text-center"
                >
                  <div class="text-caption text-grey-darken-2 font-weight-bold d-flex align-center justify-center">
                    <span>{{ item.name }}</span>
                    <span class="d-inline-flex align-center cursor-pointer ml-1">
                      <v-icon size="x-small" color="grey-darken-1" style="font-size: 14px;">
                        mdi-help-circle-outline
                      </v-icon>
                      <v-menu activator="parent" location="top center" transition="scale-transition">
                        <v-card class="pa-2 text-caption text-left text-grey-darken-3" max-width="240" border elevation="2" rounded="md">
                          {{ item.desc }}
                        </v-card>
                      </v-menu>
                    </span>
                  </div>
                  <div class="text-subtitle-2 font-weight-black text-primary mt-1">
                    {{ (results.ai_analysis?.scores?.[item.key.toLowerCase()] || results.breakdown[item.key]).toFixed(1) }}/2
                  </div>
                </v-col>
                <v-col cols="4" sm="2" class="pa-1 d-flex flex-column justify-center align-center">
                  <div class="text-caption text-grey-darken-2 font-weight-bold d-flex align-center justify-center">
                    <span>Clarity Rate</span>
                    <span class="d-inline-flex align-center cursor-pointer ml-1">
                      <v-icon size="x-small" color="grey-darken-1" style="font-size: 14px;">
                        mdi-help-circle-outline
                      </v-icon>
                      <v-menu activator="parent" location="top center" transition="scale-transition">
                        <v-card class="pa-2 text-caption text-left text-grey-darken-3" max-width="240" border elevation="2" rounded="md">
                          Measures voice clarity and microphone ambient noise level for 100% accurate AI recognition.
                        </v-card>
                      </v-menu>
                    </span>
                  </div>
                  <div class="text-subtitle-2 font-weight-black text-success mt-1">
                    {{ results.ai_analysis?.scores?.clarity_percent || Math.round((results.breakdown.WhisperConfidence || 0) * 100) }}%
                  </div>
                </v-col>
              </v-row>
            </div>

            <!-- 6. NHẬN XÉT CHI TIẾT -->
            <div>
              <div class="text-caption font-weight-bold text-grey-darken-1 mb-2">
                <v-icon size="small" color="primary" class="mr-1">mdi-account-school-outline</v-icon>
                Detailed Pedagogical Evaluation:
              </div>
              <v-card border flat rounded="lg" class="pa-3 bg-grey-lighten-4">
                <template v-if="results.ai_analysis?.pedagogical_feedback">
                  <div class="d-flex align-start ga-2 mb-2">
                    <v-icon size="small" color="blue" class="mt-1">mdi-waveform</v-icon>
                    <div>
                      <strong class="text-subtitle-2 text-blue-darken-3">Fluency & Expression:</strong>
                      <div class="text-caption text-grey-darken-3">{{ results.ai_analysis.pedagogical_feedback.fluency }}</div>
                    </div>
                  </div>
                  
                  <div class="d-flex align-start ga-2 mb-2">
                    <v-icon size="small" color="purple" class="mt-1">mdi-book-alphabet</v-icon>
                    <div>
                      <strong class="text-subtitle-2 text-purple-darken-3">Vocabulary & Word Choice:</strong>
                      <div class="text-caption text-grey-darken-3">{{ results.ai_analysis.pedagogical_feedback.vocabulary }}</div>
                    </div>
                  </div>
                  
                  <div class="d-flex align-start ga-2 mb-2">
                    <v-icon size="small" color="orange" class="mt-1">mdi-lead-pencil</v-icon>
                    <div>
                      <strong class="text-subtitle-2 text-orange-darken-4">Grammar & Sentence Structure:</strong>
                      <div class="text-caption text-grey-darken-3">{{ results.ai_analysis.pedagogical_feedback.grammar }}</div>
                    </div>
                  </div>
                  
                  <div class="d-flex align-start ga-2 mb-2">
                    <v-icon size="small" color="teal" class="mt-1">mdi-microphone-outline</v-icon>
                    <div>
                      <strong class="text-subtitle-2 text-teal-darken-4">Pronunciation & Clarity:</strong>
                      <div class="text-caption text-grey-darken-3">{{ results.ai_analysis.pedagogical_feedback.pronunciation }}</div>
                    </div>
                  </div>
                  
                  <div class="d-flex align-start ga-2 mb-2">
                    <v-icon size="small" color="indigo" class="mt-1">mdi-forum-outline</v-icon>
                    <div>
                      <strong class="text-subtitle-2 text-indigo-darken-3">Communication & Relevance:</strong>
                      <div class="text-caption text-grey-darken-3">{{ results.ai_analysis.pedagogical_feedback.communication }}</div>
                    </div>
                  </div>
                  
                  <v-divider class="my-2" />
                  
                  <div class="d-flex align-start ga-2 text-amber-darken-4">
                    <v-icon size="small" color="amber-darken-3" class="mt-1">mdi-lightbulb-on</v-icon>
                    <div>
                      <strong class="text-subtitle-2">ACTIONABLE ADVICE:</strong>
                      <div class="text-caption font-weight-bold text-grey-darken-3">{{ results.ai_analysis.pedagogical_feedback.advice }}</div>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <div class="text-caption text-grey-darken-3 whitespace-pre-line">{{ cleanFeedback(results.feedback) }}</div>
                </template>
              </v-card>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- MODAL SƠ ĐỒ HƯỚNG DẪN KHẨU HÌNH RĂNG / LƯỠI / MÔI 2D/3D -->
    <v-dialog v-model="showArticulationModal" max-width="500">
      <v-card v-if="selectedArticulation" border rounded="lg" class="pa-4">
        <div class="d-flex align-center justify-space-between mb-3 border-b pb-2">
          <div class="d-flex align-center ga-2">
            <v-avatar color="teal-lighten-5" size="40" class="text-teal-darken-3 border border-teal">
              <v-icon size="medium">mdi-lips</v-icon>
            </v-avatar>
            <div>
              <div class="text-subtitle-1 font-weight-black text-teal-darken-4">{{ selectedArticulation.title }}</div>
              <div class="text-caption font-weight-bold text-primary font-mono">Phiên âm: {{ selectedArticulation.ipa }}</div>
            </div>
          </div>
          <v-btn icon="mdi-close" variant="text" density="compact" @click="showArticulationModal = false" />
        </div>

        <!-- Sơ Đồ Khẩu Hình Đồ Họa 2D/3D -->
        <div class="bg-teal-lighten-5 border border-teal pa-4 rounded-lg mb-4 text-center">
          <div class="d-flex justify-center align-center ga-3 mb-2">
            <div class="border pa-2 bg-white rounded-circle elevation-1 d-flex align-center justify-center" style="width: 64px; height: 64px;">
              <v-icon size="36" color="teal-darken-3">mdi-lips</v-icon>
            </div>
            <v-icon size="medium" color="teal-darken-2">mdi-arrow-right-bold-outline</v-icon>
            <div class="border pa-2 bg-white rounded-circle elevation-1 d-flex align-center justify-center" style="width: 64px; height: 64px;">
              <v-icon size="36" color="light-blue-darken-2">mdi-weather-windy</v-icon>
            </div>
            <v-icon size="medium" color="teal-darken-2">mdi-arrow-right-bold-outline</v-icon>
            <div class="border pa-2 bg-white rounded-circle elevation-1 d-flex align-center justify-center" style="width: 64px; height: 64px;">
              <v-icon size="36" color="deep-orange">mdi-account-voice</v-icon>
            </div>
          </div>
          <div class="text-caption font-weight-black text-teal-darken-4">3-Step Articulation Flow: Lips & Teeth ➔ Airflow ➔ Sound Release</div>
        </div>

        <div class="text-caption">
          <div class="bg-grey-lighten-4 pa-3.5 rounded-lg border mb-3" style="line-height: 1.55;">
            <span class="font-weight-black text-grey-darken-4 d-block mb-1.5 d-flex align-center ga-1">
              <v-icon color="pink" size="small">mdi-lips</v-icon>
              <span class="text-subtitle-2 font-weight-bold">1. Lips & Teeth Position:</span>
            </span>
            <span class="text-grey-darken-3 d-block pl-6">{{ selectedArticulation.mouth_position }}</span>
          </div>

          <div class="bg-grey-lighten-4 pa-3.5 rounded-lg border mb-3" style="line-height: 1.55;">
            <span class="font-weight-black text-grey-darken-4 d-block mb-1.5 d-flex align-center ga-1">
              <v-icon color="deep-orange" size="small">mdi-emoticon-tongue-outline</v-icon>
              <span class="text-subtitle-2 font-weight-bold">2. Tongue Placement:</span>
            </span>
            <span class="text-grey-darken-3 d-block pl-6">{{ selectedArticulation.tongue_position }}</span>
          </div>

          <div class="bg-grey-lighten-4 pa-3.5 rounded-lg border mb-3" style="line-height: 1.55;">
            <span class="font-weight-black text-grey-darken-4 d-block mb-1.5 d-flex align-center ga-1">
              <v-icon color="light-blue" size="small">mdi-weather-windy</v-icon>
              <span class="text-subtitle-2 font-weight-bold">3. Airflow & Vocal Cords:</span>
            </span>
            <span class="text-grey-darken-3 d-block pl-6">{{ selectedArticulation.airflow }}</span>
          </div>

          <div class="bg-amber-lighten-5 pa-3.5 rounded-lg border border-amber mb-2" style="line-height: 1.55;">
            <span class="font-weight-black text-amber-darken-4 d-block mb-1.5 d-flex align-center ga-1">
              <v-icon color="amber-darken-3" size="small">mdi-lightbulb-on-outline</v-icon>
              <span class="text-subtitle-2 font-weight-bold">Quick Practice Tip:</span>
            </span>
            <span class="text-amber-darken-4 font-weight-bold d-block pl-6">{{ selectedArticulation.tip }}</span>
          </div>
        </div>

        <v-card-actions class="px-0 pt-3 pb-0">
          <v-spacer />
          <v-btn color="primary" variant="flat" class="font-weight-black text-none" @click="speakText(selectedArticulation.ipa)">
            <v-icon class="mr-1">mdi-volume-high</v-icon> Listen Sample Sound
          </v-btn>
          <v-btn color="grey-darken-1" variant="outlined" class="font-weight-bold text-none" @click="showArticulationModal = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { GRADE_LEVELS, SPEAKING_TOPICS, READING_LIBRARY } from '../constants/topics.js'

// State Modal Khẩu Hình 2D/3D
const showArticulationModal = ref(false)
const selectedArticulation = ref(null)

const ARTICULATION_GUIDES = {
  's': {
    title: 'Fricative Consonant /s/',
    ipa: '/s/',
    mouth_position: 'Slightly close teeth, pull lip corners sideways in a gentle smile.',
    tongue_position: 'Raise tongue tip close to upper alveolar ridge without touching, forming a narrow gap.',
    airflow: 'Continuous unvoiced airflow pushed through the gap between tongue tip and ridge (Voiceless).',
    tip: 'Sustain the airflow for 1-2 seconds to produce a crisp sibilant sound.'
  },
  'z': {
    title: 'Voiced Fricative Consonant /z/',
    ipa: '/z/',
    mouth_position: 'Same mouth and teeth position as /s/.',
    tongue_position: 'Raise tongue tip near upper alveolar ridge.',
    airflow: 'Identical mouth shape to /s/ but with vocal cord vibration (Voiced). Feel throat vibration.',
    tip: 'Place fingers on your throat; you must feel vocal cord vibration while producing /z/.'
  },
  't': {
    title: 'Plosive Consonant /t/',
    ipa: '/t/',
    mouth_position: 'Slightly open lips naturally.',
    tongue_position: 'Press tongue tip firmly against upper alveolar ridge to block airflow completely.',
    airflow: 'Release tongue tip downward rapidly to burst trapped air with a sharp sound.',
    tip: 'Place hand in front of mouth; feel a sharp burst of air on release.'
  },
  'd': {
    title: 'Voiced Plosive Consonant /d/',
    ipa: '/d/',
    mouth_position: 'Slightly open lips naturally.',
    tongue_position: 'Press tongue tip firmly against upper alveolar ridge.',
    airflow: 'Release tongue tip downward while vibrating vocal cords.',
    tip: 'Deeper resonant burst than /t/ with gentle throat vibration.'
  },
  'th': {
    title: 'Dental Consonants /θ/ & /ð/',
    ipa: '/θ/ - /ð/',
    mouth_position: 'Place tongue tip gently between upper and lower front teeth.',
    tongue_position: 'Relaxed tongue tip resting lightly between teeth.',
    airflow: 'Push air out between upper teeth and tongue surface.',
    tip: 'Do not retract tongue inside too quickly! Extend tongue tip outward 1-2 cm.'
  },
  'r': {
    title: 'Retroflex Consonant /r/',
    ipa: '/r/',
    mouth_position: 'Slightly round lips forward.',
    tongue_position: 'Curl tongue tip backward toward roof of mouth (without touching).',
    airflow: 'Airflow passes through space between palate and tense curved tongue.',
    tip: 'Imagine your tongue spooning upward and curving backward.'
  },
  'l': {
    title: 'Lateral Consonant /l/',
    ipa: '/l/',
    mouth_position: 'Open mouth naturally.',
    tongue_position: 'Press tongue tip firmly against upper alveolar ridge behind front teeth.',
    airflow: 'Airflow escapes laterally around the sides of the tongue.',
    tip: 'Keep tongue tip anchored against upper ridge upon sound completion.'
  }
}

const openArticulationGuide = (word, ipaStr) => {
  const w = (word || '').toLowerCase()
  if (w.includes('th') || (ipaStr || '').includes('θ') || (ipaStr || '').includes('ð')) {
    selectedArticulation.value = ARTICULATION_GUIDES['th']
  } else if (w.endsWith('s') || w.endsWith('z') || (ipaStr || '').includes('s')) {
    selectedArticulation.value = ARTICULATION_GUIDES['s']
  } else if (w.endsWith('t') || (ipaStr || '').includes('t')) {
    selectedArticulation.value = ARTICULATION_GUIDES['t']
  } else if (w.includes('r') || (ipaStr || '').includes('r')) {
    selectedArticulation.value = ARTICULATION_GUIDES['r']
  } else if (w.includes('l') || (ipaStr || '').includes('l')) {
    selectedArticulation.value = ARTICULATION_GUIDES['l']
  } else {
    selectedArticulation.value = ARTICULATION_GUIDES['s']
  }
  showArticulationModal.value = true
}

const props = defineProps({
  backendUrl: {
    type: String,
    required: true
  },
  userId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['add-history', 'history-updated'])

// State
const topic = ref('')
const practiceMode = ref('speaking') // 'speaking' | 'reading'
const selectedGrade = ref('primary')
const isSpeaking = ref(false)

const ttsAccent = ref(localStorage.getItem('fluent_tts_accent') || 'en-US')
const ttsGender = ref(localStorage.getItem('fluent_tts_gender') || 'female')

const saveTtsSettings = () => {
  localStorage.setItem('fluent_tts_accent', ttsAccent.value)
  localStorage.setItem('fluent_tts_gender', ttsGender.value)
}

const isRecording = ref(false)
const recordingDuration = ref(0)
const audioUrl = ref(null)
const audioBlob = ref(null)
const audioDuration = ref(0)
const isPlaying = ref(false)
const currentTime = ref(0)
const audioPlayer = ref(null)
const isAnalyzing = ref(false)
const loadingText = ref('Processing speech audio...')
const results = ref(null)
const errorMessage = ref(null)

const isSecure = ref(window.isSecureContext)
const isLocalhost = ref(window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')

let mediaRecorder = null
let audioChunks = []
let durationTimer = null
let animationFrameId = null

const scoreCriteria = [
  { key: 'Pronunciation', name: 'Pronunciation', desc: 'Evaluates accuracy of individual words and IPA phonetics. Articulate clearly and pronounce ending consonants (/s/, /t/) for max score.' },
  { key: 'Fluency', name: 'Fluency', desc: 'Measures speaking pace and natural rhythm. Speak smoothly with minimal hesitations and maintain sentences over 15 words for higher score.' },
  { key: 'Grammar', name: 'Grammar', desc: 'Evaluates structural correctness. Use proper verb tenses, complete subject-verb clauses, and avoid basic grammatical errors.' },
  { key: 'Vocabulary', name: 'Vocabulary', desc: 'Measures lexical diversity and context appropriateness. Use topic-relevant vocabulary and avoid repeating simple words.' },
  { key: 'Communication', name: 'Communication', desc: 'Evaluates expressiveness and topic relevance. Address prompt directly and elaborate your thoughts with detailed reasoning.' }
]

const loadingTexts = [
  'Transcribing spoken audio to text...',
  'Analyzing IPA phonetic accuracy...',
  'Evaluating grammar & vocabulary structure...',
  'Generating academic pedagogical feedback...'
]

let loadingInterval = null

// TTS Function
const speakText = (text) => {
  if (!text || !('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = ttsAccent.value
  utterance.rate = 0.85
  
  const voices = window.speechSynthesis.getVoices()
  
  // Filter by Accent (en-US vs en-GB)
  let matchingVoices = voices.filter(v => v.lang.toLowerCase().includes(ttsAccent.value.toLowerCase()))
  if (!matchingVoices.length) {
    matchingVoices = voices.filter(v => v.lang.startsWith('en'))
  }
  
  // Filter by Gender (Female vs Male)
  let selectedVoice = null
  if (matchingVoices.length) {
    const isFemaleReq = ttsGender.value === 'female'
    const femaleKeywords = ['female', 'zira', 'hazel', 'susan', 'catherine', 'jenny', 'eva', 'samantha', 'victoria']
    const maleKeywords = ['male', 'david', 'mark', 'george', 'guy', 'ryan', 'james', 'alex', 'daniel']
    
    const targetKeywords = isFemaleReq ? femaleKeywords : maleKeywords
    
    selectedVoice = matchingVoices.find(v => targetKeywords.some(kw => v.name.toLowerCase().includes(kw)))
    
    if (!selectedVoice) {
      selectedVoice = matchingVoices[0]
    }
  }
  
  if (selectedVoice) {
    utterance.voice = selectedVoice
  }
  
  utterance.onstart = () => { isSpeaking.value = true }
  utterance.onend = () => { isSpeaking.value = false }
  utterance.onerror = () => { isSpeaking.value = false }
  
  window.speechSynthesis.speak(utterance)
}

// Functions
const getRandomTopic = () => {
  if (practiceMode.value === 'speaking') {
    const list = SPEAKING_TOPICS[selectedGrade.value] || []
    const current = topic.value
    let next = current
    while (next === current && list.length > 1) {
      next = list[Math.floor(Math.random() * list.length)]
    }
    topic.value = next || list[0]
  } else {
    const allSentences = []
    const groups = READING_LIBRARY[selectedGrade.value] || []
    groups.forEach(g => allSentences.push(...g.sentences))
    const current = topic.value
    let next = current
    while (next === current && allSentences.length > 1) {
      next = allSentences[Math.floor(Math.random() * allSentences.length)]
    }
    topic.value = next || allSentences[0]
  }
}

const validGrammarFixes = computed(() => {
  if (!results.value?.ai_analysis?.grammar_fixes) return []
  return results.value.ai_analysis.grammar_fixes.filter(f => 
    f && f.original && f.fixed && String(f.original).trim() !== '' && String(f.fixed).trim() !== ''
  )
})

const startRecording = async () => {
  audioChunks = []
  clearAudio()
  
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream)
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }
    
    mediaRecorder.onstop = () => {
      const mimeType = mediaRecorder.mimeType || 'audio/webm'
      audioBlob.value = new Blob(audioChunks, { type: mimeType })
      audioUrl.value = URL.createObjectURL(audioBlob.value)
      
      const tempAudio = new Audio(audioUrl.value)
      tempAudio.onloadedmetadata = () => {
        audioDuration.value = tempAudio.duration
      }
    }
    
    mediaRecorder.start()
    isRecording.value = true
    recordingDuration.value = 0
    
    durationTimer = setInterval(() => {
      recordingDuration.value += 1
    }, 1000)
  } catch (err) {
    errorMessage.value = "Microphone access denied. Please allow microphone permissions in your browser."
    console.error(err)
  }
}

const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
    mediaRecorder.stream.getTracks().forEach(track => track.stop())
  }
  isRecording.value = false
  clearInterval(durationTimer)
}

const updateProgressLoop = () => {
  if (audioPlayer.value && isPlaying.value) {
    currentTime.value = audioPlayer.value.currentTime
    animationFrameId = requestAnimationFrame(updateProgressLoop)
  }
}

const togglePlay = () => {
  if (!audioPlayer.value) return
  if (isPlaying.value) {
    audioPlayer.value.pause()
    isPlaying.value = false
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId)
    }
  } else {
    if (currentTime.value >= audioDuration.value) {
      audioPlayer.value.currentTime = 0
      currentTime.value = 0
    }
    audioPlayer.value.play()
    isPlaying.value = true
    animationFrameId = requestAnimationFrame(updateProgressLoop)
  }
}

const onAudioEnded = () => {
  isPlaying.value = false
  currentTime.value = audioDuration.value
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
}

const seekAudio = (val) => {
  if (audioPlayer.value) {
    audioPlayer.value.currentTime = val
    currentTime.value = val
  }
}

const clearAudio = () => {
  if (audioPlayer.value) {
    audioPlayer.value.pause()
  }
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
  audioUrl.value = null
  audioBlob.value = null
  audioDuration.value = 0
  currentTime.value = 0
  isPlaying.value = false
  errorMessage.value = null
  results.value = null
}

const formatTime = (secs) => {
  const roundedSecs = Math.floor(secs || 0)
  const m = Math.floor(roundedSecs / 60)
  const s = roundedSecs % 60
  return `${m}:${s < 10 ? '0' : ''}${s}`
}

const startLoadingAnimation = () => {
  let idx = 0
  loadingText.value = loadingTexts[idx]
  loadingInterval = setInterval(() => {
    idx = (idx + 1) % loadingTexts.length
    loadingText.value = loadingTexts[idx]
  }, 2500)
}

const stopLoadingAnimation = () => {
  clearInterval(loadingInterval)
}

const analyzeSpeech = async () => {
  if (!audioBlob.value || !topic.value.trim()) return
  
  isAnalyzing.value = true
  results.value = null
  startLoadingAnimation()
  
  try {
    const formData = new FormData()
    const ext = audioBlob.value.type.includes('mp4') ? 'mp4' : 
                audioBlob.value.type.includes('ogg') ? 'ogg' : 'webm'
    
    formData.append('audio', audioBlob.value, `recording.${ext}`)
    formData.append('topic', topic.value)
    formData.append('mode', practiceMode.value)
    formData.append('target_text', topic.value)
    if (props.userId) {
      formData.append('user_id', props.userId)
    }
    
    const response = await fetch(`${props.backendUrl}/api/analyze`, {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      const errData = await response.json()
      throw new Error(errData.detail || 'Failed to evaluate speech audio.')
    }
    
    const data = await response.json()
    if (data.success) {
      results.value = data
      emit('history-updated')
    }
  } catch (err) {
    errorMessage.value = err.message
    console.error(err)
  } finally {
    isAnalyzing.value = false
    stopLoadingAnimation()
  }
}

const getScoreColor = (score) => {
  if (score >= 8) return 'success'
  if (score >= 6) return 'warning'
  if (score >= 4) return 'orange'
  return 'error'
}

const getScoreColorClass = (score) => {
  if (score >= 8) return 'text-success'
  if (score >= 6) return 'text-warning'
  if (score >= 4) return 'text-orange-darken-2'
  return 'text-error'
}

const cleanFeedback = (text) => {
  if (!text) return ''
  return text
    .replace(/###\s*/g, '')
    .replace(/\*\*/g, '')
    .replace(/---\s*/g, '')
    .trim()
}

const getGradeMessage = (score) => {
  if (score >= 8) return 'Outstanding! Your pronunciation is exceptionally accurate!'
  if (score >= 6) return 'Great job! Keep practicing to achieve native fluency!'
  if (score >= 4) return 'Satisfactory! Check the detailed feedback below to improve!'
  return 'Keep trying! Daily practice will rapidly build your speaking skills!'
}

onUnmounted(() => {
  if (durationTimer) clearInterval(durationTimer)
  if (loadingInterval) clearInterval(loadingInterval)
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  if ('speechSynthesis' in window) window.speechSynthesis.cancel()
})
</script>

<style scoped>
.animate-pulse {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.4; }
  100% { opacity: 1; }
}

.whitespace-pre-line {
  white-space: pre-line;
}
</style>
