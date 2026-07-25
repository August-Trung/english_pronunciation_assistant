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
      title="Yêu cầu bảo mật HTTPS"
      text="Trình duyệt yêu cầu kết nối bảo mật HTTPS để kích hoạt Microphone. Nếu bạn chạy trên tên miền chính thức, vui lòng cấu hình SSL."
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
                Bước 1: {{ practiceMode === 'reading' ? 'Chọn câu mẫu luyện đọc' : 'Chọn chủ đề luyện nói' }}
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
                Nói tự do
              </v-btn>
              <v-btn value="reading" size="small" class="text-none font-weight-bold flex-grow-1 flex-sm-grow-0" prepend-icon="mdi-book-open-variant">
                Đọc theo mẫu
              </v-btn>
            </v-btn-toggle>
          </div>

          <!-- Topic input with TTS button -->
          <v-text-field
            v-model="topic"
            :placeholder="practiceMode === 'reading' ? 'Chọn hoặc nhập câu mẫu để luyện đọc...' : 'Nhập chủ đề hoặc câu hỏi (Ví dụ: What is your favorite color?)'"
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
                  title="Cài đặt giọng đọc (Anh-Mỹ/Anh-Anh, Nam/Nữ)"
                />
                <v-menu activator="parent" location="bottom end" :close-on-content-click="false">
                  <v-card class="pa-4 text-body-2" width="320" border elevation="4" rounded="lg">
                    <div class="text-subtitle-1 font-weight-black text-secondary mb-3 d-flex align-center justify-space-between border-bottom pb-2">
                      <span>Cài đặt giọng đọc (TTS)</span>
                      <v-icon color="primary">mdi-account-voice</v-icon>
                    </div>
                    
                    <div class="font-weight-bold text-grey-darken-3 mb-2 text-subtitle-2">1. Giọng phát âm (Accent):</div>
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
                        Anh - Mỹ (US)
                      </v-btn>
                      <v-btn value="en-GB" size="small" class="text-none font-weight-bold flex-grow-1" prepend-icon="mdi-earth">
                        Anh - Anh (UK)
                      </v-btn>
                    </v-btn-toggle>

                    <div class="font-weight-bold text-grey-darken-3 mb-2 text-subtitle-2">2. Giới tính giọng đọc:</div>
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
                        Giọng Nữ
                      </v-btn>
                      <v-btn value="male" size="small" class="text-none font-weight-bold flex-grow-1" prepend-icon="mdi-gender-male">
                        Giọng Nam
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
                      Nghe thử giọng chọn
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
                :title="isSpeaking ? 'Đang đọc mẫu...' : 'Nghe mẫu phát âm (TTS)'"
                class="mr-1"
                @click="speakText(topic)"
              />
              <v-btn
                color="secondary"
                variant="text"
                density="compact"
                icon="mdi-dice-5-outline"
                :title="practiceMode === 'reading' ? 'Chọn câu mẫu ngẫu nhiên' : 'Chọn chủ đề ngẫu nhiên'"
                @click="getRandomTopic"
              />
            </template>
          </v-text-field>

          <!-- Dynamic Preset Library Section -->
          <div class="mb-3">
            <div class="text-caption font-weight-bold text-grey-darken-1 mb-1 d-flex align-center justify-space-between ga-2 flex-nowrap">
              <span class="d-flex align-center text-truncate">
                <v-icon color="primary" size="small" class="mr-1 flex-shrink-0">mdi-school-outline</v-icon>
                <span class="text-truncate">{{ practiceMode === 'reading' ? 'Thư viện câu mẫu:' : 'Gợi ý chủ đề:' }}</span>
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
                      title="Nghe phát âm mẫu"
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
              Bước 2: {{ practiceMode === 'reading' ? 'Đọc lại câu mẫu bằng giọng nói' : 'Trả lời bằng giọng nói' }}
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
                  title="Xóa bản ghi hiện tại"
                  :disabled="isAnalyzing"
                  @click="clearAudio"
                />
              </v-col>
            </v-row>

            <div class="text-center mb-2">
              <template v-if="isRecording">
                <div class="d-flex align-center justify-center text-error font-weight-black text-caption animate-pulse">
                  <v-icon color="error" class="mr-1 animate-pulse" size="x-small">mdi-record-rec</v-icon>
                  Đang ghi âm... ({{ formatTime(recordingDuration) }})
                </div>
              </template>
              <template v-else-if="!topic.trim()">
                <span class="text-caption font-weight-bold text-grey-darken-1" style="font-size: 11px;">
                  Hãy chọn hoặc nhập một câu chủ đề trước
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
                title="Phát / Tạm dừng"
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
              Chấm điểm phát âm
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
            <div class="text-subtitle-1 font-weight-black text-secondary">Kết quả đánh giá</div>
          </div>

          <!-- Error Alert Card -->
          <v-card v-if="errorMessage" border flat rounded="lg" class="pa-4 mb-3 bg-orange-lighten-5 text-center">
            <v-icon color="warning" size="36" class="mb-2">mdi-alert-circle-outline</v-icon>
            <div class="text-subtitle-2 font-weight-black text-warning-darken-3 mb-1">Không thể chấm điểm</div>
            <div class="text-caption text-grey-darken-2 mb-3">{{ errorMessage }}</div>
            <v-btn
              color="warning"
              variant="outlined"
              size="small"
              class="font-weight-bold text-none"
              prepend-icon="mdi-refresh"
              @click="errorMessage = null"
            >
              Thử lại
            </v-btn>
          </v-card>

          <!-- Empty state -->
          <div v-else-if="!results && !isAnalyzing" class="d-flex flex-column align-center justify-center flex-grow-1 text-grey-darken-1 py-8">
            <v-icon size="48" color="grey-lighten-2" class="mb-2">mdi-comment-text-voice-outline</v-icon>
            <div class="text-subtitle-2 font-weight-bold text-grey">Chưa có kết quả phân tích</div>
            <div class="text-caption text-center px-6">Hãy hoàn thành câu trả lời của em ở cột bên trái và nhấn nút để bắt đầu chấm điểm nhé!</div>
          </div>

          <!-- Loading state -->
          <div v-if="isAnalyzing" class="d-flex flex-column align-center justify-center flex-grow-1 py-8">
            <v-progress-circular indeterminate color="primary" size="48" width="4" class="mb-3" />
            <div class="text-subtitle-2 font-weight-black text-primary">{{ loadingText }}</div>
          </div>

          <!-- Score details -->
          <div v-if="results && !isAnalyzing" class="flex-grow-1">
            <!-- 1. CÂU EM ĐÃ PHÁT ÂM (Hiển thị đầu tiên) -->
            <div class="mb-3">
              <div class="text-caption font-weight-bold text-grey-darken-2 mb-1 d-flex align-center">
                <v-icon size="small" color="primary" class="mr-1">mdi-message-text-outline</v-icon>
                Câu em đã phát âm:
              </div>
              <div class="pa-3 bg-blue-lighten-5 rounded-lg text-body-2 font-weight-bold text-primary border">
                "{{ results.transcribed_text }}"
              </div>
            </div>

            <!-- 2. THẺ TỔNG QUAN & ĐỘ KHỚP CHỦ ĐỀ -->
            <v-card border flat rounded="lg" class="pa-3 mb-3 bg-teal-lighten-5 border-teal">
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="d-flex align-center ga-2">
                  <v-chip color="teal" font-weight-bold size="small" variant="flat">
                    🎯 {{ practiceMode === 'reading' ? 'Độ Chính Xác' : 'Khớp Chủ Đề' }} {{ results.reading_result ? results.reading_result.accuracy.toFixed(0) : (results.ai_analysis?.topic_relevance_score || 92) }}%
                  </v-chip>
                  <span class="text-subtitle-2 font-weight-black text-teal-darken-4">
                    {{ results.score >= 8 ? 'Xuất Sắc!' : results.score >= 6 ? 'Rất Tốt!' : 'Cố Lên Em!' }}
                  </span>
                </div>
                <div :class="getScoreColorClass(results.score)" class="text-h5 font-weight-black">
                  {{ results.score.toFixed(1).replace('.', ',') }}/10
                </div>
              </div>
              <div class="text-caption text-teal-darken-4 font-weight-bold">
                {{ results.ai_analysis?.topic_comment || (practiceMode === 'reading' ? 'Em đã hoàn thành đọc nhại câu mẫu rất tốt!' : 'Em đã trả lời bám sát chủ đề được giao!') }}
              </div>
            </v-card>

            <!-- 2.1 THẺ ĐỐI CHIẾU TỪNG TỪ BÀI ĐỌC (Dành riêng cho Đọc theo mẫu) -->
            <v-card v-if="results.reading_result" border flat rounded="lg" class="pa-3 mb-3 bg-light-blue-lighten-5 border-blue">
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="text-subtitle-2 font-weight-black text-primary d-flex align-center ga-1">
                  <v-icon color="primary" size="small">mdi-bullseye-arrow</v-icon>
                  Đối Chiếu Từng Từ Bài Đọc Mẫu
                </div>
                <v-chip color="primary" font-weight-bold size="small" variant="flat">
                  {{ results.reading_result.spoken_words_count }}/{{ results.reading_result.target_words_count }} từ
                </v-chip>
              </div>

              <div class="text-caption text-grey-darken-2 mb-2 font-weight-bold">
                Chi tiết từng từ (Xanh = Đọc chuẩn, Vàng = Đọc ngắt/sai nhẹ, Đỏ = Đọc thiếu/sai):
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

            <!-- 3. THẺ GỢI Ý CÂU BẢN XỨ CHUẨN (NATIVE EXPRESSIONS 3 CẤP ĐỘ) -->
            <v-card v-if="results.ai_analysis?.native_suggestion || results.ai_analysis?.native_suggestions" border flat rounded="lg" class="pa-3 mb-3 bg-purple-lighten-5 border-purple">
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="text-subtitle-2 font-weight-black text-purple-darken-3 d-flex align-center ga-1">
                  <v-icon color="purple" size="small">mdi-star-face</v-icon>
                  Gợi Ý Câu Bản Xứ Chuẩn (Native Expressions)
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
                    <div class="text-caption text-grey-darken-2 font-weight-bold" style="font-size: 11px;">
                      💡 {{ sug.meaning }}
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
                    Nghe mẫu
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
                </v-btn>
              </div>
            </v-card>

            <!-- THẺ CHẤM & ĐỐI CHIẾU PHIÊN ÂM IPA CHUẨN QUỐC TẾ -->
            <v-card v-if="results.ipa_analysis" border flat rounded="lg" class="pa-3 mb-3 bg-teal-lighten-5 border-teal">
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="text-subtitle-2 font-weight-black text-teal-darken-4 d-flex align-center ga-1">
                  <v-icon color="teal-darken-3" size="small">mdi-phonetics</v-icon>
                  <span>Phân Tích & Chấm Âm Tiết IPA (Chuẩn Quốc Tế)</span>
                </div>
                <v-chip color="teal-darken-3" font-weight-bold size="small" variant="flat">
                  IPA {{ results.ipa_analysis.ipa_accuracy }}%
                </v-chip>
              </div>

              <!-- Full IPA sentence comparison -->
              <div class="bg-white pa-2 rounded border mb-2 text-caption">
                <div class="d-flex align-center ga-2 mb-1">
                  <span class="font-weight-black text-primary">IPA Câu Mẫu:</span>
                  <span class="font-weight-bold text-teal-darken-4 font-mono">{{ results.ipa_analysis.target_full_ipa }}</span>
                </div>
                <div class="d-flex align-center ga-2">
                  <span class="font-weight-black text-secondary">IPA Em Đọc:</span>
                  <span class="font-weight-bold text-indigo-darken-3 font-mono">{{ results.ipa_analysis.spoken_full_ipa }}</span>
                </div>
              </div>

              <!-- Word by word IPA breakdown chips -->
              <div class="d-flex flex-wrap ga-2">
                <div
                  v-for="(w_ipa, idx) in (results.ipa_analysis.words_ipa || [])"
                  :key="idx"
                  class="pa-2 bg-white rounded border d-flex flex-column align-center"
                  style="min-width: 85px;"
                >
                  <div class="text-caption font-weight-black text-grey-darken-3">
                    {{ w_ipa.word }}
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
                    Đọc: {{ w_ipa.spoken_ipa }}
                  </div>
                  <div v-if="w_ipa.note" class="text-caption text-error font-weight-bold text-center mt-0.5" style="font-size: 9px; line-height: 1.1;">
                    ⚠️ {{ w_ipa.note }}
                  </div>
                </div>
              </div>
            </v-card>

            <!-- 4. THẺ SỬA LỖI NGỮ PHÁP & TỪ VỰNG TRỰC QUAN -->
            <v-card border flat rounded="lg" class="pa-3 mb-3" :class="validGrammarFixes.length ? 'bg-orange-lighten-5 border-orange' : 'bg-green-lighten-5 border-green'">
              <div class="text-subtitle-2 font-weight-black mb-2 d-flex align-center ga-1" :class="validGrammarFixes.length ? 'text-orange-darken-4' : 'text-success'">
                <v-icon :color="validGrammarFixes.length ? 'orange-darken-3' : 'success'" size="small">
                  {{ validGrammarFixes.length ? 'mdi-auto-fix' : 'mdi-check-decagram-outline' }}
                </v-icon>
                Sửa Lỗi Ngữ Pháp & Từ Vựng Trực Quan
              </div>
              <template v-if="validGrammarFixes.length > 0">
                <div v-for="(fix, idx) in validGrammarFixes" :key="idx" class="mb-2 pa-3 bg-white rounded-lg border">
                  <!-- Type Badge -->
                  <div class="d-flex align-center ga-2 mb-2">
                    <v-chip v-if="fix.type" color="orange-darken-3" size="x-small" variant="flat" class="font-weight-black" style="font-size: 10.5px; height: 20px;">
                      🏷️ {{ fix.type }}
                    </v-chip>
                  </div>

                  <!-- Text rows for original vs fixed English sentences -->
                  <div class="d-flex flex-column ga-2 mb-2 pl-1">
                    <div class="d-flex align-center ga-2 text-body-2 font-weight-bold text-error flex-wrap">
                      <v-chip color="error" size="x-small" variant="tonal" class="font-weight-black flex-shrink-0" style="font-size: 10px; height: 20px;">
                        ❌ Chưa chuẩn
                      </v-chip>
                      <span class="text-body-2 font-weight-bold text-error">"{{ fix.original }}"</span>
                    </div>

                    <div class="d-flex align-center ga-2 text-body-2 font-weight-bold text-success flex-wrap">
                      <v-chip color="success" size="x-small" variant="flat" class="font-weight-black flex-shrink-0" style="font-size: 10px; height: 20px;">
                        ✅ Sửa lại
                      </v-chip>
                      <span class="text-body-2 font-weight-black text-success text-decoration-underline">"{{ fix.fixed }}"</span>
                    </div>
                  </div>

                  <!-- Reason explanation in Vietnamese -->
                  <div v-if="fix.reason" class="text-caption text-grey-darken-3 pl-1 pt-2 border-t mt-2" style="line-height: 1.5;">
                    💡 <strong>Giải thích:</strong> {{ fix.reason }}
                  </div>
                </div>
              </template>
              <template v-else>
                <div class="d-flex align-center ga-2 text-caption text-success font-weight-bold bg-white pa-2 rounded border">
                  <v-icon color="success" size="small">mdi-check-circle-outline</v-icon>
                  <span>Cấu trúc câu ngữ pháp và từ vựng chuẩn xác, không có lỗi sai!</span>
                </div>
              </template>
            </v-card>

            <!-- 5. BẢNG ĐIỂM CHI TIẾT 6 KỸ NĂNG -->
            <div class="mb-3">
              <div class="text-caption font-weight-bold text-grey-darken-1 mb-2">
                <v-icon size="small" color="primary" class="mr-1">mdi-chart-bar</v-icon>
                Điểm chi tiết từng kỹ năng:
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
                    {{ (results.ai_analysis?.scores?.[item.key.toLowerCase()] || results.breakdown[item.key]).toFixed(1).replace('.', ',') }}/2
                  </div>
                </v-col>
                <v-col cols="4" sm="2" class="pa-1 d-flex flex-column justify-center align-center">
                  <div class="text-caption text-grey-darken-2 font-weight-bold d-flex align-center justify-center">
                    <span>Độ rõ tiếng</span>
                    <span class="d-inline-flex align-center cursor-pointer ml-1">
                      <v-icon size="x-small" color="grey-darken-1" style="font-size: 14px;">
                        mdi-help-circle-outline
                      </v-icon>
                      <v-menu activator="parent" location="top center" transition="scale-transition">
                        <v-card class="pa-2 text-caption text-left text-grey-darken-3" max-width="240" border elevation="2" rounded="md">
                          Đo độ to rõ của giọng nói và mức độ sạch nhiễu môi trường của micro (giúp AI nhận diện chính xác 100%).
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
                Nhận xét chi tiết:
              </div>
              <v-card border flat rounded="lg" class="pa-3 bg-grey-lighten-4">
                <template v-if="results.ai_analysis?.pedagogical_feedback">
                  <div class="d-flex align-start ga-2 mb-2">
                    <v-icon size="small" color="blue" class="mt-1">mdi-waveform</v-icon>
                    <div>
                      <strong class="text-subtitle-2 text-blue-darken-3">Trôi chảy & Diễn đạt:</strong>
                      <div class="text-caption text-grey-darken-3">{{ results.ai_analysis.pedagogical_feedback.fluency }}</div>
                    </div>
                  </div>
                  
                  <div class="d-flex align-start ga-2 mb-2">
                    <v-icon size="small" color="purple" class="mt-1">mdi-book-alphabet</v-icon>
                    <div>
                      <strong class="text-subtitle-2 text-purple-darken-3">Từ vựng:</strong>
                      <div class="text-caption text-grey-darken-3">{{ results.ai_analysis.pedagogical_feedback.vocabulary }}</div>
                    </div>
                  </div>
                  
                  <div class="d-flex align-start ga-2 mb-2">
                    <v-icon size="small" color="orange" class="mt-1">mdi-lead-pencil</v-icon>
                    <div>
                      <strong class="text-subtitle-2 text-orange-darken-4">Ngữ pháp:</strong>
                      <div class="text-caption text-grey-darken-3">{{ results.ai_analysis.pedagogical_feedback.grammar }}</div>
                    </div>
                  </div>
                  
                  <div class="d-flex align-start ga-2 mb-2">
                    <v-icon size="small" color="teal" class="mt-1">mdi-microphone-outline</v-icon>
                    <div>
                      <strong class="text-subtitle-2 text-teal-darken-4">Phát âm:</strong>
                      <div class="text-caption text-grey-darken-3">{{ results.ai_analysis.pedagogical_feedback.pronunciation }}</div>
                    </div>
                  </div>
                  
                  <div class="d-flex align-start ga-2 mb-2">
                    <v-icon size="small" color="indigo" class="mt-1">mdi-forum-outline</v-icon>
                    <div>
                      <strong class="text-subtitle-2 text-indigo-darken-3">Giao tiếp:</strong>
                      <div class="text-caption text-grey-darken-3">{{ results.ai_analysis.pedagogical_feedback.communication }}</div>
                    </div>
                  </div>
                  
                  <v-divider class="my-2" />
                  
                  <div class="d-flex align-start ga-2 text-amber-darken-4">
                    <v-icon size="small" color="amber-darken-3" class="mt-1">mdi-lightbulb-on</v-icon>
                    <div>
                      <strong class="text-subtitle-2">LỜI KHUYÊN TIẾN BỘ:</strong>
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
  </v-container>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { GRADE_LEVELS, SPEAKING_TOPICS, READING_LIBRARY } from '../constants/topics.js'

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
const loadingText = ref('Đang xử lý âm thanh...')
const results = ref(null)
const errorMessage = ref(null)

