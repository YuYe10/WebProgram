<script setup lang="ts">
import UiEmpty from '@/components/ui/UiEmpty.vue'
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-2">Archived</h1>
    <p class="text-sm text-gray-500 dark:text-gray-400 mb-8">View your archived notes and notebooks.</p>
    <UiEmpty
      icon="i-ph-archive-box"
      title="No archived items"
      description="Archive notes or notebooks to keep your workspace clean."
    />
  </div>
</template>
