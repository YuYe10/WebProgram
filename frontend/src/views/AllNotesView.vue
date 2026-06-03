<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { notesApi } from '@/api/notes'
import type { Note } from '@/types/note'
import UiEmpty from '@/components/ui/UiEmpty.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import NoteListItem from '@/components/note/NoteListItem.vue'

const router = useRouter()
const notes = ref<Note[]>([])
const isLoading = ref(true)
const total = ref(0)

onMounted(async () => {
  isLoading.value = true
  try {
    const resp = await notesApi.getAllNotes({ size: 50 })
    notes.value = resp.items
    total.value = resp.total
  } catch {
    notes.value = []
  } finally {
    isLoading.value = false
  }
})

function goToNote(note: Note) {
  router.push({ name: 'note-edit', params: { notebookId: note.notebook_id, noteId: note.id } })
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-2">All Notes</h1>
    <p class="text-sm text-gray-500 dark:text-gray-400 mb-8">
      Browse all your notes across notebooks.
    </p>

    <div v-if="isLoading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="glass-card p-4">
        <UiSkeleton width="60%" height="1.125rem" class="mb-2" />
        <UiSkeleton width="90%" height="0.875rem" />
      </div>
    </div>

    <div v-else-if="notes.length === 0" class="mt-16">
      <UiEmpty
        icon="i-ph-note-pencil"
        title="No notes yet"
        description="Create your first note in a notebook to get started."
      />
    </div>

    <div v-else class="space-y-2">
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">{{ total }} notes total</p>
      <NoteListItem
        v-for="note in notes"
        :key="note.id"
        :note="note"
        @click="goToNote(note)"
      />
    </div>
  </div>
</template>
