<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotebooksStore } from '@/stores/notebooks'
import { useNotesStore } from '@/stores/notes'
import { useTagsStore } from '@/stores/tags'
import { useUiStore } from '@/stores/ui'
import { notebooksApi } from '@/api/notebooks'
import type { Tag } from '@/types/tag'
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
const tagsStore = useTagsStore()
const ui = useUiStore()

const notebookId = computed(() => route.params.id as string)
const notebook = ref(notebooksStore.notebooks.find(n => n.id === notebookId.value) || null)
const showEditModal = ref(false)
const showDeleteConfirm = ref(false)
const showCreateModal = ref(false)
const editName = ref('')
const editDescription = ref('')
const newNoteTitle = ref('')
const selectedTagIds = ref<string[]>([])
const showTagDropdown = ref(false)
const creating = ref(false)

const selectedTags = computed<Tag[]>(() =>
  tagsStore.tags.filter(t => selectedTagIds.value.includes(t.id))
)
const availableTags = computed(() =>
  tagsStore.tags.filter(t => !selectedTagIds.value.includes(t.id))
)

onMounted(async () => {
  tagsStore.fetchTags()
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

function openCreateModal() {
  newNoteTitle.value = ''
  selectedTagIds.value = []
  showTagDropdown.value = false
  showCreateModal.value = true
}

function addTagToSelection(tag: Tag) {
  if (!selectedTagIds.value.includes(tag.id)) {
    selectedTagIds.value.push(tag.id)
  }
  showTagDropdown.value = false
}

function removeTagFromSelection(tagId: string) {
  selectedTagIds.value = selectedTagIds.value.filter(id => id !== tagId)
}

async function createNote() {
  if (!newNoteTitle.value.trim()) return
  creating.value = true
  try {
    const note = await notesStore.createNote(notebookId.value, {
      title: newNoteTitle.value.trim(),
      ...(selectedTagIds.value.length > 0 ? { tag_ids: selectedTagIds.value } : {}),
    })
    showCreateModal.value = false
    ui.addToast({ type: 'success', message: 'Note created!' })
    router.push({ name: 'note-edit', params: { notebookId: notebookId.value, noteId: note.id } })
  } catch (e: any) {
    const detail = e.response?.data?.detail || 'Failed to create note'
    ui.addToast({ type: 'error', message: detail })
  } finally {
    creating.value = false
  }
}

async function onDeleteNote(noteId: string) {
  if (!confirm('Delete this note?')) return
  await notesStore.deleteNote(noteId)
  ui.addToast({ type: 'info', message: 'Note deleted' })
}

async function onArchiveNote(note: any) {
  try {
    const newState = !note.is_archived
    await notesStore.toggleArchive(note.id, newState)
    if (newState) {
      await notesStore.fetchNotes(notebookId.value)
    }
    ui.addToast({ type: 'success', message: newState ? 'Note archived' : 'Note restored' })
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to update note' })
  }
}

async function onPinNote(note: any) {
  try {
    await notesStore.togglePin(note.id, !note.is_pinned)
    ui.addToast({ type: 'success', message: note.is_pinned ? 'Note unpinned' : 'Note pinned' })
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to update note' })
  }
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
          <UiButton variant="primary" size="sm" @click="openCreateModal">
            <span class="i-ph-plus w-4 h-4" />
            Add
          </UiButton>
          <UiButton variant="ghost" size="sm" @click="openEditModal">
            <span class="i-ph-pencil-simple w-4 h-4" />
          </UiButton>
          <UiButton variant="ghost" size="sm" @click="showDeleteConfirm = true">
            <span class="i-ph-trash w-4 h-4 text-red-500" />
          </UiButton>
        </div>
      </div>
    </div>

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
      >
        <UiButton variant="primary" class="mt-4" @click="openCreateModal">
          <span class="i-ph-plus w-5 h-5" />
          Add Note
        </UiButton>
      </UiEmpty>
    </div>

    <div v-else class="space-y-2">
      <NoteListItem
        v-for="note in notesStore.notes"
        :key="note.id"
        :note="note"
        @click="router.push({ name: 'note-edit', params: { notebookId, noteId: note.id } })"
        @delete="onDeleteNote(note.id)"
        @archive="onArchiveNote(note)"
        @pin="onPinNote(note)"
      />
    </div>

    <!-- Create Note Modal -->
    <UiModal v-model:open="showCreateModal" title="New Note" size="sm">
      <div class="flex flex-col gap-4">
        <UiInput
          v-model="newNoteTitle"
          label="Title"
          placeholder="Note title"
          icon="i-ph-note-pencil"
          @keyup.enter="createNote"
        />
        <!-- Tag selector -->
        <div>
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300 block mb-1.5">Tags</label>
          <!-- Selected tags -->
          <div v-if="selectedTags.length > 0" class="flex flex-wrap gap-1.5 mb-2">
            <span
              v-for="tag in selectedTags"
              :key="tag.id"
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
              :style="{ backgroundColor: tag.color + '20', color: tag.color }"
            >
              {{ tag.name }}
              <button
                type="button"
                class="w-3.5 h-3.5 flex items-center justify-center rounded-full hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
                @click="removeTagFromSelection(tag.id)"
              >
                <span class="i-ph-x w-3 h-3" />
              </button>
            </span>
          </div>
          <!-- Tag dropdown -->
          <div class="relative">
            <UiButton variant="ghost" size="sm" class="rounded-xl border border-gray-200 dark:border-gray-700 w-full justify-start" @click="showTagDropdown = !showTagDropdown">
              <span class="i-ph-tag w-4 h-4 mr-2" />
              <span v-if="availableTags.length > 0" class="text-gray-400">{{ availableTags.length }} tag{{ availableTags.length !== 1 ? 's' : '' }} available</span>
              <span v-else class="text-gray-400">No more tags</span>
            </UiButton>
            <div
              v-if="showTagDropdown && availableTags.length > 0"
              class="absolute top-full left-0 right-0 mt-1 z-40 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-xl p-2 max-h-48 overflow-y-auto"
            >
              <button
                v-for="tag in availableTags"
                :key="tag.id"
                type="button"
                class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                @click="addTagToSelection(tag)"
              >
                <span class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ backgroundColor: tag.color }" />
                <span class="text-gray-700 dark:text-gray-300 truncate">{{ tag.name }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <UiButton variant="ghost" @click="showCreateModal = false">Cancel</UiButton>
        <UiButton variant="primary" :loading="creating" :disabled="!newNoteTitle.trim()" @click="createNote">Create</UiButton>
      </template>
    </UiModal>

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
