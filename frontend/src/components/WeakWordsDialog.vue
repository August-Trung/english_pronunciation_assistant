<template>
  <v-dialog v-model="dialog" max-width="500" scrollable>
    <v-card rounded="lg">
      <v-card-title class="d-flex align-center justify-space-between flex-nowrap bg-error text-white py-2 px-3">
        <div class="d-flex align-center ga-2 text-truncate mr-2">
          <v-icon color="white" size="small">mdi-target-variant</v-icon>
          <span class="text-subtitle-2 text-sm-subtitle-1 font-weight-black text-truncate">KHO TỪ CẦN CẢI THIỆN</span>
        </div>
        <v-btn icon="mdi-close" variant="text" size="small" color="white" class="flex-shrink-0" @click="dialog = false" />
      </v-card-title>

      <v-card-text class="pa-4">
        <div class="text-caption text-grey-darken-1 mb-3">
          Đây là các từ em đã đọc sai hoặc phát âm thiếu trong các bài trước. Bấm vào icon loa để nghe lại mẫu chuẩn và luyện phát âm nhé!
        </div>

        <div v-if="isLoading" class="text-center py-6">
          <v-progress-circular indeterminate color="error" size="32" />
        </div>

        <div v-else-if="weakWords.length === 0" class="text-center py-8 text-grey">
          <v-icon size="48" color="success" class="mb-2">mdi-check-circle-outline</v-icon>
          <div class="text-subtitle-2 font-weight-bold text-success">Tuyệt vời! Em không có từ phát âm sai nào!</div>
          <div class="text-caption">Hãy tiếp tục duy trì phong độ nhé!</div>
        </div>

        <v-list v-else class="pa-0 border rounded-lg">
          <v-list-item
            v-for="item in weakWords"
            :key="item.id"
            class="border-b py-2 px-3 d-flex align-center justify-space-between"
          >
            <div>
              <div class="text-subtitle-2 font-weight-black text-error text-capitalize">{{ item.word }}</div>
              <div class="text-caption text-grey">Đã sai: {{ item.mistake_count }} lần • Ngày gần nhất: {{ item.last_practiced }}</div>
            </div>

            <template #append>
              <v-btn
                icon="mdi-volume-high"
                color="primary"
                variant="tonal"
                size="small"
                title="Nghe phát âm chuẩn"
                @click="speak(item.word)"
              />
            </template>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  backendUrl: String,
  userId: Number
})

const emit = defineEmits(['update:modelValue'])

const dialog = ref(props.modelValue)
const weakWords = ref([])
const isLoading = ref(false)

watch(() => props.modelValue, (val) => {
  dialog.value = val
  if (val && props.userId) {
    fetchWeakWords()
  }
})

watch(dialog, (val) => {
  emit('update:modelValue', val)
})

const fetchWeakWords = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${props.backendUrl}/api/users/${props.userId}/weak-words`)
    if (res.ok) {
      weakWords.value = await res.json()
    }
  } catch (err) {
    console.error('Error fetching weak words:', err)
  } finally {
    isLoading.value = false
  }
}

const speak = (text) => {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'en-US'
    utterance.rate = 0.9
    window.speechSynthesis.speak(utterance)
  }
}
</script>
