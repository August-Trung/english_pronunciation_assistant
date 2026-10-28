<template>
  <v-container fluid class="pa-0">
    <!-- Header Banner -->
    <v-card id="tour-history-header" flat border class="pa-4 pa-md-6 mb-4 bg-white" rounded="lg">
      <div class="d-flex flex-column flex-md-row align-start align-md-center justify-space-between ga-3">
        <div class="d-flex align-center ga-3">
          <v-avatar color="indigo-lighten-5" size="48" class="text-indigo border flex-shrink-0">
            <v-icon size="28">mdi-history</v-icon>
          </v-avatar>
          <div>
            <div class="d-flex align-center ga-2 flex-wrap">
              <h1 class="text-h6 font-weight-black text-indigo-darken-3 tracking-tight mb-0">
                Student Practice History & Evaluation Logs
              </h1>
              <v-chip v-if="userName" size="small" color="indigo" variant="tonal" class="font-weight-black flex-shrink-0">
                <v-icon start size="x-small">mdi-account-circle</v-icon>
                {{ userName }}
              </v-chip>
            </div>
            <p class="text-caption font-weight-medium text-grey-darken-1 mb-0 mt-1">
              Personalized practice portfolio. Review your past audio recordings, 5-skill AI scores, and export reports.
            </p>
          </div>
        </div>

        <!-- Export Actions -->
        <div id="tour-history-exports" class="d-flex align-center ga-2 flex-wrap">
          <v-btn
            icon="mdi-lightbulb-on-outline"
            size="small"
            variant="text"
            color="amber-darken-3"
            title="Xem hướng dẫn Lịch sử luyện tập"
            @click="replayHistoryTour"
          />
          <v-btn
            color="secondary"
            variant="outlined"
            size="small"
            class="text-none font-weight-bold"
            prepend-icon="mdi-file-pdf-box"
            @click="showPdfDialog = true"
          >
            Export PDF Report
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            size="small"
            class="text-none font-weight-bold"
            prepend-icon="mdi-zip-box"
            :loading="isExportingZip"
            @click="downloadZipArchive"
          >
            Download ZIP Archive
          </v-btn>
        </div>
      </div>
    </v-card>

    <!-- 3-Day Expiration Warning Banner -->
    <v-alert
      v-if="expiringSoonCount > 0"
      type="warning"
      variant="tonal"
      density="comfortable"
      class="mb-4 border border-warning"
      icon="mdi-alert-decagram-outline"
      rounded="lg"
    >
      <template #title>
        <span class="font-weight-black">Storage Expiration Notice (30-Day Retention Limit)</span>
      </template>
      <div class="text-caption font-weight-medium">
        Audio recordings older than {{ earliestExpiringDate }} will be automatically cleaned up in <strong>3 days</strong>.
        Please click <strong>"Download ZIP Archive"</strong> or <strong>"Export PDF Report"</strong> to archive your practice sessions!
      </div>
    </v-alert>

    <!-- Filter Toolbar -->
    <v-card id="tour-history-filters" flat border class="pa-3 mb-4 bg-grey-lighten-5" rounded="lg">
      <div class="d-flex flex-column flex-sm-row align-start align-sm-center justify-space-between ga-3">
        <!-- Date Range Toggle -->
        <v-btn-toggle
          v-model="rangeType"
          mandatory
          color="indigo"
          density="compact"
          variant="outlined"
          class="bg-white"
          @update:model-value="fetchHistoryLogs"
        >
          <v-btn value="today" size="small" class="text-none font-weight-bold" prepend-icon="mdi-calendar-today">
            Today
          </v-btn>
          <v-btn value="30days" size="small" class="text-none font-weight-bold" prepend-icon="mdi-calendar-month">
            Last 30 Days
          </v-btn>
          <v-btn value="custom" size="small" class="text-none font-weight-bold" prepend-icon="mdi-calendar-range">
            Custom Date Range
          </v-btn>
        </v-btn-toggle>

        <!-- Custom Date Range Inputs -->
        <div v-if="rangeType === 'custom'" class="d-flex align-center ga-2 flex-wrap">
          <v-text-field
            v-model="customStartDate"
            type="date"
            density="compact"
            variant="outlined"
            hide-details
            style="max-width: 150px;"
            @change="fetchHistoryLogs"
          />
          <span class="text-caption font-weight-bold text-grey-darken-2">to</span>
          <v-text-field
            v-model="customEndDate"
            type="date"
            density="compact"
            variant="outlined"
            hide-details
            style="max-width: 150px;"
            @change="fetchHistoryLogs"
          />
        </div>
      </div>
    </v-card>

    <!-- History List Section -->
    <div v-if="isLoading" class="d-flex justify-center align-center py-12">
      <v-progress-circular indeterminate color="indigo" size="48" />
    </div>

    <div v-else-if="groupedHistory.length === 0" class="text-center py-12 bg-white rounded-lg border">
      <v-icon size="64" color="grey-lighten-1">mdi-history</v-icon>
      <div class="text-subtitle-1 font-weight-bold text-grey-darken-2 mt-2">No Practice History Recorded</div>
      <div class="text-caption text-grey-darken-1">Complete a practice session in Speaking Studio to build your log!</div>
    </div>

    <div v-else class="history-groups-container">
      <div v-for="group in groupedHistory" :key="group.date" class="mb-6">
        <!-- Date Header Divider -->
        <div class="d-flex align-center ga-2 mb-3 flex-nowrap">
          <v-chip color="indigo" variant="flat" size="small" class="font-weight-black flex-shrink-0 text-no-wrap" prepend-icon="mdi-calendar-check">
            {{ group.date }}
          </v-chip>
          <span class="text-caption font-weight-bold text-grey-darken-2 flex-shrink-0 text-no-wrap">
            ({{ group.items.length }} session{{ group.items.length > 1 ? 's' : '' }})
          </span>
          <v-divider class="flex-grow-1 ml-2" />
        </div>

        <!-- Sessions List for this Date -->
        <v-row>
          <v-col v-for="item in group.items" :key="item.id" cols="12" md="6">
            <v-card flat border rounded="lg" class="pa-4 bg-white h-100 d-flex flex-column justify-space-between">
              <div>
                <!-- Top metadata: Time & Topic -->
                <div class="d-flex align-center justify-space-between ga-2 mb-2">
                  <div class="text-caption font-weight-bold text-grey-darken-1 d-flex align-center ga-1 flex-shrink-0">
                    <v-icon size="x-small">mdi-clock-outline</v-icon>
                    <span class="text-no-wrap">{{ item.time }}</span>
                  </div>
                  <v-chip
                    :color="item.score >= 8 ? 'success' : item.score >= 6 ? 'warning' : 'error'"
                    size="x-small"
                    variant="flat"
                    class="font-weight-black flex-shrink-0 text-no-wrap"
                  >
                    Score {{ item.score }}/10
                  </v-chip>
                </div>

                <div class="text-subtitle-2 font-weight-black text-indigo-darken-3 mb-2 text-wrap text-break">
                  Topic: "{{ item.topic }}"
                </div>

                <!-- Transcribed Text -->
                <div class="bg-grey-lighten-4 pa-2.5 rounded border mb-3 text-caption font-weight-medium">
                  <span class="text-grey-darken-2 font-weight-bold">Transcribed Speech:</span>
                  <div class="text-grey-darken-4 mt-0.5 font-italic text-wrap text-break">"{{ item.transcribed }}"</div>
                </div>

                <!-- IPA Phonetic Alignment if available -->
                <div v-if="item.ipa" class="bg-teal-lighten-5 border border-teal pa-2.5 rounded mb-3 text-caption">
                  <div class="d-flex align-center ga-1 text-teal-darken-4 font-weight-black mb-1">
                    <v-icon size="x-small" color="teal-darken-3">mdi-waveform</v-icon>
                    <span>Target IPA vs Spoken IPA:</span>
                  </div>
                  <div class="font-mono text-teal-darken-4 font-weight-bold">Target: {{ item.ipa.target_full_ipa }}</div>
                  <div class="font-mono text-indigo-darken-3 font-weight-bold">Spoken: {{ item.ipa.spoken_full_ipa }}</div>
                </div>
              </div>

              <!-- Audio Player & Replay -->
              <div v-if="item.audio_url" class="border-t pt-3 mt-2 d-flex align-center justify-space-between ga-2">
                <v-btn
                  size="small"
                  variant="outlined"
                  color="indigo"
                  class="text-none font-weight-bold flex-grow-1"
                  prepend-icon="mdi-play-circle-outline"
                  @click="playAudio(item.audio_url)"
                >
                  Play Audio Recording
                </v-btn>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </div>

    <!-- PDF Export Selection Dialog Modal -->
    <v-dialog v-model="showPdfDialog" max-width="520">
      <v-card rounded="lg" class="pa-4">
        <div class="d-flex align-center justify-space-between mb-3 border-b pb-2">
          <div class="d-flex align-center ga-2">
            <v-avatar color="indigo-lighten-5" size="36" class="text-indigo border">
              <v-icon size="small">mdi-file-pdf-box</v-icon>
            </v-avatar>
            <span class="text-subtitle-1 font-weight-black text-indigo-darken-3">Select PDF Report Format</span>
          </div>
          <v-btn icon="mdi-close" variant="text" density="compact" @click="showPdfDialog = false" />
        </div>

        <v-radio-group v-model="pdfExportMode" hide-details class="mb-4">
          <v-card border flat class="pa-3 mb-2 cursor-pointer" :class="pdfExportMode === 'summary' ? 'bg-indigo-lighten-5 border-indigo' : ''" @click="pdfExportMode = 'summary'">
            <div class="d-flex align-start ga-2">
              <v-radio value="summary" color="indigo" class="mt-0" />
              <div>
                <div class="text-subtitle-2 font-weight-black text-indigo-darken-4">Option A: Executive Summary Report (3-4 Pages)</div>
                <div class="text-caption text-grey-darken-2">Aggregates all sessions into a clean 3-4 page academic summary table with performance radar & top weak words.</div>
              </div>
            </div>
          </v-card>

          <v-card border flat class="pa-3 cursor-pointer" :class="pdfExportMode === 'full' ? 'bg-indigo-lighten-5 border-indigo' : ''" @click="pdfExportMode = 'full'">
            <div class="d-flex align-start ga-2">
              <v-radio value="full" color="indigo" class="mt-0" />
              <div>
                <div class="text-subtitle-2 font-weight-black text-indigo-darken-4">Option B: Full Detailed Transcript PDF</div>
                <div class="text-caption text-grey-darken-2">Includes 100% of all practice sessions in unabridged detail (Target IPA vs. Spoken IPA & AI feedback).</div>
              </div>
            </div>
          </v-card>
        </v-radio-group>

        <div class="d-flex justify-end ga-2">
          <v-btn variant="outlined" color="grey" class="text-none font-weight-bold" @click="showPdfDialog = false">Cancel</v-btn>
          <v-btn color="indigo" variant="flat" class="text-none font-weight-bold" prepend-icon="mdi-download" :loading="isGeneratingPdf" @click="generateAcademicPdf">
            Generate PDF
          </v-btn>
        </div>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  runTour,
  TOUR_KEYS,
  STUDENT_HISTORY_TOUR_STEPS
} from '@/utils/tours.js'

