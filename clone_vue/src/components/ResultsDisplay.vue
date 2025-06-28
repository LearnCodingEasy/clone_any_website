<template>
  <prime_card class="glass-effect animate__animated animate__fadeInUp">
    <template #content>
      <div class="p-6">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
          <div>
            <h3 class="text-2xl font-semibold text-white mb-1">
              <i class="pi pi-code mr-2"></i>
              Scraped Results
            </h3>
            <p class="text-white/80 text-sm">From: {{ data.url }}</p>
          </div>
          <prime_button
            @click="$emit('clear')"
            class="p-2 bg-red-500/20 hover:bg-red-500/30 border-red-400/50 text-red-200"
            outlined
          >
            <i class="pi pi-times"></i>
          </prime_button>
        </div>

        <!-- Action Buttons -->
        <div class="flex flex-wrap gap-3 mb-6">
          <prime_button
            @click="copyToClipboard('html')"
            class="flex-1 min-w-[120px] bg-green-500/20 hover:bg-green-500/30 border-green-400/50 text-green-200"
            outlined
          >
            <i class="pi pi-copy mr-2"></i>
            Copy HTML
          </prime_button>
          <prime_button
            @click="copyToClipboard('css')"
            class="flex-1 min-w-[120px] bg-blue-500/20 hover:bg-blue-500/30 border-blue-400/50 text-blue-200"
            outlined
          >
            <i class="pi pi-copy mr-2"></i>
            Copy CSS
          </prime_button>
          <prime_button
            @click="downloadFiles"
            class="flex-1 min-w-[120px] bg-purple-500/20 hover:bg-purple-500/30 border-purple-400/50 text-purple-200"
            outlined
          >
            <i class="pi pi-download mr-2"></i>
            Download
          </prime_button>
        </div>

        <!-- Code Tabs -->
        <div class="space-y-4">
          <!-- Tab Navigation -->
          <div class="flex border-b border-white/20">
            <button
              @click="activeTab = 'html'"
              :class="{ 'border-white text-white': activeTab === 'html' }"
              class="px-4 py-2 border-b-2 border-transparent text-white/60 hover:text-white transition-colors"
            >
              <i class="pi pi-file-o mr-2"></i>
              HTML
            </button>
            <button
              @click="activeTab = 'css'"
              :class="{ 'border-white text-white': activeTab === 'css' }"
              class="px-4 py-2 border-b-2 border-transparent text-white/60 hover:text-white transition-colors"
            >
              <i class="pi pi-palette mr-2"></i>
              CSS
            </button>
          </div>

          <!-- Code Content -->
          <div class="relative">
            <CodeBlock :code="activeTab === 'html' ? data.html : data.css" :language="activeTab" />
          </div>
        </div>
      </div>
    </template>
  </prime_card>
</template>

<script setup>
import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import CodeBlock from './CodeBlock.vue'

const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
})

defineEmits(['clear'])

const toast = useToast()
const activeTab = ref('html')

const copyToClipboard = async (type) => {
  try {
    const content = type === 'html' ? props.data.html : props.data.css
    await navigator.clipboard.writeText(content)

    toast.add({
      severity: 'success',
      summary: 'Copied!',
      detail: `${type.toUpperCase()} copied to clipboard`,
      life: 2000,
    })
  } catch (error) {
    console.log('error: ', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to copy to clipboard',
      life: 3000,
    })
  }
}

const downloadFiles = () => {
  // Create HTML file
  const htmlBlob = new Blob([props.data.html], { type: 'text/html' })
  const htmlUrl = URL.createObjectURL(htmlBlob)

  // Create CSS file
  const cssBlob = new Blob([props.data.css], { type: 'text/css' })
  const cssUrl = URL.createObjectURL(cssBlob)

  // Download HTML
  const htmlLink = document.createElement('a')
  htmlLink.href = htmlUrl
  htmlLink.download = 'scraped-page.html'
  htmlLink.click()

  // Download CSS
  setTimeout(() => {
    const cssLink = document.createElement('a')
    cssLink.href = cssUrl
    cssLink.download = 'scraped-styles.css'
    cssLink.click()

    // Cleanup
    URL.revokeObjectURL(htmlUrl)
    URL.revokeObjectURL(cssUrl)
  }, 100)

  toast.add({
    severity: 'success',
    summary: 'Downloaded!',
    detail: 'Files downloaded successfully',
    life: 3000,
  })
}
</script>
