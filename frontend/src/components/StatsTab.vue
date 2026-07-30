<template>
  <v-container fluid class="pa-0">
    <div v-if="!history || history.length === 0" class="d-flex flex-column align-center justify-center py-12 text-grey-darken-1">
      <v-icon size="48" color="grey-lighten-2" class="mb-2">mdi-chart-box-outline</v-icon>
      <div class="text-subtitle-2 font-weight-bold text-grey">No Analytics Data Available Yet</div>
      <div class="text-caption text-center px-6">Complete a few speaking practices to accumulate your progress data!</div>
    </div>

    <div v-else>
      <div class="d-flex align-center justify-space-between mb-3 flex-wrap ga-2">
        <div class="text-subtitle-1 font-weight-black text-teal-darken-4">AI Progress Analytics Report</div>
        <v-btn
          color="teal"
          variant="tonal"
          size="small"
          class="text-none"
          prepend-icon="mdi-file-pdf-box"
          @click="showPdfReport = true"
        >
          Export Progress PDF
        </v-btn>
      </div>

      <!-- Streak Badge -->
      <v-card v-if="streak > 0" border flat class="mb-4 pa-3 text-center bg-info text-white" rounded="lg">
        <div class="text-subtitle-2 font-weight-black d-flex align-center justify-center ga-1">
          <v-icon color="amber">mdi-fire</v-icon>
          Outstanding! You have maintained a {{ streak }}-day learning streak!
        </div>
      </v-card>

      <!-- Overview Cards -->
      <v-row class="ma-0 mb-4 ga-2">
        <v-col v-for="stat in overviewStats" :key="stat.title" cols="6" sm="3" class="pa-1">
          <v-card border flat class="pa-3 text-center bg-white" rounded="lg">
            <v-icon :color="stat.color" size="large" class="mb-1">{{ stat.icon }}</v-icon>
            <div class="text-caption text-grey-darken-2 font-weight-bold">{{ stat.title }}</div>
            <div class="text-h6 font-weight-black mt-1" :class="`text-${stat.color}`">{{ stat.value }}</div>
          </v-card>
        </v-col>
      </v-row>

      <!-- SVG Charts -->
      <v-row class="ma-0 mb-4 ga-2">
        <!-- Chart 1: Progress (Line) -->
        <v-col cols="12" md="6" class="pa-1">
          <v-card border flat class="pa-3 bg-white" rounded="lg">
            <div class="text-subtitle-2 font-weight-black text-secondary mb-2 d-flex align-center ga-1">
              <v-icon color="secondary" size="small">mdi-chart-line</v-icon>
              <span>Recent Pronunciation Performance Line</span>
            </div>
            
            <div style="height: 180px;" class="position-relative">
              <svg viewBox="0 0 500 200" width="100%" height="100%" style="background-color: transparent; user-select: none;">
                <defs>
                  <linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#03A9F4" stop-opacity="0.3"/>
                    <stop offset="100%" stop-color="#03A9F4" stop-opacity="0.0"/>
                  </linearGradient>
                </defs>

                <line x1="40" y1="25" x2="480" y2="25" stroke="#E0E0E0" stroke-dasharray="3,3" />
                <text x="30" y="30" font-size="10" fill="#757575" text-anchor="end">10</text>
                
                <line x1="40" y1="95" x2="480" y2="95" stroke="#E0E0E0" stroke-dasharray="3,3" />
                <text x="30" y="100" font-size="10" fill="#757575" text-anchor="end">5</text>
                
                <line x1="40" y1="165" x2="480" y2="165" stroke="#757575" />
                <text x="30" y="170" font-size="10" fill="#757575" text-anchor="end">0</text>

                <line x1="40" y1="53" x2="480" y2="53" stroke="#4CAF50" stroke-width="1" stroke-dasharray="4,4" opacity="0.7" />
                <text x="475" y="48" font-size="8" fill="#4CAF50" font-weight="bold" text-anchor="end">Target Goal (8.0)</text>

                <path :d="linePathD" fill="url(#lineGrad)" />
                <path :d="linePathLineD" fill="none" stroke="#03A9F4" stroke-width="3" stroke-linecap="round" />

                <circle
                  v-for="(pt, idx) in linePoints"
                  :key="idx"
                  :cx="pt.x"
                  :cy="pt.y"
                  r="5"
                  fill="#FFFFFF"
                  stroke="#1976D2"
                  stroke-width="2"
                  style="cursor: pointer; transition: r 0.2s ease, fill 0.2s ease;"
                  onmouseover="this.setAttribute('r', '7'); this.setAttribute('fill', '#FF9800');"
                  onmouseout="this.setAttribute('r', '5'); this.setAttribute('fill', '#FFFFFF');"
                >
                  <title>Attempt {{ idx + 1 }}: {{ pt.score.toFixed(1) }} pts ({{ pt.date }})</title>
                </circle>
              </svg>
            </div>
            <div class="text-caption text-center text-grey mt-1">Your speaking performances ordered from oldest to latest</div>
          </v-card>
        </v-col>

        <!-- Chart 2: 7 Days Activity (Bar) -->
        <v-col cols="12" md="6" class="pa-1">
          <v-card border flat class="pa-3 bg-white" rounded="lg">
            <div class="text-subtitle-2 font-weight-black text-secondary mb-2 d-flex align-center ga-1">
              <v-icon color="secondary" size="small">mdi-calendar-range</v-icon>
              <span>7-Day Practice Frequency</span>
            </div>

            <div style="height: 180px;" class="position-relative">
              <svg viewBox="0 0 500 200" width="100%" height="100%" style="background-color: transparent; user-select: none;">
                <line x1="40" y1="25" x2="480" y2="25" stroke="#E0E0E0" stroke-dasharray="3,3" />
                <line x1="40" y1="95" x2="480" y2="95" stroke="#E0E0E0" stroke-dasharray="3,3" />
                <line x1="40" y1="165" x2="480" y2="165" stroke="#757575" />

                <g v-for="(bar, idx) in barData" :key="idx">
                  <rect
                    :x="bar.x - 12"
                    y="25"
                    width="24"
                    height="140"
                    fill="#F5F5F5"
                    rx="4"
                  />
                  <rect
                    v-if="bar.value > 0"
                    :x="bar.x - 12"
                    :y="bar.y"
                    width="24"
                    :height="165 - bar.y"
                    fill="#4CAF50"
                    rx="4"
                    style="cursor: pointer; transition: fill 0.2s ease;"
                    onmouseover="this.setAttribute('fill', '#81C784');"
                    onmouseout="this.setAttribute('fill', '#4CAF50');"
                  >
                    <title>{{ bar.fullDate }}: Practiced {{ bar.value }} times</title>
                  </rect>
                  <text :x="bar.x" y="182" font-size="9" fill="#757575" text-anchor="middle">{{ bar.label }}</text>
                  <text v-if="bar.value > 0" :x="bar.x" :y="bar.y - 5" font-size="9" font-weight="bold" fill="#388E3C" text-anchor="middle">{{ bar.value }}</text>
                </g>
              </svg>
            </div>
            <div class="text-caption text-center text-grey mt-1">Daily recorded speaking practice sessions</div>
          </v-card>
        </v-col>
      </v-row>

      <!-- Score Distribution -->
      <div class="text-subtitle-2 font-weight-black text-secondary mb-2 d-flex align-center ga-1">
        <v-icon color="secondary" size="small">mdi-chart-pie</v-icon>
        <span>Score Distribution Breakdown</span>
      </div>
      <v-row class="ma-0 mb-4 ga-2">
        <v-col v-for="dist in scoreDistributions" :key="dist.title" cols="6" sm="3" class="pa-1">
          <v-card
            border
            flat
            class="pa-3 bg-white h-100 d-flex flex-column justify-space-between"
            :style="{ borderTop: '4px solid ' + dist.color, borderRadius: '10px' }"
          >
            <div class="d-flex align-center justify-space-between mb-2 ga-1">
              <div class="d-flex align-center ga-1 text-truncate">
                <v-icon :color="dist.iconColor" size="small" class="flex-shrink-0">{{ dist.icon }}</v-icon>
                <span class="text-caption font-weight-black text-grey-darken-3 text-truncate">{{ dist.title }}</span>
              </div>
              <span class="text-caption font-weight-bold text-grey-darken-2 bg-grey-lighten-4 px-1.5 py-0.5 rounded-pill text-no-wrap flex-shrink-0" style="font-size: 11px;">
                {{ dist.range }}
              </span>
            </div>
            <div class="d-flex align-baseline ga-1">
              <span class="text-h5 font-weight-black" :style="{ color: dist.color }">{{ dist.count }}</span>
              <span class="text-caption font-weight-bold text-grey-darken-1">times</span>
              <span class="text-caption text-grey font-weight-bold ml-auto">({{ dist.percent }}%)</span>
            </div>
          </v-card>
        </v-col>
      </v-row>

      <!-- History List -->
      <div class="text-subtitle-2 font-weight-black text-secondary mb-2 d-flex align-center ga-1">
        <v-icon color="secondary" size="small">mdi-history</v-icon>
        <span>Recent Speaking History (Top 10)</span>
      </div>
      <v-expansion-panels variant="accordion" class="border elevation-0 mb-4" rounded="lg">
        <v-expansion-panel
          v-for="(item, idx) in recentHistory"
          :key="idx"
          elevation="0"
        >
          <v-expansion-panel-title class="py-2 px-3">
            <v-row class="ma-0 w-100" align="center" no-gutters>
              <v-col cols="8" class="text-truncate">
                <span class="text-caption text-grey mr-2">{{ item.timestamp.split(' ')[0] }}</span>
                <span class="font-weight-bold text-subtitle-2">{{ item.topic }}</span>
              </v-col>
              <v-col cols="4" class="text-right">
                <v-chip :color="getScoreColor(item.score)" size="small" class="font-weight-black">
                  {{ item.score.toFixed(1) }}/10
                </v-chip>
              </v-col>
            </v-row>
          </v-expansion-panel-title>
          <v-expansion-panel-text class="bg-grey-lighten-5 pa-1">
            <v-row class="ma-0 ga-2 mb-2">
              <v-col cols="12" class="pa-1">
                <span class="text-caption font-weight-bold text-secondary d-flex align-center ga-1 mb-1">
                  <v-icon size="x-small">mdi-comment-text-outline</v-icon>
                  <span>Transcribed Spoken Text:</span>
                </span>
                <div class="pa-2 bg-white rounded border text-body-2 font-italic">
                  "{{ item.transcribed }}"
                </div>
              </v-col>
              <v-col cols="12" class="pa-1">
                <span class="text-caption font-weight-bold text-secondary d-flex align-center ga-1 mb-1">
                  <v-icon size="x-small">mdi-message-text-outline</v-icon>
                  <span>Pedagogical Feedback:</span>
                </span>
                <div class="text-caption text-grey-darken-3 bg-white pa-2 rounded border" v-html="renderHistoryFeedback(item.feedback)" />
              </v-col>
            </v-row>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

      <!-- Action Buttons -->
      <v-card border flat class="pa-3 bg-white" rounded="lg">
        <div class="text-subtitle-2 font-weight-bold text-secondary mb-2 d-flex align-center ga-1">
          <v-icon color="secondary" size="small">mdi-database-outline</v-icon>
          <span>Learning Data Management</span>
        </div>
        <v-row class="ma-0 ga-2">
          <v-col cols="12" sm="4" class="pa-1">
            <v-btn
              color="primary"
              variant="outlined"
              block
              density="comfortable"
              prepend-icon="mdi-download"
              class="font-weight-bold text-caption text-sm-body-2"
              @click="downloadCSV"
            >
              Export History (CSV)
            </v-btn>
          </v-col>
          <v-col cols="12" sm="4" class="pa-1">
            <v-btn
              color="secondary"
              variant="outlined"
              block
              density="comfortable"
              prepend-icon="mdi-export"
              class="font-weight-bold text-caption text-sm-body-2"
              @click="downloadJSON"
            >
              Backup Data (JSON)
            </v-btn>
          </v-col>
          <v-col cols="12" sm="4" class="pa-1">
            <v-btn
              color="error"
              variant="outlined"
              block
              density="comfortable"
              prepend-icon="mdi-trash-can-outline"
              class="font-weight-bold text-caption text-sm-body-2"
              @click="confirmClearHistory"
            >
              {{ isConfirmingClear ? 'Click again to confirm!' : 'Clear Practice History' }}
            </v-btn>
          </v-col>
        </v-row>
      </v-card>
    </div>

    <!-- PDF Report Dialog -->
    <PdfReportDialog v-model="showPdfReport" :streak="streak" />
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import PdfReportDialog from '@/components/PdfReportDialog.vue'

