<template>
  <v-container fluid class="pa-0">
    <v-row class="ma-0">
      <!-- Section 1: Student Profile & Daily Goal (Always Visible) -->
      <v-col cols="12" class="pa-1">
        <v-card border flat class="pa-3 bg-white" rounded="lg">
          <div class="d-flex align-center ga-2 mb-3">
            <v-avatar color="blue-lighten-5" size="36" class="text-primary mr-1 border">
              <v-icon size="small">mdi-account-outline</v-icon>
            </v-avatar>
            <div class="text-subtitle-1 font-weight-black text-secondary">Thông tin học sinh</div>
          </div>
          
          <v-row class="ma-0 align-center ga-2">
            <v-col cols="12" md="6" class="pa-1">
              <v-text-field
                v-model="localUserName"
                label="Họ và tên của em:"
                variant="outlined"
                density="comfortable"
                hide-details
                color="primary"
                prepend-inner-icon="mdi-card-account-details-outline"
                @update:model-value="saveSettings"
              />
            </v-col>
            <v-col cols="12" md="6" class="pa-1">
              <div class="d-flex align-center justify-space-between mb-1 px-1 flex-nowrap ga-2">
                <span class="text-caption font-weight-bold text-grey-darken-2 text-truncate">Mục tiêu luyện nói:</span>
                <span class="text-caption font-weight-black text-primary bg-blue-lighten-5 px-2 py-0.5 rounded-pill text-no-wrap flex-shrink-0">
                  {{ localDailyGoal }} lần/ngày
                </span>
              </div>
              <v-slider
                v-model="localDailyGoal"
                min="1"
                max="15"
                step="1"
                color="primary"
                track-color="grey-lighten-2"
                hide-details
                thumb-label="inverse"
                @update:model-value="saveSettings"
              />
            </v-col>
          </v-row>
        </v-card>
      </v-col>

      <!-- Developer Sections (Visible ONLY when isDevMode prop is true) -->
      <template v-if="isDevMode">
        <!-- Section 2: Backend API Config -->
        <v-col cols="12" class="pa-1">
          <v-card border flat class="pa-3 bg-white" rounded="lg">
            <div class="d-flex align-center ga-2 mb-3">
              <v-avatar color="indigo-lighten-5" size="36" class="text-indigo mr-1 border">
                <v-icon size="small">mdi-server-network</v-icon>
              </v-avatar>
              <div class="text-subtitle-1 font-weight-black text-secondary">[Dev] Kết nối Máy chủ (API)</div>
            </div>

            <v-row class="ma-0 align-center ga-2">
              <v-col cols="12" sm="8" class="pa-1">
                <v-text-field
                  v-model="localBackendUrl"
                  label="Đường dẫn API máy chủ:"
                  placeholder="Ví dụ: http://localhost:8000"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  color="primary"
                  prepend-inner-icon="mdi-link-variant"
                />
              </v-col>
              <v-col cols="12" sm="4" class="pa-1">
                <v-btn
                  color="primary"
                  variant="flat"
                  block
                  height="48"
                  class="font-weight-bold text-caption text-sm-body-2"
                  prepend-icon="mdi-transit-connection-variant"
                  :loading="isTestingConnection"
                  @click="testConnection"
                >
                  Kiểm tra kết nối
                </v-btn>
              </v-col>
            </v-row>

            <v-alert
              v-if="connectionStatus"
              :type="connectionStatus.success ? 'success' : 'error'"
              density="compact"
              variant="tonal"
              class="mt-3 py-2 text-caption text-sm-subtitle-2 font-weight-medium"
              hide-details
            >
              {{ connectionStatus.message }}
            </v-alert>
          </v-card>
        </v-col>

        <!-- Section 3: Restore Backup -->
        <v-col cols="12" class="pa-1">
          <v-card border flat class="pa-3 bg-white" rounded="lg">
            <div class="d-flex align-center ga-2 mb-2">
              <v-avatar color="purple-lighten-5" size="36" class="text-purple mr-1 border">
                <v-icon size="small">mdi-database-refresh-outline</v-icon>
              </v-avatar>
              <div class="text-subtitle-1 font-weight-black text-secondary">[Dev] Phục hồi dữ liệu (Restore)</div>
            </div>
            <div class="text-caption text-grey-darken-1 mb-3 pl-1">
              Chọn tệp tin backup `.json` từ máy để tải lại toàn bộ lịch sử luyện tập của em trước đó.
            </div>
            
            <v-row class="ma-0 align-center ga-2">
              <v-col cols="12" sm="8" class="pa-1">
                <v-file-input
                  label="Chọn tệp sao lưu (.json)"
                  accept="application/json"
                  density="comfortable"
                  variant="outlined"
                  hide-details
                  prepend-icon=""
                  prepend-inner-icon="mdi-file-download-outline"
                  @change="handleBackupUpload"
                />
              </v-col>
              <v-col cols="12" sm="4" class="pa-1">
                <v-btn
                  color="secondary"
                  variant="flat"
                  block
                  height="48"
                  class="font-weight-bold text-caption text-sm-body-2"
                  prepend-icon="mdi-cloud-upload-outline"
                  :disabled="!backupFile"
                  @click="restoreBackup"
                >
                  Khôi phục lịch sử
                </v-btn>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </template>

      <!-- Section 4: About App info (Always Visible) -->
      <v-col cols="12" class="pa-1">
        <v-card border flat class="pa-3 bg-blue-lighten-5" rounded="lg">
          <div class="d-flex align-center ga-2 mb-2">
            <v-icon color="primary">mdi-information-outline</v-icon>
            <div class="text-subtitle-2 font-weight-bold text-primary">Về ứng dụng FLUENT</div>
          </div>
          
          <div class="text-caption text-grey-darken-3 pl-1" style="line-height: 1.6;">
            <strong>FLUENT - Trợ lý luyện nói Tiếng Anh Học đường</strong><br>
            Ứng dụng giúp học sinh đánh giá chính xác khả năng phát âm, rèn luyện sự tự tin thông qua AI.
            Mọi xử lý đều được bảo mật tối đa và lưu dữ liệu trực tiếp trong thiết bị của em.<br>
            • <strong>Phiên bản</strong>: 5.0 (Vite + Vue 3 + Vuetify 3 + FastAPI)<br>
            • <strong>Phát triển bởi</strong>: August Trung • <strong>Tên miền ứng dụng</strong>: <a href="https://fluent.augusttrung.com" target="_blank" class="text-primary font-weight-bold text-decoration-none">fluent.augusttrung.com</a>
          </div>
        </v-card>
      </v-col>

      <!-- Section 5: Frequently Asked Questions (FAQ) -->
      <v-col cols="12" class="pa-1">
        <v-card border flat class="pa-3 bg-white" rounded="lg">
          <div class="d-flex align-center ga-2 mb-3">
            <v-avatar color="amber-lighten-5" size="36" class="text-amber-darken-3 mr-1 border">
              <v-icon size="small">mdi-help-circle-outline</v-icon>
            </v-avatar>
            <div>
              <div class="text-subtitle-1 font-weight-black text-secondary">Các câu hỏi thường gặp (FAQ)</div>
              <div class="text-caption text-grey-darken-1">Giải đáp thắc mắc về AI chấm điểm, bảo mật và phương pháp học tập</div>
            </div>
          </div>

          <v-expansion-panels variant="accordion" class="border rounded-lg overflow-hidden">
            <v-expansion-panel v-for="(faq, i) in faqs" :key="i" elevation="0" class="border-b">
              <v-expansion-panel-title class="py-3 px-3 text-caption text-sm-subtitle-2 font-weight-black text-grey-darken-4">
                <div class="d-flex align-center ga-2">
                  <v-icon color="primary" size="small">mdi-comment-question-outline</v-icon>
                  <span>{{ faq.question }}</span>
                </div>
              </v-expansion-panel-title>
              <v-expansion-panel-text class="text-caption text-grey-darken-3 py-2 px-3 bg-grey-lighten-5" style="line-height: 1.6;">
                <div v-html="faq.answer"></div>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, watch } from 'vue'

