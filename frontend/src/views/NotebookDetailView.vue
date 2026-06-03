<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotebooksStore } from '@/stores/notebooks'
import { useNotesStore } from '@/stores/notes'
import { useUiStore } from '@/stores/ui'
import { notebooksApi } from '@/api/notebooks'
import UiButton from '@/components/ui/UiButton.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiEmpty from '@/components/ui/UiEmpty.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import NoteListItem from '@/components/note/NoteListItem.vue'
import { format } from 'date-fns'

const route = useRoute()
const router = useRouter()
const notebooksStore = useNotebooksStore()
const notesStore = useNotesStore()
const ui = useUiStore()

const notebookId = computed(() => route.params.id as string)
const notebook = ref(notebooksStore.notebooks.find(n => n.id === notebookId.value) || null)
const showEditModal = ref(false)
const showDeleteConfirm = ref(false)
const editName = ref('')
const editDescription = ref('')
const newNoteTitle = ref('')

onMounted(async () => {
  if (!notebook.value) {
    try {
      notebook.value = await notebooksApi.getById(notebookId.value)
    } catch {
      router.push('/')
      return
    }
  }
  notebooksStore.setActiveNotebook(notebook.value)
  await notesStore.fetchNotes(notebookId.value)
})

async function updateNotebook() {
  if (!editName.value.trim()) return
  await notebooksStore.updateNotebook(notebookId.value, {
    name: editName.value.trim(),
    description: editDescription.value.trim() || undefined,
  })
  notebook.value = notebooksStore.notebooks.find(n => n.id === notebookId.value) || null
  showEditModal.value = false
  ui.addToast({ type: 'success', message: 'Notebook updated' })
}

async function deleteNotebook() {
  await notebooksStore.deleteNotebook(notebookId.value)
  ui.addToast({ type: 'success', message: 'Notebook deleted' })
  router.push('/')
}

async function createNote() {
  if (!newNoteTitle.value.trim()) return
  const note = await notesStore.createNote(notebookId.value, {
    title: newNoteTitle.value.trim(),
  })
  newNoteTitle.value = ''
  router.push({ name: 'note-edit', params: { notebookId: notebookId.value, noteId: note.id } })
}

async function onDeleteNote(noteId: string) {
  await notesStore.deleteNote(noteId)
  ui.addToast({ type: 'info', message: 'Note deleted' })
}

function openEditModal() {
  if (!notebook.value) return
  editName.value = notebook.value.name
  editDescription.value = notebook.value.description || ''
  showEditModal.value = true
}
</script>

<template>
  <div>
    <!-- Notebook Header -->
    <div v-if="notebook" class="mb-8">
      <div class="flex items-start justify-between">
        <div class="flex items-center gap-4">
          <div
            class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
            :style="{ backgroundColor: notebook.color + '20', color: notebook.color }"
          >
            <span :class="notebook.icon || 'i-ph-notebook'" class="w-7 h-7" />
          </div>
          <div>
            <h1 class="text-2xl font-bold">{{ notebook.name }}</h1>
            <p v-if="notebook.description" class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
              {{ notebook.description }}
            </p>
            <p class="text-xs text-gray-400 mt-1">
              {{ notesStore.total }} notes · Updated {{ format(new Date(notebook.updated_at), 'MMM d, yyyy') }}
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <UiButton variant="ghost" size="sm" @click="openEditModal">
            <span class="i-ph-pencil-simple w-4 h-4" />
          </UiButton>
          <UiButton variant="ghost" size="sm" @click="showDeleteConfirm = true">
            <span class="i-ph-trash w-4 h-4 text-red-500" />
          </UiButton>
        </div>
      </div>
    </div>

    <!-- Quick create note -->
    <form @submit.prevent="createNote" class="mb-6">
      <div class="flex gap-3">
        <input
          v-model="newNoteTitle"
          placeholder="Quick note title... press Enter to create"
          class="flex-1 px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all placeholder:text-gray-400"
        />
        <UiButton variant="primary" type="submit" :disabled="!newNoteTitle.trim()">
          <span class="i-ph-plus w-5 h-5" />
          Add
        </UiButton>
      </div>
    </form>

    <!-- Notes List -->
    <div v-if="notesStore.isLoading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="glass-card p-4">
        <UiSkeleton width="60%" height="1.125rem" class="mb-2" />
        <UiSkeleton width="90%" height="0.875rem" />
      </div>
    </div>

    <div v-else-if="notesStore.notes.length === 0">
      <UiEmpty
        icon="i-ph-note-pencil"
        title="No notes yet"
        description="Create your first note in this notebook."
      />
    </div>

    <div v-else class="space-y-2">
      <NoteListItem
        v-for="note in notesStore.notes"
        :key="note.id"
        :note="note"
        @click="router.push({ name: 'note-edit', params: { notebookId, noteId: note.id } })"
        @delete="onDeleteNote(note.id)"
      />
    </div>

    <!-- Edit Modal -->
    <UiModal v-model:open="showEditModal" title="Edit Notebook" size="sm">
      <div class="flex flex-col gap-4">
        <UiInput v-model="editName" label="Name" />
        <UiInput v-model="editDescription" label="Description" />
      </div>
      <template #footer>
        <UiButton variant="ghost" @click="showEditModal = false">Cancel</UiButton>
        <UiButton variant="primary" @click="updateNotebook">Save</UiButton>
      </template>
    </UiModal>

    <!-- Delete Confirm -->
    <UiModal v-model:open="showDeleteConfirm" title="Delete Notebook" size="sm">
      <p class="text-sm text-gray-600 dark:text-gray-400">
        Are you sure? This will permanently delete this notebook and all notes within it.
      </p>
      <template #footer>
        <UiButton variant="ghost" @click="showDeleteConfirm = false">Cancel</UiButton>
        <UiButton variant="danger" @click="deleteNotebook">Delete</UiButton>
      </template>
    </UiModal>
  </div>
</template>