const showPdfReport = ref(false)

const props = defineProps({
  history: {
    type: Array,
    required: true
  },
  dailyGoal: {
    type: Number,
    default: 5
  }
})

const emit = defineEmits(['clear-history'])

const isConfirmingClear = ref(false)
let clearTimer = null

const safeHistory = computed(() => {
  if (!props.history) return []
  if (Array.isArray(props.history)) return props.history
  if (typeof props.history === 'object' && Array.isArray(props.history.history)) return props.history.history
  return []
})

const streak = computed(() => {
  const list = safeHistory.value
  if (list.length === 0) return 0
  const uniqueDates = [...new Set(list.map(item => item.date))].sort((a, b) => new Date(b) - new Date(a))
  
  if (uniqueDates.length === 0) return 0
  
  const todayStr = new Date().toISOString().split('T')[0]
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  const yesterdayStr = yesterday.toISOString().split('T')[0]
  
  if (uniqueDates[0] !== todayStr && uniqueDates[0] !== yesterdayStr) {
    return 0
  }
  
  let currentStreak = 1
  for (let i = 0; i < uniqueDates.length - 1; i++) {
    const cur = new Date(uniqueDates[i])
    const prev = new Date(uniqueDates[i + 1])
    const diffDays = Math.round((cur - prev) / (1000 * 60 * 60 * 24))
    
    if (diffDays === 1) {
      currentStreak++
    } else if (diffDays > 1) {
      break
    }
  }
  return currentStreak
})

