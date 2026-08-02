<template>
  <v-container fluid class="pa-0">
    <!-- Header Banner -->
    <v-card flat border class="pa-4 pa-md-6 mb-4 bg-white" rounded="lg">
      <div class="d-flex flex-column flex-md-row align-start align-md-center justify-space-between ga-3">
        <div class="d-flex align-center ga-3">
          <v-avatar color="indigo-lighten-5" size="48" class="text-indigo border">
            <v-icon size="28">mdi-history</v-icon>
          </v-avatar>
          <div>
            <h1 class="text-h6 font-weight-black text-indigo-darken-3 tracking-tight">
              Student Practice History & Evaluation Logs
            </h1>
            <p class="text-caption font-weight-medium text-grey-darken-1 mb-0">
              Review your past audio recordings, 5-skill AI scores, IPA phonetic alignment, and export reports.
            </p>
          </div>
        </div>

        <!-- Export Actions -->
        <div class="d-flex align-center ga-2 flex-wrap">
          <v-btn
            color="secondary"
            variant="outlined"
            size="small"
            class="text-none font-weight-bold"
            prepend-icon="mdi-file-pdf-box"
            :loading="isExportingPdf"
            @click="exportPdfReport"
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
    <v-card flat border class="pa-3 mb-4 bg-grey-lighten-5" rounded="lg">
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
        <div class="d-flex align-center ga-2 mb-3">
          <v-chip color="indigo" variant="flat" size="small" class="font-weight-black" prepend-icon="mdi-calendar-check">
            {{ group.date }}
          </v-chip>
          <span class="text-caption font-weight-bold text-grey-darken-2">
            ({{ group.items.length }} session{{ group.items.length > 1 ? 's' : '' }})
          </span>
          <v-divider class="flex-grow-1" />
        </div>

        <!-- Sessions List for this Date -->
        <v-row>
          <v-col v-for="item in group.items" :key="item.id" cols="12" md="6">
            <v-card flat border rounded="lg" class="pa-4 bg-white h-100 d-flex flex-column justify-space-between">
              <div>
                <!-- Top metadata: Time & Topic -->
                <div class="d-flex align-center justify-space-between ga-2 mb-2">
                  <div class="text-caption font-weight-bold text-grey-darken-1 d-flex align-center ga-1">
                    <v-icon size="x-small">mdi-clock-outline</v-icon>
                    <span>{{ item.time }}</span>
                  </div>
                  <v-chip
                    :color="item.score >= 8 ? 'success' : item.score >= 6 ? 'warning' : 'error'"
                    size="x-small"
                    variant="flat"
                    class="font-weight-black"
                  >
                    Score {{ item.score }}/10
                  </v-chip>
                </div>

                <div class="text-subtitle-2 font-weight-black text-indigo-darken-3 mb-2">
                  Topic: "{{ item.topic }}"
                </div>

                <!-- Transcribed Text -->
                <div class="bg-grey-lighten-4 pa-2.5 rounded border mb-3 text-caption font-weight-medium">
                  <span class="text-grey-darken-2 font-weight-bold">Transcribed Speech:</span>
                  <div class="text-grey-darken-4 mt-0.5 font-italic">"{{ item.transcribed }}"</div>
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
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  backendUrl: {
    type: String,
    required: true
  },
  userId: {
    type: Number,
    default: 1
  }
})

const isLoading = ref(false)
const isExportingPdf = ref(false)
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

const exportPdfReport = async () => {
  isExportingPdf.value = true
  try {
    window.print()
  } catch (err) {
    console.error('PDF export error:', err)
  } finally {
    isExportingPdf.value = false
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
})
</script>

<style scoped>
.history-groups-container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
