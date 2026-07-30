<template>
  <v-container fluid class="pa-0 max-width-700">
    <!-- Rich Teal Gradient Banner Card -->
    <v-card border flat class="pa-3 pa-sm-4 mb-4 text-white rounded-lg" style="background: linear-gradient(135deg, #009688 0%, #004D40 100%);">
      <div class="d-flex align-center ga-2 ga-sm-3">
        <v-avatar color="teal-lighten-4" size="40" class="flex-shrink-0">
          <v-icon color="teal-darken-4" size="default">mdi-waveform</v-icon>
        </v-avatar>
        <div>
          <div class="text-subtitle-1 text-sm-h6 font-weight-black tracking-tight leading-tight">SHADOWING STUDIO</div>
          <div class="text-caption text-teal-lighten-4">Master natural native rhythm and intonation by speaking along with AI models</div>
        </div>
      </div>
    </v-card>

    <!-- Main Content -->
    <div class="mb-4">
      <!-- Level Selection Filter -->
      <div class="d-flex align-center justify-space-between mb-3 flex-wrap ga-2">
        <div class="text-subtitle-2 font-weight-black text-grey-darken-3 d-flex align-center ga-1">
          <v-icon color="teal" size="small">mdi-text-box-search-outline</v-icon>
          <span>Select Practice Level:</span>
        </div>

        <v-btn-toggle
          v-model="selectedLevel"
          mandatory
          color="teal"
          density="compact"
          variant="outlined"
          rounded="pill"
        >
          <v-btn value="easy" size="x-small">Easy</v-btn>
          <v-btn value="medium" size="x-small">Medium</v-btn>
          <v-btn value="hard" size="x-small">Hard</v-btn>
        </v-btn-toggle>
      </div>

      <!-- Active Sample Sentence Box -->
      <div class="pa-4 rounded-lg mb-4 text-center border" style="background: linear-gradient(135deg, #E0F2F1 0%, #B2DFDB 100%);">
        <div class="text-caption text-teal-darken-4 font-weight-bold mb-1">
          AI Suggested Model:
        </div>

        <div class="text-subtitle-1 font-weight-black text-grey-darken-4 mb-1">
          "{{ currentSentence.text }}"
        </div>
        <div class="d-flex flex-column align-center ga-1 mb-3">
          <span class="text-subtitle-2 text-teal-darken-3 font-weight-bold font-italic">
            /{{ currentSentence.ipa }}/
          </span>
          <span class="text-caption text-grey-darken-2 d-flex align-center ga-1">
            <v-icon color="primary" size="x-small">mdi-translate</v-icon>
            <span>{{ currentSentence.meaning }}</span>
          </span>
        </div>

        <!-- Audio Accent Setting -->
        <div class="d-flex align-center justify-center ga-2 mb-2">
          <v-chip-group v-model="ttsAccent" mandatory density="compact" color="teal">
            <v-chip value="en-US" size="x-small" label variant="tonal">US Accent</v-chip>
            <v-chip value="en-GB" size="x-small" label variant="tonal">UK Accent</v-chip>
          </v-chip-group>
        </div>

        <div class="d-flex align-center justify-center ga-2 flex-wrap">
          <v-btn
            color="teal"
            variant="tonal"
            size="small"
            class="text-none"
            prepend-icon="mdi-volume-high"
            @click="playSampleTTS"
          >
            Listen Sample
          </v-btn>
          <v-btn
            color="teal"
            variant="tonal"
            size="small"
            class="text-none"
            prepend-icon="mdi-auto-fix"
            :loading="isGeneratingAI"
            @click="generateAISentence"
          >
            Generate New AI Sentence
          </v-btn>
        </div>
      </div>

      <!-- Micro Studio Section -->
      <div class="text-center my-1 py-1">
        <div class="text-caption text-grey-darken-2 mb-1">
          {{ isRecording ? 'Recording in progress... Click button to stop:' : 'Click microphone button below to record:' }}
        </div>

        <div class="d-flex align-center justify-center position-relative mx-auto mb-1" style="width: 56px; height: 56px;">
          <v-progress-circular
            v-if="isRecording || isAnalyzing"
            indeterminate
            color="teal"
            size="56"
            width="3"
            class="position-absolute"
          />
          <v-btn
            :color="isRecording ? 'grey-darken-3' : 'teal-darken-1'"
            icon
            density="comfortable"
            style="width: 48px; height: 48px; z-index: 2;"
            :disabled="isAnalyzing"
            @click="isRecording ? stopRecording() : startRecording()"
          >
            <v-icon size="small">{{ isRecording ? 'mdi-stop' : 'mdi-microphone' }}</v-icon>
          </v-btn>
        </div>

        <div v-if="isRecording" class="text-caption text-teal-darken-2 mb-1 font-weight-bold">
          Recording... ({{ recordingDuration }}s)
        </div>

        <div v-if="isAnalyzing" class="text-caption text-teal-darken-3 animate-pulse py-1">
          AI is analyzing intonation & rhythm...
        </div>
      </div>

      <!-- Error Alert -->
      <v-card v-if="errorMessage" border flat rounded="lg" class="pa-3 my-2 bg-orange-lighten-5 text-center">
        <v-icon color="warning" size="small" class="mr-1">mdi-alert-circle-outline</v-icon>
        <span class="text-caption font-weight-bold text-warning-darken-3">{{ errorMessage }}</span>
      </v-card>

      <!-- Analysis Result -->
      <div v-if="result && !isAnalyzing" class="d-flex flex-column ga-3 mt-3">
        <!-- 1. TRANSCRIBED SPOKEN TEXT -->
        <div class="pa-3 bg-blue-lighten-5 rounded-lg border">
          <div class="text-body-2 font-weight-bold text-primary mb-2 d-flex align-center ga-1">
            <v-icon color="primary" size="small">mdi-message-text-outline</v-icon>
            <span>Transcribed Spoken Text:</span>
            <span class="font-weight-black text-primary-darken-2 ml-1">"{{ result.transcribed_text }}"</span>
          </div>

          <!-- AUDIO PLAYER PLAYBACK -->
          <div v-if="audioUrl" class="d-flex align-center ga-2 bg-white pa-2 rounded border mt-2">
            <v-btn
              :color="isPlaying ? 'warning' : 'primary'"
              density="compact"
              icon
              size="small"
              @click="togglePlayAudio"
            >
              <v-icon size="small">{{ isPlaying ? 'mdi-pause' : 'mdi-play' }}</v-icon>
            </v-btn>
            <div class="text-caption font-weight-bold text-grey-darken-2">
              {{ isPlaying ? 'Playing audio...' : 'Play back recorded voice' }}
            </div>
            <audio ref="audioPlayer" :src="audioUrl" @ended="isPlaying = false" class="d-none" />
          </div>
        </div>

        <!-- 2. OVERVIEW CARD -->
        <v-card border flat rounded="lg" class="pa-3" :class="result.score >= 6 ? 'bg-teal-lighten-5 border-teal' : 'bg-orange-lighten-5 border-orange'">
          <div class="d-flex align-center justify-space-between mb-1">
            <div class="d-flex align-center ga-2">
              <v-chip :color="result.score >= 6 ? 'teal' : 'orange-darken-3'" font-weight-bold size="small" variant="flat">
                <v-icon size="x-small" start>mdi-target</v-icon>
                Accuracy {{ result.reading_result ? result.reading_result.accuracy.toFixed(0) : 0 }}%
              </v-chip>
              <span class="text-subtitle-2 font-weight-black" :class="result.score >= 8 ? 'text-teal-darken-4' : result.score >= 6 ? 'text-teal-darken-3' : 'text-orange-darken-4'">
                {{ result.score >= 8 ? 'Outstanding!' : result.score >= 6 ? 'Great Job!' : 'Needs Practice!' }}
              </span>
            </div>
            <div class="text-h5 font-weight-black" :class="result.score >= 6 ? 'text-teal-darken-4' : 'text-orange-darken-4'">
              {{ result.score.toFixed(1) }}/10
            </div>
          </div>
          <div class="text-caption font-weight-bold" :class="result.score >= 6 ? 'text-teal-darken-4' : 'text-orange-darken-4'">
            <v-icon size="x-small" class="mr-1">mdi-information-outline</v-icon>
            {{ result.score < 5 ? 'Word alignment low. Speak louder and articulate each word clearly!' : (result.ai_analysis?.topic_comment || 'You completed Shadowing intonation practice successfully!') }}
          </div>
        </v-card>

        <!-- 3. WORD ALIGNMENT CARD -->
        <v-card v-if="result.reading_result" border flat rounded="lg" class="pa-3 bg-light-blue-lighten-5 border-blue">
          <div class="d-flex align-center justify-space-between mb-2">
            <div class="text-subtitle-2 font-weight-black text-primary d-flex align-center ga-1">
              <v-icon color="primary" size="small">mdi-bullseye-arrow</v-icon>
              Model Sentence Word Alignment
            </div>
            <v-chip color="primary" font-weight-bold size="small" variant="flat">
              {{ result.reading_result.spoken_words_count }}/{{ result.reading_result.target_words_count }} words
            </v-chip>
          </div>

          <div class="text-caption text-grey-darken-2 mb-2 font-weight-bold">
            Word details (Green = Correct, Yellow = Partial, Red = Missing/Incorrect):
          </div>

          <div class="d-flex flex-wrap ga-1 bg-white pa-2 rounded border">
            <v-chip
              v-for="(item, idx) in (result.reading_result.word_analysis || [])"
              :key="idx"
              size="small"
              :color="item.status === 'correct' ? 'success' : item.status === 'partial' ? 'warning' : 'error'"
              variant="flat"
              class="font-weight-bold"
            >
              <v-icon size="x-small" start>
                {{ item.status === 'correct' ? 'mdi-check' : item.status === 'partial' ? 'mdi-alert-circle' : 'mdi-close' }}
              </v-icon>
              <span :class="{'text-decoration-line-through': item.status === 'missing'}">
                {{ item.word }}
              </span>
            </v-chip>
          </div>
        </v-card>

        <!-- IPA PHONETIC EVALUATION -->
        <v-card v-if="result.ipa_analysis" border flat rounded="lg" class="pa-3 mb-3 bg-teal-lighten-5 border-teal">
          <div class="d-flex align-center justify-space-between mb-2">
            <div class="text-subtitle-2 font-weight-black text-teal-darken-4 d-flex align-center ga-1">
              <v-icon color="teal-darken-2" size="small">mdi-bookmark-music-outline</v-icon>
              <span>IPA Phonetic Evaluation (International Standard)</span>
            </div>
            <v-chip color="teal-darken-3" font-weight-bold size="small" variant="flat">
              IPA {{ result.ipa_analysis.ipa_accuracy }}%
            </v-chip>
          </div>

          <!-- Full IPA sentence comparison -->
          <div class="bg-white pa-2 rounded border mb-2 text-caption">
            <div class="d-flex align-center ga-2 mb-1">
              <span class="font-weight-black text-primary">Target IPA:</span>
              <span class="font-weight-bold text-teal-darken-4 font-mono">{{ result.ipa_analysis.target_full_ipa }}</span>
            </div>
            <div class="d-flex align-center ga-2">
              <span class="font-weight-black text-secondary">Spoken IPA:</span>
              <span class="font-weight-bold text-indigo-darken-3 font-mono">{{ result.ipa_analysis.spoken_full_ipa }}</span>
            </div>
          </div>

          <!-- Pitch Intonation Chart F0 -->
          <div v-if="result.ipa_analysis.pitch_analysis?.pitch_points?.length" class="bg-white pa-3 rounded border mb-3">
            <div class="d-flex align-center justify-space-between mb-2">
              <div class="text-caption font-weight-black text-indigo-darken-3 d-flex align-center ga-1">
                <v-icon color="indigo" size="x-small">mdi-chart-bell-curve-cumulative</v-icon>
                <span>Pitch Contour & Intonation Chart (F0)</span>
              </div>
              <v-chip size="x-small" color="indigo" variant="tonal" class="font-weight-black">
                Intonation Match {{ result.ipa_analysis.pitch_analysis.pitch_accuracy }}%
              </v-chip>
            </div>
            <div class="d-flex align-center justify-space-between text-caption text-grey mb-1" style="font-size: 10px;">
              <span><v-icon size="x-small" color="primary">mdi-minus</v-icon> Native Speaker</span>
              <span><v-icon size="x-small" color="amber-darken-3">mdi-minus</v-icon> Learner Voice</span>
            </div>
            <!-- SVG Pitch Chart -->
            <div class="w-100 bg-grey-lighten-4 rounded pa-2 d-flex align-end justify-space-between" style="height: 60px; position: relative;">
              <div
                v-for="(pt, p_idx) in result.ipa_analysis.pitch_analysis.pitch_points"
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
          <div v-if="result.ipa_analysis.linking_pairs?.length" class="bg-amber-lighten-5 pa-2.5 rounded border border-amber mb-3">
            <div class="text-caption font-weight-black text-amber-darken-4 mb-1 d-flex align-center ga-1">
              <v-icon color="amber-darken-4" size="x-small">mdi-link-variant</v-icon>
              <span>Connected Speech & Liaisons:</span>
            </div>
            <div class="d-flex flex-wrap ga-2 mt-1">
              <v-chip
                v-for="(pair, l_idx) in result.ipa_analysis.linking_pairs"
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
              v-for="(w_ipa, idx) in (result.ipa_analysis.words_ipa || [])"
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
              <div v-if="w_ipa.spoken_ipa && w_ipa.status !== 'correct'" class="text-caption font-weight-bold text-error mt-0.5" style="font-size: 9px;">
                Spoken: {{ w_ipa.spoken_ipa }}
              </div>
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

        <!-- 4. THẺ GỢI Ý CÂU BẢN XỨ CHUẨN 3 CẤP ĐỘ -->
        <v-card v-if="result.ai_analysis?.native_suggestions?.length" border flat rounded="lg" class="pa-3 bg-purple-lighten-5 border-purple">
          <div class="text-subtitle-2 font-weight-black text-purple-darken-3 mb-2 d-flex align-center ga-1">
            <v-icon color="purple" size="small">mdi-star-face</v-icon>
            Native Expressions (3 Levels)
          </div>

          <div class="d-flex flex-column ga-2">
            <div
              v-for="(sug, idx) in result.ai_analysis.native_suggestions"
              :key="idx"
              class="pa-2 bg-white rounded border d-flex align-center justify-space-between flex-wrap ga-2"
            >
              <div class="flex-grow-1 pr-2">
                <v-chip
                  size="x-small"
                  :color="idx === 0 ? 'success' : idx === 1 ? 'info' : 'secondary'"
                  variant="flat"
                  class="font-weight-black mb-1"
                  style="font-size: 10px; height: 18px;"
                >
                  {{ sug.style }}
                </v-chip>
                <div class="text-subtitle-2 font-weight-black text-purple-darken-4">
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
        </v-card>

        <!-- 5. GRAMMAR & VOCABULARY VISUAL FIXES -->
        <v-card border flat rounded="lg" class="pa-3" :class="validGrammarFixes.length ? 'bg-orange-lighten-5 border-orange' : 'bg-green-lighten-5 border-green'">
          <div class="text-subtitle-2 font-weight-black mb-2 d-flex align-center ga-1" :class="validGrammarFixes.length ? 'text-orange-darken-4' : 'text-success'">
            <v-icon :color="validGrammarFixes.length ? 'orange-darken-3' : 'success'" size="small">
              {{ validGrammarFixes.length ? 'mdi-auto-fix' : 'mdi-check-decagram-outline' }}
            </v-icon>
            Grammar & Vocabulary Visual Fixes
          </div>

          <template v-if="validGrammarFixes.length > 0">
            <div v-for="(fix, idx) in validGrammarFixes" :key="idx" class="mb-2 pa-3 bg-white rounded-lg border">
              <div class="d-flex align-center ga-2 mb-2">
                <v-chip v-if="fix.type" color="orange-darken-3" size="x-small" variant="flat" class="font-weight-black" style="font-size: 10.5px; height: 20px;">
                  <v-icon size="x-small" start>mdi-tag-outline</v-icon>
                  {{ fix.type }}
                </v-chip>
              </div>

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

        <!-- 6. DETAILED SKILL SCORES TABLE -->
        <v-card v-if="result.ai_analysis?.scores" border flat rounded="lg" class="pa-3 bg-grey-lighten-5">
          <div class="text-caption font-weight-bold text-grey-darken-1 mb-2 d-flex align-center ga-1">
            <v-icon size="x-small" color="grey-darken-2">mdi-chart-box-outline</v-icon>
            <span>Detailed Skill Scores:</span>
          </div>
          <v-row density="compact">
            <v-col cols="4" sm="2" class="text-center">
              <div class="text-caption text-grey font-weight-bold">Pronunciation</div>
              <div class="text-subtitle-2 font-weight-black text-primary">{{ result.ai_analysis.scores.pronunciation }}/2</div>
            </v-col>
            <v-col cols="4" sm="2" class="text-center">
              <div class="text-caption text-grey font-weight-bold">Fluency</div>
              <div class="text-subtitle-2 font-weight-black text-primary">{{ result.ai_analysis.scores.fluency }}/2</div>
            </v-col>
            <v-col cols="4" sm="2" class="text-center">
              <div class="text-caption text-grey font-weight-bold">Grammar</div>
              <div class="text-subtitle-2 font-weight-black text-primary">{{ result.ai_analysis.scores.grammar }}/2</div>
            </v-col>
            <v-col cols="4" sm="2" class="text-center">
              <div class="text-caption text-grey font-weight-bold">Vocabulary</div>
              <div class="text-subtitle-2 font-weight-black text-primary">{{ result.ai_analysis.scores.vocabulary }}/2</div>
            </v-col>
            <v-col cols="4" sm="2" class="text-center">
              <div class="text-caption text-grey font-weight-bold">Communication</div>
              <div class="text-subtitle-2 font-weight-black text-primary">{{ result.ai_analysis.scores.communication }}/2</div>
            </v-col>
            <v-col cols="4" sm="2" class="text-center">
              <div class="text-caption text-grey font-weight-bold">Clarity Rate</div>
              <div class="text-subtitle-2 font-weight-black text-teal-darken-2">{{ result.ai_analysis.scores.clarity_percent }}%</div>
            </v-col>
          </v-row>
        </v-card>
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
              <div class="text-caption font-weight-bold text-primary font-mono">Phonetics: {{ selectedArticulation.ipa }}</div>
            </div>
          </div>
          <v-btn icon="mdi-close" variant="text" density="compact" @click="showArticulationModal = false" />
        </div>

        <!-- Sơ Đồ Khẩu Hình Đồ Họa 2D/3D -->
        <div class="bg-teal-lighten-5 border border-teal pa-4 rounded-lg mb-3 text-center">
          <div class="d-flex justify-center align-center ga-4 mb-2">
            <div class="border pa-2 bg-white rounded-circle elevation-1" style="width: 70px; height: 70px;">
              <v-icon size="40" color="teal-darken-3">mdi-emoticon-outline</v-icon>
            </div>
            <v-icon size="large" color="teal-darken-2">mdi-arrow-right-bold-outline</v-icon>
            <div class="border pa-2 bg-white rounded-circle elevation-1" style="width: 70px; height: 70px;">
              <v-icon size="40" color="deep-orange">mdi-account-voice</v-icon>
            </div>
          </div>
          <div class="text-caption font-weight-black text-teal-darken-4">3-Step Articulation Flow: Lips & Teeth ➔ Airflow ➔ Sound Release</div>
        </div>

        <div class="space-y-2 text-caption">
          <div class="bg-grey-lighten-4 pa-2.5 rounded border mb-2">
            <span class="font-weight-black text-grey-darken-4 d-block mb-1 d-flex align-center ga-1">
              <v-icon color="pink" size="x-small">mdi-lips</v-icon>
              <span>1. Lips & Teeth Position:</span>
            </span>
            <span class="text-grey-darken-3">{{ selectedArticulation.mouth_position }}</span>
          </div>

          <div class="bg-grey-lighten-4 pa-2.5 rounded border mb-2">
            <span class="font-weight-black text-grey-darken-4 d-block mb-1 d-flex align-center ga-1">
              <v-icon color="deep-orange" size="x-small">mdi-emoticon-tongue-outline</v-icon>
              <span>2. Tongue Placement:</span>
            </span>
            <span class="text-grey-darken-3">{{ selectedArticulation.tongue_position }}</span>
          </div>

          <div class="bg-grey-lighten-4 pa-2.5 rounded border mb-2">
            <span class="font-weight-black text-grey-darken-4 d-block mb-1 d-flex align-center ga-1">
              <v-icon color="light-blue" size="x-small">mdi-weather-windy</v-icon>
              <span>3. Airflow & Vocal Cords:</span>
            </span>
            <span class="text-grey-darken-3">{{ selectedArticulation.airflow }}</span>
          </div>

          <div class="bg-amber-lighten-5 pa-2.5 rounded border border-amber">
            <span class="font-weight-black text-amber-darken-4 d-block mb-1 d-flex align-center ga-1">
              <v-icon color="amber-darken-3" size="x-small">mdi-lightbulb-on-outline</v-icon>
              <span>Quick Practice Tip:</span>
            </span>
            <span class="text-amber-darken-4 font-weight-bold">{{ selectedArticulation.tip }}</span>
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
      </div>
    </div>
  </v-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  backendUrl: String,
  userId: Number
})

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

