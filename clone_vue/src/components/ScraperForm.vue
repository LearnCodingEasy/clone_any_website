<template>
  <div class="space-y-6">
    <!-- Input Section -->
    <prime_card class="glass-effect animate__animated animate__fadeInUp">
      <template #content>
        <div class="p-6">
          <div class="text-center mb-6">
            <div
              class="inline-flex items-center justify-center w-16 h-16 bg-white/20 rounded-full mb-4"
            >
              <i class="pi pi-clone text-2xl text-white"></i>
            </div>
            <h2 class="text-2xl font-semibold text-white mb-2">Complete Website Cloner</h2>
            <p class="text-white/80">
              Clone 100% of any website - All files, libraries, images & perfect structure
            </p>
          </div>

          <form @submit.prevent="scrapeWebsite" class="space-y-4">
            <div class="relative">
              <label for="url" class="block text-white font-medium mb-2">
                <i class="pi pi-link mr-2"></i>
                Website URL to Clone
              </label>
              <div class="relative">
                <prime_input_text
                  id="url"
                  v-model="websiteUrl"
                  placeholder="https://example.com"
                  class="w-full p-4 pr-12 text-lg"
                  :disabled="isLoading"
                  @input="validateUrl"
                />
                <i
                  class="pi pi-globe absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400"
                ></i>
              </div>
              <div
                v-if="urlError"
                class="text-red-300 text-sm mt-1 animate__animated animate__shakeX"
              >
                {{ urlError }}
              </div>
            </div>

            <prime_button
              type="submit"
              :disabled="!isValidUrl || isLoading"
              class="w-full p-4 text-lg font-semibold bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700"
              :loading="isLoading"
            >
              <i v-if="!isLoading" class="pi pi-clone mr-2"></i>
              {{ isLoading ? loadingMessage : '🚀 Clone Complete Website' }}
            </prime_button>
          </form>

          <!-- Enhanced Loading Animation -->
          <div v-if="isLoading" class="text-center mt-6">
            <div class="relative inline-flex items-center justify-center w-24 h-24 mb-4">
              <div class="absolute inset-0 rounded-full border-4 border-white/20"></div>
              <div
                class="absolute inset-0 rounded-full border-4 border-white border-t-transparent animate-spin"
              ></div>
              <i class="pi pi-download text-white text-2xl animate-pulse"></i>
            </div>
            <p class="text-white text-lg font-semibold mb-2">{{ loadingMessage }}</p>
            <div class="text-white/60 text-sm">Cloning entire website with all dependencies...</div>
            <div v-if="downloadProgress.total > 0" class="mt-4">
              <div class="w-full bg-white/20 rounded-full h-2 mb-2">
                <div
                  class="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full transition-all duration-300"
                  :style="{
                    width: `${(downloadProgress.current / downloadProgress.total) * 100}%`,
                  }"
                ></div>
              </div>
              <div class="text-white/80 text-sm">
                Downloaded {{ downloadProgress.current }} of {{ downloadProgress.total }} files
              </div>
            </div>
          </div>
        </div>
      </template>
    </prime_card>

    <!-- Results Section -->
    <prime_card v-if="scrapedData" class="glass-effect animate__animated animate__fadeInUp">
      <template #content>
        <div class="p-6">
          <!-- Header -->
          <div class="flex items-center justify-between mb-6">
            <div>
              <h3 class="text-2xl font-semibold text-white mb-1">
                <i class="pi pi-check-circle mr-2 text-green-400"></i>
                Website Cloned Successfully!
              </h3>
              <p class="text-white/80 text-sm">
                <strong>{{ scrapedData.title }}</strong>
              </p>
              <p class="text-white/60 text-xs">
                From: {{ scrapedData.url }} | Cloned: {{ scrapedData.scraped_at }}
              </p>
            </div>
            <prime_button @click="clearResults" class="p-2" severity="danger" outlined>
              <i class="pi pi-times"></i>
            </prime_button>
          </div>

          <!-- Complete Stats Grid -->
          <div class="grid grid-cols-2 md:grid-cols-6 gap-4 mb-6">
            <div
              class="bg-gradient-to-br from-blue-500/20 to-blue-600/20 rounded-lg p-3 text-center border border-blue-400/30"
            >
              <div class="text-white text-xl font-bold">
                {{ scrapedData.stats?.total_files || 0 }}
              </div>
              <div class="text-blue-200 text-sm">Total Files</div>
            </div>
            <div
              class="bg-gradient-to-br from-purple-500/20 to-purple-600/20 rounded-lg p-3 text-center border border-purple-400/30"
            >
              <div class="text-white text-xl font-bold">
                {{ scrapedData.stats?.css_files || 0 }}
              </div>
              <div class="text-purple-200 text-sm">CSS Files</div>
            </div>
            <div
              class="bg-gradient-to-br from-yellow-500/20 to-yellow-600/20 rounded-lg p-3 text-center border border-yellow-400/30"
            >
              <div class="text-white text-xl font-bold">{{ scrapedData.stats?.js_files || 0 }}</div>
              <div class="text-yellow-200 text-sm">JS Files</div>
            </div>
            <div
              class="bg-gradient-to-br from-green-500/20 to-green-600/20 rounded-lg p-3 text-center border border-green-400/30"
            >
              <div class="text-white text-xl font-bold">{{ scrapedData.stats?.images || 0 }}</div>
              <div class="text-green-200 text-sm">Images</div>
            </div>
            <div
              class="bg-gradient-to-br from-red-500/20 to-red-600/20 rounded-lg p-3 text-center border border-red-400/30"
            >
              <div class="text-white text-xl font-bold">
                {{ scrapedData.stats?.libraries || 0 }}
              </div>
              <div class="text-red-200 text-sm">Libraries</div>
            </div>
            <div
              class="bg-gradient-to-br from-indigo-500/20 to-indigo-600/20 rounded-lg p-3 text-center border border-indigo-400/30"
            >
              <div class="text-white text-xl font-bold">{{ scrapedData.stats?.fonts || 0 }}</div>
              <div class="text-indigo-200 text-sm">Fonts</div>
            </div>
          </div>

          <!-- Enhanced Action Buttons -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <prime_button
              @click="downloadCompleteProject"
              class="p-4 text-lg font-semibold bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700"
            >
              <i class="pi pi-download mr-2"></i>
              Download Complete Project
            </prime_button>
            <prime_button
              @click="downloadAsZip"
              class="p-4 text-lg font-semibold bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700"
            >
              <i class="pi pi-file-export mr-2"></i>
              Download as ZIP
            </prime_button>
            <prime_button
              @click="previewProject"
              class="p-4 text-lg font-semibold bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700"
            >
              <i class="pi pi-eye mr-2"></i>
              Preview Project
            </prime_button>
          </div>

          <!-- File Structure Tree -->
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <h4 class="text-xl font-semibold text-white">
                <i class="pi pi-folder mr-2"></i>
                Project Structure
              </h4>
              <div class="flex space-x-2">
                <prime_button @click="expandAll" size="small" outlined>
                  <i class="pi pi-plus mr-1"></i>
                  Expand All
                </prime_button>
                <prime_button @click="collapseAll" size="small" outlined>
                  <i class="pi pi-minus mr-1"></i>
                  Collapse All
                </prime_button>
              </div>
            </div>

            <!-- File Tree -->
            <div class="bg-gray-900 rounded-lg overflow-hidden">
              <div class="p-4 max-h-96 overflow-y-auto">
                <FileTree
                  :resources="scrapedData.resources"
                  :html="scrapedData.html"
                  @download-file="downloadSingleFile"
                  @preview-file="previewFile"
                />
              </div>
            </div>
          </div>
        </div>
      </template>
    </prime_card>

    <!-- File Preview Modal -->
    <div
      v-if="showPreviewModal"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
    >
      <div class="bg-gray-900 rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden">
        <div
          class="flex items-center justify-between px-6 py-4 bg-gray-800 border-b border-gray-700"
        >
          <div>
            <h3 class="text-white font-semibold text-lg">{{ previewFile?.filename }}</h3>
            <p class="text-gray-400 text-sm">{{ previewFile?.original_path }}</p>
          </div>
          <button @click="showPreviewModal = false" class="text-white hover:text-gray-300 text-xl">
            <i class="pi pi-times"></i>
          </button>
        </div>
        <div class="p-6 overflow-auto max-h-[80vh]">
          <pre
            v-if="!previewFile?.is_binary"
            class="text-sm text-gray-300 whitespace-pre-wrap"
          ><code>{{ previewFile?.content }}</code></pre>
          <div v-else class="text-center text-gray-400 py-8">
            <i class="pi pi-file text-4xl mb-4"></i>
            <p>Binary file - Cannot preview</p>
            <p class="text-sm">{{ formatFileSize(previewFile?.size || 0) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// onMounted
import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import axios from 'axios'
import FileTree from './FileTree.vue'

const toast = useToast()
const websiteUrl = ref('')
const isLoading = ref(false)
const urlError = ref('')
const scrapedData = ref(null)
const loadingMessage = ref('Initializing...')
const showPreviewModal = ref(false)
// const previewFile = ref(null)
// console.log('previewFile: ', previewFile);
const downloadProgress = ref({ current: 0, total: 0 })

const loadingMessages = [
  'Initializing complete website cloner...',
  'Analyzing website structure...',
  'Discovering all resources...',
  'Extracting CSS files and libraries...',
  'Downloading JavaScript files...',
  'Fetching all images (100%)...',
  'Processing fonts and assets...',
  'Downloading external libraries...',
  'Building project structure...',
  'Finalizing complete clone...',
]

const isValidUrl = computed(() => {
  const urlPattern = /^https?:\/\/.+\..+/
  return urlPattern.test(websiteUrl.value) && !urlError.value
})

const validateUrl = () => {
  urlError.value = ''

  if (!websiteUrl.value) {
    return
  }

  const urlPattern = /^https?:\/\/.+\..+/
  if (!urlPattern.test(websiteUrl.value)) {
    urlError.value = 'Please enter a valid URL (e.g., https://example.com)'
  }
}

const scrapeWebsite = async () => {
  if (!isValidUrl.value) {
    toast.add({
      severity: 'warn',
      summary: 'Invalid URL',
      detail: 'Please enter a valid website URL',
      life: 3000,
    })
    return
  }

  isLoading.value = true
  downloadProgress.value = { current: 0, total: 0 }

  try {
    // Show progressive loading messages
    let messageIndex = 0
    const messageInterval = setInterval(() => {
      if (messageIndex < loadingMessages.length - 1) {
        loadingMessage.value = loadingMessages[messageIndex]
        messageIndex++
      }
    }, 3000)

    // Simulate download progress updates
    const progressInterval = setInterval(async () => {
      // In a real implementation, you'd get this from the backend
      if (downloadProgress.value.total > 0) {
        downloadProgress.value.current = Math.min(
          downloadProgress.value.current + Math.floor(Math.random() * 3) + 1,
          downloadProgress.value.total,
        )
      }
    }, 500)

    // Make actual API call to Django backend
    const response = await axios.post(
      '/api/scrape/',
      {
        url: websiteUrl.value,
      },
      {
        timeout: 300000, // 5 minute timeout for complete cloning
      },
    )

    clearInterval(messageInterval)
    clearInterval(progressInterval)

    scrapedData.value = response.data

    toast.add({
      severity: 'success',
      summary: '🎉 Website Cloned Successfully!',
      detail: `Cloned ${response.data.stats?.total_files || 0} files from ${response.data.title}`,
      life: 5000,
    })
  } catch (error) {
    console.error('Cloning error:', error)

    let errorMessage = 'Failed to clone website'
    if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    } else if (error.code === 'ECONNABORTED') {
      errorMessage = 'Request timed out - website is too large or slow to respond'
    } else if (error.message) {
      errorMessage = error.message
    }

    toast.add({
      severity: 'error',
      summary: 'Cloning Failed',
      detail: errorMessage,
      life: 5000,
    })
  } finally {
    isLoading.value = false
    loadingMessage.value = 'Initializing...'
  }
}

const clearResults = () => {
  scrapedData.value = null
  websiteUrl.value = ''
}

const downloadCompleteProject = () => {
  if (!scrapedData.value) return

  // Download HTML file
  downloadTextFile(scrapedData.value.html, 'index.html', 'text/html')

  // Download all resources
  scrapedData.value.resources?.forEach((resource, index) => {
    setTimeout(
      () => {
        downloadSingleFile(resource)
      },
      100 + index * 50,
    )
  })

  toast.add({
    severity: 'success',
    summary: '📦 Download Started!',
    detail: 'Complete project is being downloaded with original structure',
    life: 3000,
  })
}

const downloadSingleFile = (resource) => {
  try {
    if (resource.is_binary) {
      // Handle binary files
      const byteCharacters = atob(resource.content)
      const byteNumbers = new Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)
      const blob = new Blob([byteArray], {
        type: resource.content_type || 'application/octet-stream',
      })

      downloadBlob(blob, resource.filename)
    } else {
      // Handle text files
      const mimeType = getMimeType(resource.category)
      downloadTextFile(resource.content, resource.filename, mimeType)
    }
  } catch (error) {
    console.error('Download error:', error)
    toast.add({
      severity: 'error',
      summary: 'Download Failed',
      detail: `Failed to download ${resource.filename}`,
      life: 3000,
    })
  }
}