const faqs = ref([
  {
    question: "AI có tự động sửa phát âm sai thành đúng nếu bài nói quá trôi chảy không?",
    answer: "<strong>Không.</strong> FLUENT áp dụng cơ chế đánh giá 3 lớp nghiêm ngặt: (1) Bóc tách chính xác từng âm tiết thực tế thu âm được; (2) Thuật toán Fuzzy Matching kiểm tra đối chiếu từng từ với bản mẫu; (3) AI đánh giá 6 kỹ năng độc lập. Bất kỳ từ nào phát âm thiếu âm cuối (như <code>-s</code>, <code>-ed</code>), đọc chệch nguyên âm hay bỏ từ đều bị phát hiện và cảnh báo màu Đỏ/Vàng rõ ràng."
  },
  {
    question: "Điểm số 6 kỹ năng (Phát âm, Trọng âm, Ngữ điệu...) được AI chấm theo tiêu chuẩn nào?",
    answer: "Điểm số được đánh giá dựa trên khung tham chiếu phát âm Tiếng Anh chuẩn quốc tế (bảng phiên âm IPA) kết hợp mô hình AI Llama-3.3-70B / Gemini Flash. AI phân tích độ chính xác từ vựng, nhịp điệu bài nói, độ trôi chảy (Fluency), trọng âm câu (Stress) và ngữ điệu (Intonation) để quy đổi ra thang điểm 10 chuẩn mực sư phạm."
  },
  {
    question: "Dữ liệu giọng nói và thông tin cá nhân của học sinh có được bảo mật không?",
    answer: "<strong>Hoàn toàn bảo mật.</strong> File ghi âm giọng nói chỉ được xử lý tức thì trong bộ nhớ đệm để trích xuất văn bản và phân tích điểm, không lưu trữ vĩnh viễn trên máy chủ công cộng. Lịch sử bài tập và mục tiêu luyện tập được mã hóa và lưu trực tiếp theo tài khoản cá nhân của em."
  },
  {
    question: "Làm thế nào để đạt điểm 9 - 10 trong phần 'Luyện nói tự do theo chủ đề'?",
    answer: "Để đạt điểm cao, em cần đáp ứng 3 yếu tố cốt lõi:<br>1. <strong>Phát âm tròn chữ</strong>: Đọc rõ ràng các phụ âm cuối và trọng âm từ.<br>2. <strong>Độ khớp chủ đề cao</strong>: Trả lời đúng trọng tâm câu hỏi gợi ý của bài tập.<br>3. <strong>Cấu trúc câu tự nhiên</strong>: Áp dụng các từ vựng linh hoạt. Em có thể tham khảo thẻ <strong>'Gợi ý câu bản xứ chuẩn'</strong> ở kết quả đánh giá để học cách diễn đạt hay nhất."
  },
  {
    question: "Chế độ 'Luyện ngữ điệu (Shadowing)' khác gì với 'Luyện nói tự do'?",
    answer: "• <strong>Luyện ngữ điệu (Shadowing)</strong>: Giúp em tập trung rèn luyện cơ miệng, phát âm chuẩn từng từ và bắt chước nhịp điệu, ngắt nghỉ theo câu mẫu của người bản xứ.<br>• <strong>Luyện nói tự do (Topic Practice)</strong>: Rèn luyện khả năng phản xạ, tư duy Tiếng Anh và xây dựng câu nói độc lập theo chủ đề bài học."
  },
  {
    question: "Nếu em phát âm sai một số từ thì làm sao để rèn luyện lại?",
    answer: "Tất cả các từ em phát âm chưa chuẩn sẽ tự động được AI tổng hợp vào <strong>'Bộ từ vựng cần cải thiện' (Weak Words)</strong> trong mục Hồ sơ. Em có thể mở phần này ra bất cứ lúc nào để nghe phát âm mẫu IPA và luyện lại từng từ cho đến khi đạt điểm tuyệt đối."
  },
  {
    question: "Hệ thống phân tích và chấm điểm âm tiết IPA (International Phonetic Alphabet) như thế nào?",
    answer: "Hệ thống sử dụng bộ chuyển đổi G2P (Grapheme-to-Phoneme) <code>eng_to_ipa</code> kết hợp thuật toán căn chỉnh âm tiết <strong>Phonetic Levenshtein Alignment</strong> theo chuẩn công nghiệp quốc tế. Mỗi câu nói của em được phân tách thành từng âm IPA để phát hiện chính xác các lỗi nuốt âm đuôi (như /s/, /t/, /d/), lệch nguyên âm hay phát âm ngắt ngữ, từ đó hỗ trợ điều chỉnh khẩu hình miệng chuẩn bản xứ."
  }
])