const selectedLevel = ref('easy')
const isRecording = ref(false)
const isAnalyzing = ref(false)
const recordingDuration = ref(0)
const audioBlob = ref(null)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const timer = ref(null)
const result = ref(null)
const errorMessage = ref(null)
const audioUrl = ref(null)
const audioPlayer = ref(null)
const isPlaying = ref(false)

const validGrammarFixes = computed(() => {
  if (!result.value?.ai_analysis?.grammar_fixes) return []
  return result.value.ai_analysis.grammar_fixes.filter(f => 
    f && f.original && f.fixed && String(f.original).trim() !== '' && String(f.fixed).trim() !== ''
  )
})

const togglePlayAudio = () => {
  if (!audioPlayer.value) return
  if (isPlaying.value) {
    audioPlayer.value.pause()
    isPlaying.value = false
  } else {
    audioPlayer.value.play()
    isPlaying.value = true
  }
}

const sampleSentences = {
  easy: [
    { text: "Practice makes perfect!", ipa: "ˈpræktɪs meɪks ˈpɜːfɪkt", meaning: "Consistent practice builds mastery" },
    { text: "How are you doing today?", ipa: "haʊ ɑː juː ˈduːɪŋ təˈdeɪ", meaning: "Asking about someone's current well-being" },
    { text: "Have a nice day!", ipa: "hæv ə naɪs deɪ", meaning: "Wishing someone a pleasant day ahead" },
    { text: "Nice to meet you!", ipa: "naɪs tuː miːt juː", meaning: "Polite greeting upon meeting someone new" },
    { text: "Where are you from?", ipa: "weər ɑː juː frɒm", meaning: "Inquiring about someone's origin or hometown" }
  ],
  medium: [
    { text: "Never put off until tomorrow what you can do today.", ipa: "ˈnɛvər pʊt ɒf ənˈtɪl təˈmɒrəʊ wɒt juː kæn duː təˈdeɪ", meaning: "Avoid procrastination and act promptly" },
    { text: "I really appreciate your help with this project.", ipa: "aɪ ˈrɪəli əˈpriːʃieɪt jɔː hɛlp wɪð ðɪs ˈprɒʤɛkt", meaning: "Expressing genuine gratitude for assistance" },
    { text: "Learning a new language opens up a world of opportunities.", ipa: "ˈlɜːnɪŋ ə njuː ˈlæŋɡwɪʤ ˈəʊpənz ʌp ə wɜːld ɒv ˌɒpəˈtjuːnɪtiz", meaning: "Language acquisition expands life horizons" },
    { text: "Could you please speak a little slower?", ipa: "kʊd juː pliːz spiːk ə ˈlɪtl ˈsləʊər", meaning: "Requesting a slower speaking pace" }
  ],
  hard: [
    { text: "Success is not final, failure is not fatal: it is the courage to continue that counts.", ipa: "səkˈsɛs ɪz nɒt ˈfaɪnl ˈfeɪljər ɪz nɒt ˈfeɪtl", meaning: "Perseverance defines true achievement" },
    { text: "The future belongs to those who believe in the beauty of their dreams.", ipa: "ðə ˈfjuːtʃər bɪˈlɒŋz tuː ðəʊz huː bɪˈliːv ɪn ðə ˈbjuːti ɒv ðeər driːmz", meaning: "Belief in dreams shapes future success" },
    { text: "In the middle of every difficulty lies opportunity.", ipa: "ɪn ðə ˈmɪdl ɒv ˈɛvri ˈdɪfɪkəlti laɪz ˌɒpəˈtjuːnɪti", meaning: "Challenges contain hidden possibilities" }
  ]
}

