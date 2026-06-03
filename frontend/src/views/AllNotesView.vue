<script setup lang="ts">
import { onMounted } from 'vue'
import { useNotesStore } from '@/stores/notes'
import { useUiStore } from '@/stores/ui'
import UiEmpty from '@/components/ui/UiEmpty.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'

const notesStore = useNotesStore()
const ui = useUiStore()

onMounted(() => {
  // For "All Notes" we would need a backend endpoint.
  // For now, show a placeholder.
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-2">All Notes</h1>
    <p class="text-sm text-gray-500 dark:text-gray-400 mb-8">Browse all your notes across notebooks.</p>
    <UiEmpty
      icon="i-ph-note-pencil"
      title="Coming soon"
      description="Cross-notebook note browsing will be available in the next update."
    />
  </div>
</template>
