<template>
  <div id="app" class="min-h-screen py-8">
    <div class="container mx-auto px-4">
      <header class="text-center mb-8 animate__animated animate__fadeInDown">
        <h1 class="text-4xl font-bold text-white mb-2">🎯 Website Scraper Tool</h1>
        <p class="text-white/80 text-lg">Extract HTML & CSS from any public website</p>
      </header>
      <main class="max-w-4xl mx-auto">
        <ScraperForm />
      </main>
    </div>
    <prime_toast />
  </div>
</template>

<script setup>
import ScraperForm from './components/ScraperForm.vue'
</script>
