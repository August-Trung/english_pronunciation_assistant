<template>
  <v-container fluid class="pa-0 max-width-700">
    <!-- Rich Teal Gradient Banner Card (Sang trọng, bắt mắt) -->
    <v-card border flat class="pa-3 pa-sm-4 mb-4 text-white rounded-lg" style="background: linear-gradient(135deg, #009688 0%, #004D40 100%);">
      <div class="d-flex align-center ga-2 ga-sm-3">
        <v-avatar color="teal-lighten-4" size="40" class="flex-shrink-0">
          <v-icon color="teal-darken-4" size="default">mdi-waveform</v-icon>
        </v-avatar>
        <div>
          <div class="text-subtitle-1 text-sm-h6 font-weight-black tracking-tight leading-tight">LUYỆN NGỮ ĐIỆU (SHADOWING)</div>
          <div class="text-caption text-teal-lighten-4">Luyện nói theo ngữ điệu câu mẫu để phát âm tự nhiên như người bản xứ</div>
        </div>
      </div>
    </v-card>

    <!-- Main Content -->
    <div class="mb-4">
      <!-- Level Selection Filter -->
      <div class="d-flex align-center justify-space-between mb-3 flex-wrap ga-2">
        <div class="text-subtitle-2 font-weight-black text-grey-darken-3 d-flex align-center ga-1">
          <v-icon color="teal" size="small">mdi-text-box-search-outline</v-icon>
          <span>Chọn cấp độ luyện tập:</span>
        </div>

        <v-btn-toggle
          v-model="selectedLevel"
          mandatory
          color="teal"
          density="compact"
          variant="outlined"
          rounded="pill"
        >
          <v-btn value="easy" size="x-small">Cơ bản</v-btn>
          <v-btn value="medium" size="x-small">Giao tiếp</v-btn>
          <v-btn value="hard" size="x-small">Nâng cao</v-btn>
        </v-btn-toggle>
      </div>

      <!-- Active Sample Sentence Box -->
      <div class="pa-4 rounded-lg mb-4 text-center border" style="background: linear-gradient(135deg, #E0F2F1 0%, #B2DFDB 100%);">
        <div class="text-caption text-teal-darken-4 font-weight-bold mb-1">
          Câu mẫu AI đề xuất:
        </div>

        <div class="text-subtitle-1 font-weight-black text-grey-darken-4 mb-1">
          "{{ currentSentence.text }}"
        </div>
        <div class="text-caption text-grey-darken-3 font-italic mb-3" style="font-size: 11px;">
          IPA: /{{ currentSentence.ipa }}/ • Nghĩa: {{ currentSentence.meaning }}
        </div>

        <!-- Audio Accent Setting -->
        <div class="d-flex align-center justify-center ga-2 mb-2">
          <v-chip-group v-model="ttsAccent" mandatory density="compact" color="teal">
            <v-chip value="en-US" size="x-small" label variant="tonal">🇺🇸 Giọng Mỹ (US)</v-chip>
            <v-chip value="en-GB" size="x-small" label variant="tonal">🇬🇧 Giọng Anh (UK)</v-chip>
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
            Nghe đọc mẫu
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
            AI tạo câu mới
          </v-btn>
        </div>
      </div>

      <!-- Micro Studio Section -->
      <div class="text-center my-1 py-1">
        <div class="text-caption text-grey-darken-2 mb-1">
          {{ isRecording ? 'Đang thu âm... Bấm nút để dừng:' : 'Bấm nút dưới, đọc theo ngữ điệu câu mẫu:' }}
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
          Đang thu âm... ({{ recordingDuration }}s)
        </div>

        <div v-if="isAnalyzing" class="text-caption text-teal-darken-3 animate-pulse py-1">
          AI đang phân tích ngữ điệu...
        </div>
      </div>

      <!-- Error Alert -->
      <v-card v-if="errorMessage" border flat rounded="lg" class="pa-3 my-2 bg-orange-lighten-5 text-center">
        <v-icon color="warning" size="small" class="mr-1">mdi-alert-circle-outline</v-icon>
        <span class="text-caption font-weight-bold text-warning-darken-3">{{ errorMessage }}</span>
      </v-card>

      <!-- Analysis Result -->
      <div v-if="result && !isAnalyzing" class="d-flex flex-column ga-3 mt-3">
        <!-- 1. CÂU EM ĐÃ PHÁT ÂM & THỦ THỬ NGHE LẠI -->
        <div class="pa-3 bg-blue-lighten-5 rounded-lg border">
          <div class="text-body-2 font-weight-bold text-primary mb-2 d-flex align-center ga-1">
            <v-icon color="primary" size="small">mdi-message-text-outline</v-icon>
            <span>Câu em đã phát âm:</span>
            <span class="font-weight-black text-primary-darken-2 ml-1">"{{ result.transcribed_text }}"</span>
          </div>

          <!-- AUDIO PLAYER NGHE LẠI ĐOẠN THU ÂM -->
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
              {{ isPlaying ? 'Đang phát...' : 'Nghe lại giọng vừa thu âm' }}
            </div>
            <audio ref="audioPlayer" :src="audioUrl" @ended="isPlaying = false" class="d-none" />
          </div>
        </div>

        <!-- 2. THẺ TỔNG QUAN -->
        <v-card border flat rounded="lg" class="pa-3" :class="result.score >= 6 ? 'bg-teal-lighten-5 border-teal' : 'bg-orange-lighten-5 border-orange'">
          <div class="d-flex align-center justify-space-between mb-1">
            <div class="d-flex align-center ga-2">
              <v-chip :color="result.score >= 6 ? 'teal' : 'orange-darken-3'" font-weight-bold size="small" variant="flat">
                <v-icon size="x-small" start>mdi-target</v-icon>
                Độ Chính Xác {{ result.reading_result ? result.reading_result.accuracy.toFixed(0) : 0 }}%
              </v-chip>
              <span class="text-subtitle-2 font-weight-black" :class="result.score >= 8 ? 'text-teal-darken-4' : result.score >= 6 ? 'text-teal-darken-3' : 'text-orange-darken-4'">
                {{ result.score >= 8 ? 'Xuất Sắc!' : result.score >= 6 ? 'Rất Tốt!' : 'Cần Cải Thiện!' }}
              </span>
            </div>
            <div class="text-h5 font-weight-black" :class="result.score >= 6 ? 'text-teal-darken-4' : 'text-orange-darken-4'">
              {{ result.score.toFixed(1).replace('.', ',') }}/10
            </div>
          </div>
          <div class="text-caption font-weight-bold" :class="result.score >= 6 ? 'text-teal-darken-4' : 'text-orange-darken-4'">
            <v-icon size="x-small" class="mr-1">mdi-information-outline</v-icon>
            {{ result.score < 5 ? 'Em chưa đọc khớp câu mẫu, hãy đọc to và rõ ràng từng từ hơn nhé!' : (result.ai_analysis?.topic_comment || 'Em đã hoàn thành đọc nhại ngữ điệu câu mẫu rất tốt!') }}
          </div>
        </v-card>

        <!-- 3. THẺ ĐỐI CHIẾU TỪNG TỪ BÀI ĐỌC MẪU -->
        <v-card v-if="result.reading_result" border flat rounded="lg" class="pa-3 bg-light-blue-lighten-5 border-blue">
          <div class="d-flex align-center justify-space-between mb-2">
            <div class="text-subtitle-2 font-weight-black text-primary d-flex align-center ga-1">
              <v-icon color="primary" size="small">mdi-bullseye-arrow</v-icon>
              Đối Chiếu Từng Từ Bài Đọc Mẫu
            </div>
            <v-chip color="primary" font-weight-bold size="small" variant="flat">
              {{ result.reading_result.spoken_words_count }}/{{ result.reading_result.target_words_count }} từ
            </v-chip>
          </div>

          <div class="text-caption text-grey-darken-2 mb-2 font-weight-bold">
            Chi tiết từng từ (Xanh = Đọc chuẩn, Vàng = Đọc ngắt/sai nhẹ, Đỏ = Đọc thiếu/sai):
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

        <!-- THẺ CHẤM & ĐỐI CHIẾU PHIÊN ÂM IPA CHUẨN QUỐC TẾ -->
        <v-card v-if="result.ipa_analysis" border flat rounded="lg" class="pa-3 mb-3 bg-teal-lighten-5 border-teal">
          <div class="d-flex align-center justify-space-between mb-2">
            <div class="text-subtitle-2 font-weight-black text-teal-darken-4 d-flex align-center ga-1">
              <v-icon color="teal-darken-2" size="small">mdi-bookmark-music-outline</v-icon>
              <span>Phân Tích & Chấm Âm Tiết IPA (Chuẩn Quốc Tế)</span>
            </div>
            <v-chip color="teal-darken-3" font-weight-bold size="small" variant="flat">
              IPA {{ result.ipa_analysis.ipa_accuracy }}%
            </v-chip>
          </div>

          <!-- Full IPA sentence comparison -->
          <div class="bg-white pa-2 rounded border mb-2 text-caption">
            <div class="d-flex align-center ga-2 mb-1">
              <span class="font-weight-black text-primary">IPA Câu Mẫu:</span>
              <span class="font-weight-bold text-teal-darken-4 font-mono">{{ result.ipa_analysis.target_full_ipa }}</span>
            </div>
            <div class="d-flex align-center ga-2">
              <span class="font-weight-black text-secondary">IPA Em Đọc:</span>
              <span class="font-weight-bold text-indigo-darken-3 font-mono">{{ result.ipa_analysis.spoken_full_ipa }}</span>
            </div>
          </div>

          <!-- Biểu đồ Đường Cong Ngữ Điệu (Pitch Intonation Chart F0) -->
          <div v-if="result.ipa_analysis.pitch_analysis?.pitch_points?.length" class="bg-white pa-3 rounded border mb-3">
            <div class="d-flex align-center justify-space-between mb-2">
              <div class="text-caption font-weight-black text-indigo-darken-3 d-flex align-center ga-1">
                <v-icon color="indigo" size="x-small">mdi-chart-bell-curve-cumulative</v-icon>
                <span>Biểu Đồ Đường Cong Ngữ Điệu & Trầm Bổng (F0 Pitch Contour)</span>
              </div>
              <v-chip size="x-small" color="indigo" variant="tonal" class="font-weight-black">
                Khớp ngữ điệu {{ result.ipa_analysis.pitch_analysis.pitch_accuracy }}%
              </v-chip>
            </div>
            <div class="d-flex align-center justify-space-between text-caption text-grey mb-1" style="font-size: 10px;">
              <span><v-icon size="x-small" color="primary">mdi-minus</v-icon> Giọng bản xứ (Native)</span>
              <span><v-icon size="x-small" color="amber-darken-3">mdi-minus</v-icon> Giọng học sinh</span>
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

          <!-- Thẻ Nối Âm Tự Nhiên (Connected Speech & Liaisons) -->
          <div v-if="result.ipa_analysis.linking_pairs?.length" class="bg-amber-lighten-5 pa-2.5 rounded border border-amber mb-3">
            <div class="text-caption font-weight-black text-amber-darken-4 mb-1 d-flex align-center ga-1">
              <v-icon color="amber-darken-4" size="x-small">mdi-link-variant</v-icon>
              <span>Gợi Ý Nối Âm Tự Nhiên Bản Xứ (Connected Speech):</span>
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
                {{ pair.word1 }} 🔗 {{ pair.word2 }} ({{ pair.ipa_link }})
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
                Đọc: {{ w_ipa.spoken_ipa }}
              </div>
              <div v-if="w_ipa.note" class="text-caption text-error font-weight-bold text-center mt-0.5" style="font-size: 9px; line-height: 1.1;">
                ⚠️ {{ w_ipa.note }}
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
                Khẩu hình
              </v-btn>
            </div>
          </div>
        </v-card>

        <!-- 4. THẺ GỢI Ý CÂU BẢN XỨ CHUẨN 3 CẤP ĐỘ -->
        <v-card v-if="result.ai_analysis?.native_suggestions?.length" border flat rounded="lg" class="pa-3 bg-purple-lighten-5 border-purple">
          <div class="text-subtitle-2 font-weight-black text-purple-darken-3 mb-2 d-flex align-center ga-1">
            <v-icon color="purple" size="small">mdi-star-face</v-icon>
            Gợi Ý Câu Bản Xứ Chuẩn (Native Expressions)
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
                Nghe mẫu
              </v-btn>
            </div>
          </div>
        </v-card>

        <!-- 5. THẺ SỬA LỖI NGỮ PHÁP & TỪ VỰNG TRỰC QUAN -->
        <v-card border flat rounded="lg" class="pa-3" :class="validGrammarFixes.length ? 'bg-orange-lighten-5 border-orange' : 'bg-green-lighten-5 border-green'">
          <div class="text-subtitle-2 font-weight-black mb-2 d-flex align-center ga-1" :class="validGrammarFixes.length ? 'text-orange-darken-4' : 'text-success'">
            <v-icon :color="validGrammarFixes.length ? 'orange-darken-3' : 'success'" size="small">
              {{ validGrammarFixes.length ? 'mdi-auto-fix' : 'mdi-check-decagram-outline' }}
            </v-icon>
            Sửa Lỗi Ngữ Pháp & Từ Vựng Trực Quan
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
                    Chưa chuẩn
                  </v-chip>
                  <span class="text-body-2 font-weight-bold text-error">"{{ fix.original }}"</span>
                </div>

                <div class="d-flex align-center ga-2 text-body-2 font-weight-bold text-success flex-wrap">
                  <v-chip color="success" size="x-small" variant="flat" class="font-weight-black flex-shrink-0" style="font-size: 10px; height: 20px;">
                    <v-icon size="x-small" start>mdi-check-circle-outline</v-icon>
                    Sửa lại
                  </v-chip>
                  <span class="text-body-2 font-weight-black text-success text-decoration-underline">"{{ fix.fixed }}"</span>
                </div>
              </div>

              <div v-if="fix.reason" class="text-caption text-grey-darken-3 pl-1 pt-2 border-t mt-2" style="line-height: 1.5;">
                <v-icon size="x-small" color="amber-darken-3" class="mr-1">mdi-lightbulb-on-outline</v-icon>
                <strong>Giải thích:</strong> {{ fix.reason }}
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

        <!-- 6. BẢNG ĐIỂM 5 KỸ NĂNG -->
        <v-card v-if="result.ai_analysis?.scores" border flat rounded="lg" class="pa-3 bg-grey-lighten-5">
          <div class="text-caption font-weight-bold text-grey-darken-1 mb-2 d-flex align-center ga-1">
            <v-icon size="x-small" color="grey-darken-2">mdi-chart-box-outline</v-icon>
            <span>Điểm chi tiết từng kỹ năng:</span>
          </div>
          <v-row density="compact">
            <v-col cols="4" sm="2" class="text-center">
              <div class="text-caption text-grey font-weight-bold">Phát âm</div>
              <div class="text-subtitle-2 font-weight-black text-primary">{{ result.ai_analysis.scores.pronunciation }}/2</div>
            </v-col>
            <v-col cols="4" sm="2" class="text-center">
              <div class="text-caption text-grey font-weight-bold">Trôi chảy</div>
              <div class="text-subtitle-2 font-weight-black text-primary">{{ result.ai_analysis.scores.fluency }}/2</div>
            </v-col>
            <v-col cols="4" sm="2" class="text-center">
              <div class="text-caption text-grey font-weight-bold">Ngữ pháp</div>
              <div class="text-subtitle-2 font-weight-black text-primary">{{ result.ai_analysis.scores.grammar }}/2</div>
            </v-col>
            <v-col cols="4" sm="2" class="text-center">
              <div class="text-caption text-grey font-weight-bold">Từ vựng</div>
              <div class="text-subtitle-2 font-weight-black text-primary">{{ result.ai_analysis.scores.vocabulary }}/2</div>
            </v-col>
            <v-col cols="4" sm="2" class="text-center">
              <div class="text-caption text-grey font-weight-bold">Giao tiếp</div>
              <div class="text-subtitle-2 font-weight-black text-primary">{{ result.ai_analysis.scores.communication }}/2</div>
            </v-col>
            <v-col cols="4" sm="2" class="text-center">
              <div class="text-caption text-grey font-weight-bold">Độ rõ tiếng</div>
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
              <div class="text-caption font-weight-bold text-primary font-mono">Phiên âm: {{ selectedArticulation.ipa }}</div>
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
          <div class="text-caption font-weight-black text-teal-darken-4">Sơ đồ chuyển động luồng hơi & đầu lưỡi</div>
        </div>

        <div class="space-y-2 text-caption">
          <div class="bg-grey-lighten-4 pa-2.5 rounded border mb-2">
            <span class="font-weight-black text-grey-darken-4 d-block mb-1">👄 1. Khẩu Hình Môi & Răng:</span>
            <span class="text-grey-darken-3">{{ selectedArticulation.mouth_position }}</span>
          </div>

          <div class="bg-grey-lighten-4 pa-2.5 rounded border mb-2">
            <span class="font-weight-black text-grey-darken-4 d-block mb-1">👅 2. Vị Trí Đầu Lưỡi:</span>
            <span class="text-grey-darken-3">{{ selectedArticulation.tongue_position }}</span>
          </div>

          <div class="bg-grey-lighten-4 pa-2.5 rounded border mb-2">
            <span class="font-weight-black text-grey-darken-4 d-block mb-1">💨 3. Luồng Hơi & Thanh Quản:</span>
            <span class="text-grey-darken-3">{{ selectedArticulation.airflow }}</span>
          </div>

          <div class="bg-amber-lighten-5 pa-2.5 rounded border border-amber">
            <span class="font-weight-black text-amber-darken-4 d-block mb-1">💡 Mẹo Luyện Tập Nhanh:</span>
            <span class="text-amber-darken-4 font-weight-bold">{{ selectedArticulation.tip }}</span>
          </div>
        </div>

        <v-card-actions class="px-0 pt-3 pb-0">
          <v-spacer />
          <v-btn color="primary" variant="flat" class="font-weight-black text-none" @click="speakText(selectedArticulation.ipa)">
            <v-icon class="mr-1">mdi-volume-high</v-icon> Nghe Âm Mẫu
          </v-btn>
          <v-btn color="grey-darken-1" variant="outlined" class="font-weight-bold text-none" @click="showArticulationModal = false">
            Đóng
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
    title: 'Phụ Âm Xì /s/ (Fricative)',
    ipa: '/s/',
    mouth_position: 'Hai hàm răng khép nhẹ, hai mép môi hơi kéo sang 2 bên như đang mỉm cười nhẹ.',
    tongue_position: 'Đầu lưỡi nâng gần sát nướu răng cửa trên (không chạm vào răng), tạo khe hẹp.',
    airflow: 'Đẩy luồng hơi xì xát liên tục qua khe giữa đầu lưỡi và nướu răng. Không rung dây thanh quản (Voiceless).',
    tip: 'Hãy giữ luồng hơi kéo dài 1-2 giây để tạo tiếng xì giòn giã.'
  },
  'z': {
    title: 'Phụ Âm Rung /z/ (Voiced Fricative)',
    ipa: '/z/',
    mouth_position: 'Khẩu hình môi và răng giống hệt âm /s/.',
    tongue_position: 'Đầu lưỡi nâng gần sát nướu răng cửa trên.',
    airflow: 'Khấu hình giống /s/ nhưng RUNG dây thanh quản (Voiced). Bạn cảm nhận cổ họng rung khi đọc.',
    tip: 'Đặt ngón tay lên cổ họng, bạn phải thấy cổ họng rung khi xì ra âm /z/.'
  },
  't': {
    title: 'Phụ Âm Bật /t/ (Plosive)',
    ipa: '/t/',
    mouth_position: 'Môi hơi mở tự nhiên.',
    tongue_position: 'Đầu lưỡi áp chặt vào nướu răng cửa trên để chặn hoàn toàn luồng khí.',
    airflow: 'Bật nhẹ đầu lưỡi xuống nhanh để giải phóng luồng khí nén tạo tiếng bật dứt khoát.',
    tip: 'Đặt bàn tay trước miệng, bạn phải cảm nhận được một luồng hơi bật mạnh ra.'
  },
  'd': {
    title: 'Phụ Âm Bật Rung /d/ (Voiced Plosive)',
    ipa: '/d/',
    mouth_position: 'Môi hơi mở tự nhiên.',
    tongue_position: 'Đầu lưỡi áp chặt vào nướu răng cửa trên.',
    airflow: 'Bật đầu lưỡi xuống đồng thời RUNG dây thanh quản.',
    tip: 'Âm bật trầm hơn âm /t/ và có độ rung nhẹ ở cổ họng.'
  },
  'th': {
    title: 'Phụ Âm Thè Lưỡi /θ/ & /ð/',
    ipa: '/θ/ - /ð/',
    mouth_position: 'Đặt đầu lưỡi thè ra giữa 2 hàm răng cửa (răng kẹp nhẹ lên lưỡi).',
    tongue_position: 'Đầu lưỡi thả lỏng đặt nhẹ giữa 2 hàm răng.',
    airflow: 'Đẩy luồng hơi xì qua khe giữa răng trên và mặt lưỡi.',
    tip: 'Đừng rụt lưỡi vào trong quá nhanh! Hãy thè nhẹ đầu lưỡi ra ngoài 1-2 cm.'
  },
  'r': {
    title: 'Phụ Âm Căng Lưỡi /r/',
    ipa: '/r/',
    mouth_position: 'Môi hơi chu tròn về phía trước.',
    tongue_position: 'Đầu lưỡi uốn cong ngược về phía sau vòm miệng (không chạm vòm miệng).',
    airflow: 'Luồng khí đi qua khe giữa vòm miệng và thân lưỡi căng.',
    tip: 'Tưởng tượng lưỡi tạo thành hình cái thìa uốn cong về sau.'
  },
  'l': {
    title: 'Phụ Âm Đầu Lưỡi /l/',
    ipa: '/l/',
    mouth_position: 'Miệng mở tự nhiên.',
    tongue_position: 'Đầu lưỡi chạm chắc vào nướu sau răng cửa trên.',
    airflow: 'Luồng khí thoát ra qua 2 bên mép lưỡi.',
    tip: 'Giữ đầu lưỡi dính chặt vào nướu răng trên khi kết thúc âm.'
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
    { text: "Practice makes perfect!", ipa: "ˈpræktɪs meɪks ˈpɜːfɪkt", meaning: "Có công mài sắt có ngày nên kim" },
    { text: "How are you doing today?", ipa: "haʊ ɑː juː ˈduːɪŋ təˈdeɪ", meaning: "Hôm nay bạn thế nào?" },
    { text: "Have a nice day!", ipa: "hæv ə naɪs deɪ", meaning: "Chúc bạn một ngày tốt lành!" },
    { text: "Nice to meet you!", ipa: "naɪs tuː miːt juː", meaning: "Rất vui được gặp bạn!" },
    { text: "Where are you from?", ipa: "weər ɑː juː frɒm", meaning: "Bạn đến từ đâu?" }
  ],
  medium: [
    { text: "Never put off until tomorrow what you can do today.", ipa: "ˈnɛvər pʊt ɒf ənˈtɪl təˈmɒrəʊ wɒt juː kæn duː təˈdeɪ", meaning: "Đừng để việc hôm nay đến ngày mai" },
    { text: "I really appreciate your help with this project.", ipa: "aɪ ˈrɪəli əˈpriːʃieɪt jɔː hɛlp wɪð ðɪs ˈprɒʤɛkt", meaning: "Tôi rất trân trọng sự giúp đỡ của bạn" },
    { text: "Learning a new language opens up a world of opportunities.", ipa: "ˈlɜːnɪŋ ə njuː ˈlæŋɡwɪʤ ˈəʊpənz ʌp ə wɜːld ɒv ˌɒpəˈtjuːnɪtiz", meaning: "Học một ngôn ngữ mới mở ra vô vàn cơ hội" },
    { text: "Could you please speak a little slower?", ipa: "kʊd juː pliːz spiːk ə ˈlɪtl ˈsləʊər", meaning: "Bạn có thể nói chậm lại một chút không?" }
  ],
  hard: [
    { text: "Success is not final, failure is not fatal: it is the courage to continue that counts.", ipa: "səkˈsɛs ɪz nɒt ˈfaɪnl ˈfeɪljər ɪz nɒt ˈfeɪtl", meaning: "Thành công không phải là vĩnh cửu, thất bại không phải là tận cùng" },
    { text: "The future belongs to those who believe in the beauty of their dreams.", ipa: "ðə ˈfjuːtʃər bɪˈlɒŋz tuː ðəʊz huː bɪˈliːv ɪn ðə ˈbjuːti ɒv ðeər driːmz", meaning: "Tương lai thuộc về những ai tin vào vẻ đẹp của giấc mơ" },
    { text: "In the middle of every difficulty lies opportunity.", ipa: "ɪn ðə ˈmɪdl ɒv ˈɛvri ˈdɪfɪkəlti laɪz ˌɒpəˈtjuːnɪti", meaning: "Trong trung tâm của mỗi khó khăn luôn ẩn chứa cơ hội" }
  ]
}