const overviewStats = computed(() => {
  const list = safeHistory.value
  if (list.length === 0) return []
  
  const total = list.length
  const avg = list.reduce((sum, item) => sum + (item.score || 0), 0) / total
  const best = Math.max(...list.map(item => item.score || 0))
  const todayStr = new Date().toISOString().split('T')[0]
  const todayCount = list.filter(item => item.date === todayStr).length
  
  return [
    { title: 'Total Practices', value: `${total} sessions`, icon: 'mdi-microphone-outline', color: 'primary' },
    { title: 'Average Score', value: `${avg.toFixed(1)}/10`, icon: 'mdi-star-outline', color: 'success' },
    { title: 'Highest Score', value: `${best.toFixed(1)}/10`, icon: 'mdi-trophy-outline', color: 'warning' },
    { title: 'Today Goal', value: `${todayCount}/${props.dailyGoal}`, icon: 'mdi-calendar-check-outline', color: 'info' }
  ]
})

const scoreDistributions = computed(() => {
  const list = safeHistory.value
  if (list.length === 0) return []
  
  const total = list.length
  const counts = { excellent: 0, good: 0, ok: 0, poor: 0 }
  
  list.forEach(item => {
    if (item.score >= 8) counts.excellent++
    else if (item.score >= 6) counts.good++
    else if (item.score >= 4) counts.ok++
    else counts.poor++
  })
  
  const pct = (val) => total > 0 ? Math.round((val / total) * 100) : 0
  
  return [
    { title: 'Excellent', range: '≥ 8.0', count: counts.excellent, percent: pct(counts.excellent), color: '#4CAF50', icon: 'mdi-emoticon-excited-outline', iconColor: 'success' },
    { title: 'Proficient', range: '6.0-7.9', count: counts.good, percent: pct(counts.good), color: '#FFB300', icon: 'mdi-emoticon-happy-outline', iconColor: 'warning' },
    { title: 'Developing', range: '4.0-5.9', count: counts.ok, percent: pct(counts.ok), color: '#FF9800', icon: 'mdi-emoticon-neutral-outline', iconColor: 'orange' },
    { title: 'Needs Practice', range: '< 4.0', count: counts.poor, percent: pct(counts.poor), color: '#F44336', icon: 'mdi-emoticon-sad-outline', iconColor: 'error' }
  ]
})