const props = defineProps({
  backendUrl: {
    type: String,
    required: true
  },
  userId: {
    type: Number,
    default: 1
  },
  userName: {
    type: String,
    default: ''
  },
  userEmail: {
    type: String,
    default: ''
  }
})

const isLoading = ref(false)
const showPdfDialog = ref(false)
const pdfExportMode = ref('summary')
const isGeneratingPdf = ref(false)
const isExportingZip = ref(false)
const rangeType = ref('today')
const customStartDate = ref('')
const customEndDate = ref('')

const historyItems = ref([])
const expiringSoonCount = ref(0)
const earliestExpiringDate = ref('')

const fetchHistoryLogs = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/history/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: props.userId || 1,
        range_type: rangeType.value,
        start_date: customStartDate.value,
        end_date: customEndDate.value
      })
    })

    if (res.ok) {
      const data = await res.json()
      historyItems.value = data.history || []
      expiringSoonCount.value = data.expiring_soon_count || 0
      earliestExpiringDate.value = data.earliest_expiring_date || ''
    }
  } catch (err) {
    console.error('Error fetching history logs:', err)
  } finally {
    isLoading.value = false
  }
}

const groupedHistory = computed(() => {
  const groups = {}
  historyItems.value.forEach(item => {
    const dateStr = item.date || 'Unknown Date'
    if (!groups[dateStr]) {
      groups[dateStr] = { date: dateStr, items: [] }
    }
    groups[dateStr].items.push(item)
  })
  return Object.values(groups)
})

