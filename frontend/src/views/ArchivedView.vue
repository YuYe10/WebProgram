<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { notesApi } from '@/api/notes'
import type { Note } from '@/types/note'
import UiEmpty from '@/components/ui/UiEmpty.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import NoteListItem from '@/components/note/NoteListItem.vue'
import { useUiStore } from '@/stores/ui'

const router = useRouter()
const ui = useUiStore()
const notes = ref<Note[]>([])
const isLoading = ref(true)

onMounted(async () => {
  isLoading.value = true
  try {
    const resp = await notesApi.getArchivedNotes({ size: 50 })
    notes.value = resp.items
  } catch {
    notes.value = []
  } finally {
    isLoading.value = false
  }
})

function goToNote(note: Note) {
  router.push({ name: 'note-edit', params: { notebookId: note.notebook_id, noteId: note.id } })
}

async function restoreNote(note: Note) {
  try {
    await notesApi.archive(note.id, false)
    notes.value = notes.value.filter(n => n.id !== note.id)
    ui.addToast({ type: 'success', message: 'Note restored' })
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to restore note' })
  }
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-2">Archived</h1>
    <p class="text-sm text-gray-500 dark:text-gray-400 mb-8">
      View and restore your archived notes.
    </p>

    <div v-if="isLoading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="glass-card p-4">
        <UiSkeleton width="60%" height="1.125rem" class="mb-2" />
        <UiSkeleton width="90%" height="0.875rem" />
      </div>
    </div>

    <div v-else-if="notes.length === 0" class="mt-16">
      <UiEmpty
        icon="i-ph-archive-box"
        title="No archived items"
        description="Archive notes to keep your workspace clean. They will appear here."
      />
    </div>

    <div v-else class="space-y-2">
      <NoteListItem
        v-for="note in notes"
        :key="note.id"
        :note="note"
        @click="goToNote(note)"
      >
        <template #actions>
          <button
            class="px-2 py-1 text-xs rounded-md text-brand-500 hover:bg-brand-50 dark:hover:bg-brand-900/30 transition-colors"
            @click.stop="restoreNote(note)"
          >
            Restore
          </button>
        </template>
      </NoteListItem>
    </div>
  </div>
</template>