const aiSentencePool = {
  easy: [
    { text: "Keep up the great work!", ipa: "kiːp ʌp ðə ɡreɪt wɜːk", meaning: "Encouraging continued effort" },
    { text: "Where is the nearest coffee shop?", ipa: "weər ɪz ðə ˈnɪərɪst ˈkɒfi ʃɒp", meaning: "Asking for directions to local coffee shop" },
    { text: "What time does the train leave?", ipa: "wɒt taɪm dʌz ðə treɪn liːv", meaning: "Inquiring about train departure schedule" },
    { text: "I really love learning English!", ipa: "aɪ ˈrɪəli lʌv ˈlɜːnɪŋ ˈɪŋɡlɪʃ", meaning: "Expressing passion for English learning" },
    { text: "Thank you for your warm welcome!", ipa: "θæŋk juː fɔː jɔː wɔːm ˈwɛlkəm", meaning: "Expressing thanks for hospitable greeting" }
  ],
  medium: [
    { text: "Practice makes progress, not perfection.", ipa: "ˈpræktɪs meɪks ˈprəʊɡrɛs nɒt pəˈfɛkʃən", meaning: "Focus on continuous growth rather than perfection" },
    { text: "Could you please give me a hand with this bag?", ipa: "kʊd juː pliːz ɡɪv miː ə hænd wɪð ðɪs bæɡ", meaning: "Asking for help carrying luggage" },
    { text: "I will call you back as soon as I finish my work.", ipa: "aɪ wɪl kɔːl juː bæk æz suːn æz aɪ ˈfɪnɪʃ maɪ wɜːk", meaning: "Promising a return phone call after work" }
  ],
  hard: [
    { text: "The secret of getting ahead is getting started.", ipa: "ðə ˈsiːkrɪt ɒv ˈɡɛtɪŋ əˈhɛd ɪz ˈɡɛtɪŋ ˈstɑːtɪd", meaning: "Initiating action is the key to progress" },
    { text: "Great things are done by a series of small things brought together.", ipa: "ɡreɪt θɪŋz ɑː dʌn baɪ ə ˈsɪəriːz ɒv smɔːl θɪŋz brɔːt təˈɡɛðər", meaning: "Cumulative small efforts achieve greatness" }
  ]
}

