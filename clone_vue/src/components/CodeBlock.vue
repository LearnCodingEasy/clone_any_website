<template>
  <div class="relative">
    <!-- Copy Button -->
    <button
      @click="copyCode"
      class="absolute top-3 right-3 z-10 p-2 bg-black/50 hover:bg-black/70 rounded text-white/80 hover:text-white transition-colors"
      title="Copy code"
    >
      <i class="pi pi-copy text-sm"></i>
    </button>

    <!-- Code Container -->
    <div class="bg-gray-900 rounded-lg overflow-hidden">
      <div class="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <div class="flex items-center space-x-2">
          <div class="flex space-x-1">
            <div class="w-3 h-3 bg-red-500 rounded-full"></div>
            <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <div class="w-3 h-3 bg-green-500 rounded-full"></div>
          </div>
          <span class="text-gray-300 text-sm font-medium">
            {{ language.toUpperCase() }}
          </span>
        </div>
        <span class="text-gray-400 text-xs"> {{ lineCount }} lines </span>
      </div>

      <div class="p-4 overflow-x-auto max-h-96">
        <pre
          class="text-sm"
        ><code :class="`language-${language}`" v-html="highlightedCode"></code></pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useToast } from 'primevue/usetoast'

const props = defineProps({
  code: {
    type: String,
    required: true,
  },
  language: {
    type: String,
    default: 'html',
  },
})

const toast = useToast()

const lineCount = computed(() => {
  return props.code.split('\n').length
})

const highlightedCode = computed(() => {
  // Basic syntax highlighting (you can enhance this with a proper library like Prism.js)
  let highlighted = props.code

  if (props.language === 'html') {
    highlighted = highlighted
      .replace(/(&lt;\/?)([a-zA-Z][a-zA-Z0-9]*)/g, '$1<span class="text-blue-400">$2</span>')
      .replace(/(\s)([a-zA-Z-]+)(=)/g, '$1<span class="text-green-400">$2</span>$3')
      .replace(/(=")([^"]*?)(")/g, '=<span class="text-yellow-300">"$2"</span>')
      .replace(/(&lt;!--.*?--&gt;)/g, '<span class="text-gray-500">$1</span>')
  } else if (props.language === 'css') {
    highlighted = highlighted
      .replace(/([.#]?[a-zA-Z][a-zA-Z0-9-]*)\s*{/g, '<span class="text-blue-400">$1</span> {')
      .replace(/([a-zA-Z-]+)(\s*:)/g, '<span class="text-green-400">$1</span>$2')
      .replace(/(:\s*)([^;]+)(;)/g, ': <span class="text-yellow-300">$2</span>;')
      .replace(/(\/\*.*?\*\/)/g, '<span class="text-gray-500">$1</span>')
  }

  return highlighted
})

const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(props.code)
    toast.add({
      severity: 'success',
      summary: 'Copied!',
      detail: 'Code copied to clipboard',
      life: 2000,
    })
  } catch (error) {
    console.log('error: ', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to copy code',
      life: 3000,
    })
  }
}
</script>

<style scoped>
code {
  color: #e5e7eb;
  font-family: 'Fira Code', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace;
  line-height: 1.5;
}
</style>