const aiSentencePool = {
  easy: [
    { text: "Keep up the great work!", ipa: "kiːp ʌp ðə ɡreɪt wɜːk", meaning: "Tiếp tục phát huy phong độ tốt nhé!" },
    { text: "Where is the nearest coffee shop?", ipa: "weər ɪz ðə ˈnɪərɪst ˈkɒfi ʃɒp", meaning: "Quán cà phê gần nhất ở đâu?" },
    { text: "What time does the train leave?", ipa: "wɒt taɪm dʌz ðə treɪn liːv", meaning: "Mấy giờ chuyến tàu khởi hành?" },
    { text: "I really love learning English!", ipa: "aɪ ˈrɪəli lʌv ˈlɜːnɪŋ ˈɪŋɡlɪʃ", meaning: "Tôi rất thích học tiếng Anh!" },
    { text: "Thank you for your warm welcome!", ipa: "θæŋk juː fɔː jɔː wɔːm ˈwɛlkəm", meaning: "Cảm ơn sự đón tiếp nồng hậu của bạn!" }
  ],
  medium: [
    { text: "Practice makes progress, not perfection.", ipa: "ˈpræktɪs meɪks ˈprəʊɡrɛs nɒt pəˈfɛkʃən", meaning: "Luyện tập tạo nên sự tiến bộ, không phải sự hoàn hảo." },
    { text: "Could you please give me a hand with this bag?", ipa: "kʊd juː pliːz ɡɪv miː ə hænd wɪð ðɪs bæɡ", meaning: "Bạn có thể giúp tôi một tay với chiếc túi này không?" },
    { text: "I will call you back as soon as I finish my work.", ipa: "aɪ wɪl kɔːl juː bæk æz suːn æz aɪ ˈfɪnɪʃ maɪ wɜːk", meaning: "Tôi sẽ gọi lại cho bạn ngay khi hoàn thành công việc." }
  ],
  hard: [
    { text: "The secret of getting ahead is getting started.", ipa: "ðə ˈsiːkrɪt ɒv ˈɡɛtɪŋ əˈhɛd ɪz ˈɡɛtɪŋ ˈstɑːtɪd", meaning: "Bí mật của việc vươn lên dẫn đầu là hãy bắt đầu ngay." },
    { text: "Great things are done by a series of small things brought together.", ipa: "ɡreɪt θɪŋz ɑː dʌn baɪ ə ˈsɪəriːz ɒv smɔːl θɪŋz brɔːt təˈɡɛðər", meaning: "Những điều vĩ đại được tạo nên từ chuỗi những việc nhỏ cộng lại." }
  ]
}

const isGeneratingAI = ref(false)
const dynamicSentence = ref(null)
const currentIndex = ref(0)

const currentSentence = computed(() => {
  if (dynamicSentence.value) return dynamicSentence.value
  return sampleSentences[selectedLevel.value][currentIndex.value] || sampleSentences.easy[0]
})

const generateAISentence = () => {
  isGeneratingAI.value = true
  result.value = null
  errorMessage.value = null
  audioBlob.value = null
  
  setTimeout(() => {
    const pool = aiSentencePool[selectedLevel.value] || aiSentencePool.easy
    const randomPick = pool[Math.floor(Math.random() * pool.length)]
    dynamicSentence.value = randomPick
    isGeneratingAI.value = false
  }, 250)
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
    errorMessage.value = 'Không thể mở micro! Hãy cấp quyền micro trên trình duyệt.'
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
      throw new Error(errData.detail || 'Không thể nhận diện giọng nói. Em hãy phát âm to và rõ ràng hơn nhé!')
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