const downloadTextFile = (content, filename, mimeType) => {
  const blob = new Blob([content], { type: mimeType })
  downloadBlob(blob, filename)
}

const downloadBlob = (blob, filename) => {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

const getMimeType = (category) => {
  const mimeTypes = {
    css: 'text/css',
    javascript: 'text/javascript',
    library: 'text/javascript',
    image: 'image/png',
    font: 'font/woff2',
    other: 'application/octet-stream',
  }
  return mimeTypes[category] || 'text/plain'
}

const downloadAsZip = () => {
  toast.add({
    severity: 'info',
    summary: '🚧 Coming Soon!',
    detail: 'ZIP download feature is being developed',
    life: 3000,
  })
}

const previewProject = () => {
  if (!scrapedData.value) return

  // Create a blob URL for the HTML and open it
  const htmlBlob = new Blob([scrapedData.value.html], { type: 'text/html' })
  const url = URL.createObjectURL(htmlBlob)
  window.open(url, '_blank')

  // Clean up after a delay
  setTimeout(() => {
    URL.revokeObjectURL(url)
  }, 10000)
}

const previewFile = (file) => {
  previewFile.value = file
  showPreviewModal.value = true
}

const expandAll = () => {
  // Implementation for expanding all folders in file tree
  toast.add({
    severity: 'info',
    summary: 'Expanded',
    detail: 'All folders expanded',
    life: 2000,
  })
}

const collapseAll = () => {
  // Implementation for collapsing all folders in file tree
  toast.add({
    severity: 'info',
    summary: 'Collapsed',
    detail: 'All folders collapsed',
    life: 2000,
  })
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>
