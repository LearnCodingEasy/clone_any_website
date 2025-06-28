<template>
  <div class="file-tree">
    <!-- HTML File -->
    <div class="flex items-center justify-between py-2 px-3 hover:bg-gray-800 rounded">
      <div class="flex items-center space-x-3">
        <i class="pi pi-file text-blue-400"></i>
        <span class="text-white font-medium">index.html</span>
        <span class="text-gray-400 text-sm">({{ formatFileSize(html?.length || 0) }})</span>
      </div>
      <div class="flex space-x-2">
        <button
          @click="
            $emit('preview-file', { filename: 'index.html', content: html, is_binary: false })
          "
          class="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
        >
          <i class="pi pi-eye text-sm"></i>
        </button>
        <button
          @click="downloadHtml"
          class="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
        >
          <i class="pi pi-download text-sm"></i>
        </button>
      </div>
    </div>

    <!-- Organized Folders -->
    <div v-for="(folder, folderName) in organizedFiles" :key="folderName" class="mt-2">
      <div
        class="flex items-center justify-between py-2 px-3 hover:bg-gray-800 rounded cursor-pointer"
        @click="toggleFolder(folderName)"
      >
        <div class="flex items-center space-x-3">
          <i
            :class="expandedFolders[folderName] ? 'pi pi-folder-open' : 'pi pi-folder'"
            class="text-yellow-400"
          ></i>
          <span class="text-white font-medium">{{ folderName }}/</span>
          <span class="text-gray-400 text-sm">({{ folder.length }} files)</span>
        </div>
        <i
          :class="expandedFolders[folderName] ? 'pi pi-chevron-down' : 'pi pi-chevron-right'"
          class="text-gray-400"
        ></i>
      </div>

      <!-- Files in folder -->
      <div v-if="expandedFolders[folderName]" class="ml-6 border-l border-gray-700 pl-4">
        <div
          v-for="file in folder"
          :key="file.filename"
          class="flex items-center justify-between py-2 px-3 hover:bg-gray-800 rounded"
        >
          <div class="flex items-center space-x-3">
            <i :class="getFileIcon(file)" class="text-blue-400"></i>
            <span class="text-white">{{ file.filename }}</span>
            <span class="text-gray-400 text-sm">({{ formatFileSize(file.size) }})</span>
            <span v-if="file.error" class="text-red-400 text-xs">❌ Error</span>
            <span v-else-if="file.downloaded" class="text-green-400 text-xs">✅ Ready</span>
          </div>
          <div class="flex space-x-2">
            <button
              @click="$emit('preview-file', file)"
              class="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
            >
              <i class="pi pi-eye text-sm"></i>
            </button>
            <button
              @click="$emit('download-file', file)"
              class="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
            >
              <i class="pi pi-download text-sm"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  resources: {
    type: Array,
    default: () => [],
  },
  html: {
    type: String,
    default: '',
  },
})

defineEmits(['download-file', 'preview-file'])

const expandedFolders = ref({
  css: true,
  js: true,
  images: true,
  fonts: false,
  libraries: false,
  other: false,
})

const organizedFiles = computed(() => {
  const folders = {
    css: [],
    js: [],
    images: [],
    fonts: [],
    libraries: [],
    other: [],
  }

  props.resources?.forEach((resource) => {
    const category = resource.category
    if (category === 'javascript') {
      folders.js.push(resource)
    } else if (category === 'image') {
      folders.images.push(resource)
    } else if (category === 'font') {
      folders.fonts.push(resource)
    } else if (category === 'library') {
      folders.libraries.push(resource)
    } else if (category === 'css') {
      folders.css.push(resource)
    } else {
      folders.other.push(resource)
    }
  })

  // Remove empty folders
  Object.keys(folders).forEach((key) => {
    if (folders[key].length === 0) {
      delete folders[key]
    }
  })

  return folders
})

const toggleFolder = (folderName) => {
  expandedFolders.value[folderName] = !expandedFolders.value[folderName]
}

const getFileIcon = (file) => {
  const iconMap = {
    css: 'pi pi-palette',
    javascript: 'pi pi-cog',
    library: 'pi pi-cloud',
    image: 'pi pi-image',
    font: 'pi pi-font',
    other: 'pi pi-file',
  }
  return iconMap[file.category] || 'pi pi-file'
}

const downloadHtml = () => {
  const blob = new Blob([props.html], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'index.html'
  link.click()
  URL.revokeObjectURL(url)
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style scoped>
.file-tree {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}
</style>