const recentHistory = computed(() => {
  return [...safeHistory.value].reverse().slice(0, 10)
})

const linePoints = computed(() => {
  const list = safeHistory.value
  if (list.length === 0) return []
  const data = list.slice(-10)
  const total = data.length
  
  return data.map((item, idx) => {
    const x = total > 1 ? 50 + (idx / (total - 1)) * 400 : 250
    const y = 165 - ((item.score || 0) / 10) * 140
    let label = ''
    try {
      const parts = item.timestamp.split(' ')
      if (parts[0]) {
        const dateParts = parts[0].split('/')
        label = `${dateParts[0]}/${dateParts[1]}`
      }
    } catch {
      label = item.date
    }
    return { x, y, score: item.score, date: label }
  })
})

const linePathD = computed(() => {
  const pts = linePoints.value
  if (pts.length === 0) return ''
  if (pts.length === 1) return `M 250 165 L 250 ${pts[0].y} L 250 165 Z`
  
  let path = `M ${pts[0].x} 165`
  pts.forEach(p => {
    path += ` L ${p.x} ${p.y}`
  })
  path += ` L ${pts[pts.length - 1].x} 165 Z`
  return path
})

const linePathLineD = computed(() => {
  const pts = linePoints.value
  if (pts.length === 0) return ''
  if (pts.length === 1) return `M 245 ${pts[0].y} L 255 ${pts[0].y}`
  
  let path = `M ${pts[0].x} ${pts[0].y}`
  for (let i = 1; i < pts.length; i++) {
    path += ` L ${pts[i].x} ${pts[i].y}`
  }
  return path
})