const isGeneratingAI = ref(false)
const dynamicSentence = ref(null)
const currentIndex = ref(0)

const currentSentence = computed(() => {
  if (dynamicSentence.value) return dynamicSentence.value
  const list = sampleSentences[selectedLevel.value] || sampleSentences.easy
  return list[currentIndex.value % list.length]
})

const sessionSentenceHistory = ref(new Set())

const generateAISentence = async () => {
  isGeneratingAI.value = true
  result.value = null
  errorMessage.value = null
  audioBlob.value = null
  
  const currentText = currentSentence.value?.text || ''
  if (currentText) {
    sessionSentenceHistory.value.add(currentText.trim().toLowerCase())
  }
  
  const historyArray = Array.from(sessionSentenceHistory.value)
  
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const url = `${props.backendUrl}/api/generate-sentence?level=${selectedLevel.value}&exclude=${encodeURIComponent(currentText)}&exclude_history=${encodeURIComponent(JSON.stringify(historyArray))}`
      const res = await fetch(url)
      if (res.ok) {
        const data = await res.json()
        if (data && data.text) {
          const newTextLower = data.text.trim().toLowerCase()
          if (!sessionSentenceHistory.value.has(newTextLower)) {
            sessionSentenceHistory.value.add(newTextLower)
            dynamicSentence.value = data
            isGeneratingAI.value = false
            return
          }
        }
      }
    } catch (err) {
      console.warn('Groq AI sentence fetch failed, falling back to local pool:', err)
    }
  }

  // Fallback to pool with de-duplication loop
  const pool = aiSentencePool[selectedLevel.value] || aiSentencePool.easy
  let randomPick = pool[Math.floor(Math.random() * pool.length)]
  let attempts = 0
  while (sessionSentenceHistory.value.has(randomPick.text.trim().toLowerCase()) && pool.length > 1 && attempts < 10) {
    randomPick = pool[Math.floor(Math.random() * pool.length)]
    attempts++
  }
  sessionSentenceHistory.value.add(randomPick.text.trim().toLowerCase())
  dynamicSentence.value = randomPick
  isGeneratingAI.value = false
}