const playAudio = (url) => {
  if (!url) return
  const fullUrl = url.startsWith('http') ? url : `${props.backendUrl}${url}`
  const audio = new Audio(fullUrl)
  audio.play()
}

const generateAcademicPdf = () => {
  isGeneratingPdf.value = true
  try {
    // Generate clean academic HTML string and open printable report window
    const reportTitle = pdfExportMode.value === 'summary' ? 'Executive Summary Report' : 'Full Practice Transcript'
    let reportHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Fluent Academic English Studio - ${reportTitle}</title>
        <style>
          body { font-family: 'Segoe UI', Helvetica, Arial, sans-serif; color: #1e293b; padding: 30px; margin: 0; }
          .header { border-bottom: 3px solid #312e81; padding-bottom: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }
          .title { font-size: 22px; font-weight: 900; color: #312e81; margin: 0; }
          .subtitle { font-size: 13px; color: #64748b; margin-top: 4px; }
          .section { margin-bottom: 24px; }
          .section-title { font-size: 15px; font-weight: 800; color: #1e1b4b; border-bottom: 1px solid #cbd5e1; padding-bottom: 6px; margin-bottom: 12px; }
          .metric-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 18px; margin-bottom: 16px; display: flex; gap: 24px; }
          .metric { display: flex; flex-direction: column; }
          .metric-label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; }
          .metric-val { font-size: 20px; font-weight: 900; color: #4338ca; }
          table { width: 100%; border-collapse: collapse; margin-top: 12px; }
          th { background: #f1f5f9; text-align: left; padding: 8px 12px; font-size: 12px; font-weight: 800; color: #334155; border-bottom: 2px solid #cbd5e1; }
          td { padding: 10px 12px; font-size: 12px; border-bottom: 1px solid #e2e8f0; vertical-align: top; }
          .score-badge { font-weight: 800; color: #047857; background: #d1fae5; padding: 2px 8px; border-radius: 12px; font-size: 11px; }
          @media print {
            body { padding: 0; }
            .no-print { display: none; }
          }
        </style>
      </head>
      <body>
        <div class="header">
          <div>
            <h1 class="title">FLUENT ACADEMIC ENGLISH STUDIO</h1>
            <div class="subtitle">Official Student Evaluation Report &bull; Mode: ${reportTitle}</div>
          </div>
          <div style="text-align: right; font-size: 12px; color: #64748b;">
            <div>Date Range: ${rangeType.value.toUpperCase()}</div>
          </div>
        </div>

        <div class="metric-box">
          <div class="metric">
            <span class="metric-label">Total Practice Sessions</span>
            <span class="metric-val">${historyItems.value.length}</span>
          </div>
          <div class="metric">
            <span class="metric-label">Overall Average Score</span>
            <span class="metric-val">${historyItems.value.length ? (historyItems.value.reduce((acc, curr) => acc + (curr.score || 0), 0) / historyItems.value.length).toFixed(1) : '0.0'} / 10.0</span>
          </div>
        </div>
    `

    if (pdfExportMode.value === 'summary') {
      reportHtml += `
        <div class="section">
          <div class="section-title">Daily Summary Aggregates (${groupedHistory.value.length} Active Days)</div>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Total Sessions</th>
                <th>Daily Avg Score</th>
                <th>Primary Practice Topic</th>
              </tr>
            </thead>
            <tbody>
      `
      groupedHistory.value.forEach(group => {
        const avgScore = (group.items.reduce((acc, curr) => acc + (curr.score || 0), 0) / group.items.length).toFixed(1)
        const firstTopic = group.items[0] ? group.items[0].topic : 'General Practice'
        reportHtml += `
          <tr>
            <td><strong>${group.date}</strong></td>
            <td>${group.items.length} sessions</td>
            <td><span class="score-badge">${avgScore} / 10.0</span></td>
            <td>"${firstTopic}"</td>
          </tr>
        `
      })
      reportHtml += `
            </tbody>
          </table>
        </div>
      `
    } else {
      // Option B: Full Detailed Transcript PDF
      reportHtml += `
        <div class="section">
          <div class="section-title">Full Practice Transcripts (${historyItems.value.length} Detailed Sessions)</div>
          ${historyItems.value.map((item, idx) => `
            <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px 16px; margin-bottom: 12px;">
              <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 800; color: #334155; margin-bottom: 6px;">
                <span>Session #${historyItems.value.length - idx} &bull; ${item.timestamp || item.date}</span>
                <span class="score-badge">Score ${item.score}/10</span>
              </div>
              <div style="font-weight: 800; color: #312e81; font-size: 13px; margin-bottom: 4px;">Topic: "${item.topic}"</div>
              <div style="background: white; border: 1px solid #e2e8f0; padding: 8px 12px; border-radius: 6px; font-size: 12px; font-style: italic; margin-bottom: 8px; color: #1e293b;">
                Transcribed Speech: "${item.transcribed}"
              </div>
              ${item.ipa ? `<div style="font-family: monospace; font-size: 11px; color: #0f766e; background: #ccfbf1; border: 1px solid #99f6e4; padding: 6px 10px; border-radius: 6px; margin-bottom: 6px;">Target IPA: ${item.ipa.target_full_ipa || ''}<br>Spoken IPA: ${item.ipa.spoken_full_ipa || ''}</div>` : ''}
              ${item.feedback ? `<div style="font-size: 11px; color: #475569;"><strong>AI Feedback:</strong> ${item.feedback}</div>` : ''}
            </div>
          `).join('')}
        </div>
      `
    }
    reportHtml += `
      </body>
      </html>
    `

    const printWin = window.open('', '_blank')
    printWin.document.write(reportHtml)
    printWin.document.close()
    printWin.focus()
    setTimeout(() => {
      printWin.print()
    }, 500)

    showPdfDialog.value = false
  } catch (err) {
    console.error('PDF Generation Error:', err)
  } finally {
    isGeneratingPdf.value = false
  }
}

const downloadZipArchive = async () => {
  isExportingZip.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/history/export-zip`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: props.userId || 1,
        range_type: rangeType.value,
        start_date: customStartDate.value,
        end_date: customEndDate.value
      })
    })

    if (res.ok) {
      const blob = await res.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = `practice_history_${rangeType.value}.zip`
      document.body.appendChild(a)
      a.click()
      a.remove()
    }
  } catch (err) {
    console.error('ZIP export error:', err)
  } finally {
    isExportingZip.value = false
  }
}

onMounted(() => {
  fetchHistoryLogs()
  setTimeout(() => {
    runTour(TOUR_KEYS.STUDENT_HISTORY, STUDENT_HISTORY_TOUR_STEPS)
  }, 1000)
})

const replayHistoryTour = () => {
  runTour(TOUR_KEYS.STUDENT_HISTORY, STUDENT_HISTORY_TOUR_STEPS, true)
}
</script>

<style scoped>
.history-groups-container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