const isSecure = ref(window.isSecureContext)
const isLocalhost = ref(window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')

let mediaRecorder = null
let audioChunks = []
let durationTimer = null
let animationFrameId = null

const scoreCriteria = [
  { key: 'Pronunciation', name: 'Phát âm', desc: 'Đánh giá độ chuẩn xác khi phát âm từng từ và âm tiết IPA. Nói tròn vành rõ chữ, bật âm đuôi (/s/, /t/) đầy đủ để đạt điểm tối đa.' },
  { key: 'Fluency', name: 'Trôi chảy', desc: 'Đo tốc độ nói và nhịp điệu tự nhiên. Nói mượt mà, hạn chế ngập ngừng "ờ, ừ" và duy trì câu dài trên 15 từ để đạt điểm cao.' },
  { key: 'Grammar', name: 'Ngữ pháp', desc: 'Đánh giá tính chính xác của cấu trúc câu. Chia đúng thì động từ, câu có đầy đủ chủ ngữ - vị ngữ và không sai ngữ pháp cơ bản.' },
  { key: 'Vocabulary', name: 'Từ vựng', desc: 'Đo mức độ phong phú và độ hợp lý của từ vựng. Sử dụng từ vựng đúng chủ đề và tránh lặp lại một từ đơn giản quá nhiều lần.' },
  { key: 'Communication', name: 'Giao tiếp', desc: 'Đánh giá khả năng diễn đạt và độ bám sát chủ đề. Trả lời đúng trọng tâm câu hỏi và đưa ra lý do giải thích chi tiết ý tưởng.' }
]

const loadingTexts = [
  'Đang nhận diện giọng nói thành văn bản...',
  'Đang phân tích độ chuẩn xác của phát âm...',
  'Đang đánh giá các lỗi ngữ pháp...',
  'Đang tạo phản hồi sư phạm chuyên môn...'
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
    errorMessage.value = "Không thể truy cập Microphone. Vui lòng cho phép quyền truy cập micro trên trình duyệt."
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
      throw new Error(errData.detail || 'Không thể chấm điểm âm thanh.')
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
  if (score >= 8) return 'Xuất sắc! Em phát âm rất chuẩn!'
  if (score >= 6) return 'Khá tốt! Luyện tập thêm để giỏi hơn nữa nhé!'
  if (score >= 4) return 'Đạt yêu cầu! Đọc thêm phần nhận xét bên dưới nha!'
  return 'Cần cố gắng! Em luyện nói mỗi ngày để phát triển kỹ năng nhé!'
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