const nextSentence = () => {
  dynamicSentence.value = null
  result.value = null
  errorMessage.value = null
  audioBlob.value = null
  const list = sampleSentences[selectedLevel.value]
  currentIndex.value = (currentIndex.value + 1) % list.length
}

watch(selectedLevel, () => {
  dynamicSentence.value = null
  currentIndex.value = 0
  result.value = null
  errorMessage.value = null
  audioBlob.value = null
})

const ttsAccent = ref('en-US')

const playSampleTTS = () => {
  speakText(currentSentence.value.text)
}

const speakText = (text) => {
  if ('speechSynthesis' in window && text) {
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = ttsAccent.value || 'en-US'
    utterance.rate = 0.9
    window.speechSynthesis.speak(utterance)
  }
}

const startRecording = async () => {
  result.value = null
  errorMessage.value = null
  audioChunks.value = []
  audioUrl.value = null
  isPlaying.value = false
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)
    mediaRecorder.value.ondataavailable = (e) => audioChunks.value.push(e.data)
    mediaRecorder.value.onstop = () => {
      audioBlob.value = new Blob(audioChunks.value, { type: 'audio/webm' })
      audioUrl.value = URL.createObjectURL(audioBlob.value)
      analyzeShadowing()
    }
    mediaRecorder.value.start()
    isRecording.value = true
    recordingDuration.value = 0
    timer.value = setInterval(() => recordingDuration.value++, 1000)
  } catch (err) {
    errorMessage.value = 'Microphone access denied! Please allow microphone permissions in browser.'
  }
}

const stopRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    isRecording.value = false
    clearInterval(timer.value)
  }
}

const analyzeShadowing = async () => {
  if (!audioBlob.value) return
  isAnalyzing.value = true
  errorMessage.value = null
  try {
    const formData = new FormData()
    formData.append('audio', audioBlob.value, 'shadowing.webm')
    formData.append('topic', currentSentence.value.text)
    formData.append('target_text', currentSentence.value.text)
    formData.append('mode', 'reading')
    if (props.userId) {
      formData.append('user_id', props.userId)
    }

    const res = await fetch(`${props.backendUrl}/api/analyze`, {
      method: 'POST',
      body: formData
    })

    if (!res.ok) {
      const errData = await res.json()
      throw new Error(errData.detail || 'Unable to analyze speech audio. Please speak louder and clearly!')
    }

    const data = await res.json()
    if (data.success) {
      result.value = data
    }
  } catch (err) {
    errorMessage.value = err.message || 'Không thể nhận diện giọng nói. Em hãy phát âm to và rõ ràng hơn nhé!'
    console.error('Shadowing error:', err)
  } finally {
    isAnalyzing.value = false
  }
}
</script>

<style scoped>
.max-width-700 {
  max-width: 700px;
  margin: 0 auto;
}
</style>