const barData = computed(() => {
  const list = safeHistory.value
  const result = []
  const today = new Date()
  
  for (let i = 6; i >= 0; i--) {
    const d = new Date()
    d.setDate(today.getDate() - i)
    const dStr = d.toISOString().split('T')[0]
    const count = list.filter(item => item.date === dStr).length
    
    const x = 60 + ((6 - i) / 6) * 380
    const maxVal = Math.max(8, ...result.map(r => r.value), count)
    const y = 165 - (count / maxVal) * 140
    const label = `${d.getDate()}/${d.getMonth() + 1}`
    
    result.push({
      x,
      y,
      value: count,
      label,
      fullDate: dStr
    })
  }
  return result
})

const getScoreColor = (score) => {
  if (score >= 8) return 'success'
  if (score >= 6) return 'warning'
  if (score >= 4) return 'orange'
  return 'error'
}

const renderHistoryFeedback = (feedback) => {
  if (!feedback) return ''
  let raw = feedback
  raw = raw.replace(/\n/g, '<br>')
  raw = raw.replace(/### (.*?)(<br>|$)/g, '<div class="font-weight-bold text-secondary mt-1 mb-1">$1</div>')
  raw = raw.replace(/\*\*(.*?)\*\*/g, '<strong class="text-secondary">$1</strong>')
  raw = raw.replace(/- (.*?)(<br>|$)/g, '<div class="pl-2 d-flex align-center"><i class="mdi mdi-circle-small text-primary mr-1"></i><span>$1</span></div>')
  return raw
}

const downloadCSV = () => {
  const list = safeHistory.value
  if (list.length === 0) return
  
  const headers = ['Timestamp', 'Date', 'Topic', 'Transcribed Text', 'Score', 'Pronunciation', 'Fluency', 'Grammar', 'Vocabulary', 'Communication']
  const rows = list.map(item => [
    item.timestamp,
    item.date,
    `"${(item.topic || '').replace(/"/g, '""')}"`,
    `"${(item.transcribed || '').replace(/"/g, '""')}"`,
    item.score,
    item.breakdown?.Pronunciation || 0,
    item.breakdown?.Fluency || 0,
    item.breakdown?.Grammar || 0,
    item.breakdown?.Vocabulary || 0,
    item.breakdown?.Communication || 0
  ])
  
  const csvContent = "data:text/csv;charset=utf-8,\uFEFF" 
    + [headers.join(','), ...rows.map(e => e.join(','))].join('\n')
  
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement("a")
  link.setAttribute("href", encodedUri)
  link.setAttribute("download", `speaking_history_${new Date().toISOString().split('T')[0]}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const downloadJSON = () => {
  const list = safeHistory.value
  if (list.length === 0) return
  const data = {
    exportDate: new Date().toLocaleString('vi-VN'),
    history: list
  }
  const sJson = JSON.stringify(data, null, 2)
  const blob = new Blob([sJson], { type: "application/json" })
  const url = URL.createObjectURL(blob)
  
  const link = document.createElement("a")
  link.setAttribute("href", url)
  link.setAttribute("download", `backup_speaking_${new Date().toISOString().split('T')[0]}.json`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const confirmClearHistory = () => {
  if (isConfirmingClear.value) {
    emit('clear-history')
    isConfirmingClear.value = false
    clearTimeout(clearTimer)
  } else {
    isConfirmingClear.value = true
    clearTimer = setTimeout(() => {
      isConfirmingClear.value = false
    }, 4000)
  }
}
</script>
