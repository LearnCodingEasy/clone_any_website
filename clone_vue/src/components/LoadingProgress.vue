<template>
  <div class="mt-6 animate__animated animate__fadeIn">
    <div class="text-center mb-4">
      <div class="relative inline-flex items-center justify-center w-20 h-20 mb-4">
        <div class="absolute inset-0 rounded-full border-4 border-white/20"></div>
        <div
          class="absolute inset-0 rounded-full border-4 border-white border-t-transparent animate-spin"
          :style="{ animationDuration: '1s' }"
        ></div>
        <i class="pi pi-cog text-white text-2xl animate-spin"></i>
      </div>

      <h3 class="text-white font-semibold text-lg mb-2">Processing Your Request</h3>
      <p class="text-white/80 text-sm">
        {{ currentStageText }}
      </p>
    </div>

    <!-- Progress Bar -->
    <div class="w-full bg-white/20 rounded-full h-2 mb-4">
      <div
        class="bg-gradient-to-r from-blue-400 to-purple-500 h-2 rounded-full transition-all duration-500 ease-out"
        :style="{ width: `${progressPercentage}%` }"
      ></div>
    </div>

    <!-- Stage Indicators -->
    <div class="flex justify-between text-xs text-white/60">
      <span
        v-for="(stageName, index) in stageNames"
        :key="index"
        :class="{ 'text-white font-semibold': index <= stage }"
        class="transition-all duration-300"
      >
        <i :class="index <= stage ? 'pi pi-check-circle' : 'pi pi-circle'" class="mr-1"></i>
        {{ stageName }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stage: {
    type: Number,
    default: 0,
  },
})

const stageNames = ['Init', 'Fetch', 'Parse', 'Extract', 'Process', 'Complete']

const stageTexts = [
  'Initializing scraper...',
  'Fetching website content...',
  'Parsing HTML structure...',
  'Extracting CSS styles...',
  'Processing and cleaning data...',
  'Finalizing results...',
]

const currentStageText = computed(() => {
  return stageTexts[props.stage] || stageTexts[0]
})

const progressPercentage = computed(() => {
  return Math.min(((props.stage + 1) / stageNames.length) * 100, 100)
})
</script>
