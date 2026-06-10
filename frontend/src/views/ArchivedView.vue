<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { notesApi } from '@/api/notes'
import type { Note } from '@/types/note'
import UiEmpty from '@/components/ui/UiEmpty.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiModal from '@/components/ui/UiModal.vue'
import NoteListItem from '@/components/note/NoteListItem.vue'
import { useUiStore } from '@/stores/ui'

const router = useRouter()
const ui = useUiStore()
const notes = ref<Note[]>([])
const isLoading = ref(true)
const total = ref(0)
const page = ref(1)
const pageSize = 20
const hasMore = ref(false)

// Delete confirmation
const showDeleteConfirm = ref(false)
const noteToDelete = ref<Note | null>(null)
const deleting = ref(false)

onMounted(() => {
  fetchArchived()
})

async function fetchArchived() {
  isLoading.value = true
  try {
    const resp = await notesApi.getArchivedNotes({ page: page.value, size: pageSize })
    notes.value = resp.items
    total.value = resp.total
    hasMore.value = resp.total > page.value * pageSize
  } catch {
    notes.value = []
  } finally {
    isLoading.value = false
  }
}

async function loadMore() {
  page.value++
  try {
    const resp = await notesApi.getArchivedNotes({ page: page.value, size: pageSize })
    notes.value.push(...resp.items)
    total.value = resp.total
    hasMore.value = notes.value.length < resp.total
  } catch {
    page.value--
  }
}

function goToNote(note: Note) {
  router.push({ name: 'note-edit', params: { notebookId: note.notebook_id, noteId: note.id } })
}

async function restoreNote(note: Note) {
  try {
    await notesApi.archive(note.id, false)
    notes.value = notes.value.filter(n => n.id !== note.id)
    total.value--
    ui.addToast({ type: 'success', message: 'Note restored' })
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to restore note' })
  }
}

function confirmDelete(note: Note) {
  noteToDelete.value = note
  showDeleteConfirm.value = true
}

async function deletePermanently() {
  if (!noteToDelete.value) return
  deleting.value = true
  try {
    await notesApi.delete(noteToDelete.value.id)
    notes.value = notes.value.filter(n => n.id !== noteToDelete.value!.id)
    total.value--
    showDeleteConfirm.value = false
    noteToDelete.value = null
    ui.addToast({ type: 'success', message: 'Note permanently deleted' })
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to delete note' })
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-2">
      <div>
        <h1 class="text-2xl font-bold">Archived</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          View and restore your archived notes.
        </p>
      </div>
    </div>

    <p v-if="!isLoading && notes.length > 0" class="text-sm text-gray-500 dark:text-gray-400 mb-6">
      {{ total }} archived {{ total === 1 ? 'note' : 'notes' }}
    </p>

    <!-- Loading -->
    <div v-if="isLoading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="glass-card p-4">
        <UiSkeleton width="60%" height="1.125rem" class="mb-2" />
        <UiSkeleton width="90%" height="0.875rem" />
      </div>
    </div>

    <!-- Empty -->
    <div v-else-if="notes.length === 0" class="mt-16">
      <UiEmpty
        icon="i-ph-archive-box"
        title="No archived items"
        description="Archive notes to keep your workspace clean. They will appear here."
      />
    </div>

    <!-- Note list -->
    <div v-else class="space-y-2">
      <NoteListItem
        v-for="note in notes"
        :key="note.id"
        :note="note"
        @click="goToNote(note)"
        @archive="restoreNote(note)"
        @delete="confirmDelete(note)"
      />

      <!-- Load more -->
      <div v-if="hasMore" class="flex justify-center pt-4">
        <UiButton variant="ghost" @click="loadMore">
          <span class="i-ph-arrow-down w-4 h-4" />
          Load more
        </UiButton>
      </div>
    </div>

    <!-- Delete confirmation modal -->
    <UiModal v-model:open="showDeleteConfirm" title="Delete Permanently" size="sm">
      <div class="flex flex-col gap-3">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          This will permanently delete <strong>"{{ noteToDelete?.title || 'Untitled' }}"</strong>.
          This action cannot be undone.
        </p>
      </div>
      <template #footer>
        <UiButton variant="ghost" @click="showDeleteConfirm = false">Cancel</UiButton>
        <UiButton variant="danger" :loading="deleting" @click="deletePermanently">
          Delete Permanently
        </UiButton>
      </template>
    </UiModal>
  </div>
</template>