const props = defineProps({
  userName: {
    type: String,
    required: true
  },
  dailyGoal: {
    type: Number,
    required: true
  },
  backendUrl: {
    type: String,
    required: true
  },
  isDevMode: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update-settings', 'restore-history'])

// Local state initialized from props
const localUserName = ref(props.userName || '')
const localDailyGoal = ref(props.dailyGoal || 5)
const localBackendUrl = ref(props.backendUrl || '')

const isTestingConnection = ref(false)
const connectionStatus = ref(null)

const backupFile = ref(null)

// Watch props to sync changes
watch(() => props.userName, (newVal) => { if (newVal) localUserName.value = newVal })
watch(() => props.dailyGoal, (newVal) => { localDailyGoal.value = newVal || 5 }, { immediate: true })
watch(() => props.backendUrl, (newVal) => { if (newVal) localBackendUrl.value = newVal })

// Save settings to parent
const saveSettings = () => {
  emit('update-settings', {
    userName: localUserName.value,
    dailyGoal: localDailyGoal.value,
    backendUrl: localBackendUrl.value
  })
}

// Watch backend URL change to trigger auto-save
watch(localBackendUrl, () => {
  saveSettings()
})

const testConnection = async () => {
  isTestingConnection.value = true
  connectionStatus.value = null
  
  try {
    const url = localBackendUrl.value.replace(/\/$/, '')
    const response = await fetch(`${url}/api/health`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    })
    
    if (!response.ok) throw new Error()
    
    const data = await response.json()
    if (data.status === 'healthy') {
      connectionStatus.value = {
        success: true,
        message: `🟢 Kết nối thành công! Máy chủ AI đang hoạt động tốt (Model: ${data.model_size}).`
      }
    } else {
      connectionStatus.value = {
        success: true,
        message: '🟡 Kết nối thành công! Máy chủ AI đang khởi động mô hình trong giây lát.'
      }
    }
  } catch (err) {
    connectionStatus.value = {
      success: false,
      message: '🔴 Không thể kết nối tới máy chủ. Vui lòng kiểm tra lại đường dẫn API hoặc kiểm tra xem máy chủ đã bật chưa.'
    }
  } finally {
    isTestingConnection.value = false
  }
}

const handleBackupUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    backupFile.value = file
  } else {
    backupFile.value = null
  }
}

const restoreBackup = () => {
  if (!backupFile.value) return
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result)
      if (data && Array.isArray(data.history)) {
        emit('restore-history', data.history)
        alert(`🎉 Phục hồi thành công! Đã khôi phục ${data.history.length} bản ghi lịch sử vào ứng dụng.`)
        backupFile.value = null
      } else {
        throw new Error('Sai định dạng.')
      }
    } catch (err) {
      alert('Không thể khôi phục. Tệp tin không đúng định dạng sao lưu của ứng dụng.')
      console.error(err)
    }
  }
  reader.readAsText(backupFile.value)
}
</script>
