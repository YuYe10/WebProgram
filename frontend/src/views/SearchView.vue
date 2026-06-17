<script setup lang="ts">
/**
 * @component SearchView
 * @description Full-text search view for notes with debounced query input
 * and optional notebook filtering.
 *
 * Key features:
 * - Debounced search (300ms) to avoid excessive API calls
 * - Notebook filter via dropdown selector
 * - Active filter indicator with clear button
 * - Archive, pin, and delete actions on search results
 * - Skeleton loading and empty states
 *
 * @dependencies
 * - searchApi: performs full-text search queries
 * - useNotebooksStore: provides notebooks for the filter dropdown
 * - useUiStore: toast notifications
 * - useDebounceFn (VueUse): debounced search execution
 * - NoteListItem: reusable note card component
 *
 * @example
 * <!-- Route: /search?q=keyword&notebook_id=abc123 -->
 * <SearchView />
 */
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { searchApi } from '@/api/search'
import { useNotebooksStore } from '@/stores/notebooks'
import { useUiStore } from '@/stores/ui'
import type { Note } from '@/types/note'
import UiInput from '@/components/ui/UiInput.vue'
import UiEmpty from '@/components/ui/UiEmpty.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiButton from '@/components/ui/UiButton.vue'
import NoteListItem from '@/components/note/NoteListItem.vue'
import { useRouter } from 'vue-router'
import { useDebounceFn } from '@vueuse/core'

const route = useRoute()
const router = useRouter()
const notebooksStore = useNotebooksStore()
const ui = useUiStore()

/** Search query string, initialized from URL query param */
const query = ref((route.query.q as string) || '')
/** Notebook ID filter, initialized from URL query param */
const notebookId = ref((route.query.notebook_id as string) || '')
/** Search result notes */
const results = ref<Note[]>([])
/** Whether a search request is in progress */
const isLoading = ref(false)
/** Total number of matching results */
const total = ref(0)

/** The notebook object for the active filter, if any */
const selectedNotebook = computed(() =>
  notebooksStore.notebooks.find(n => n.id === notebookId.value)
)

/** Fetch notebooks for the filter dropdown on mount */
onMounted(() => {
  notebooksStore.fetchNotebooks()
})

/**
 * Computed description for the empty state, including
 * the search query and optional notebook name.
 */
const emptyDescription = computed(() => {
  const parts = [`No notes found for "${query.value}"`]
  if (selectedNotebook.value) parts.push(`in "${selectedNotebook.value.name}"`)
  return parts.join(' ')
})

/**
 * Debounced search function (300ms delay).
 * Clears results when the query is empty; otherwise calls the search API
 * with optional notebook filter.
 */
const search = useDebounceFn(async () => {
  if (!query.value.trim()) {
    results.value = []
    total.value = 0
    return
  }
  isLoading.value = true
  try {
    const resp = await searchApi.search({
      q: query.value.trim(),
      page: 1,
      size: 50,
      ...(notebookId.value ? { notebook_id: notebookId.value } : {}),
    })
    results.value = resp.items
    total.value = resp.total
  } catch {
    results.value = []
  } finally {
    isLoading.value = false
  }
}, 300)

/** Trigger search immediately when query or notebook filter changes */
watch([query, notebookId], () => {
  search()
}, { immediate: true })

/**
 * Navigates to the note editor for the given search result.
 * @param note - The note to open
 */
function goToNote(note: Note) {
  router.push({ name: 'note-edit', params: { notebookId: note.notebook_id, noteId: note.id } })
}

/** Clears the notebook filter */
function clearNotebookFilter() {
  notebookId.value = ''
}

// Archive / Pin / Delete actions for search results

/**
 * Toggles the archive state of a note in search results.
 * Removes archived notes from the results list.
 * @param note - The note to archive/unarchive
 */
async function toggleArchive(note: Note) {
  try {
    const { notesApi } = await import('@/api/notes')
    const newState = !note.is_archived
    await notesApi.archive(note.id, newState)
    note.is_archived = newState
    if (newState) {
      results.value = results.value.filter(n => n.id !== note.id)
      total.value--
    }
    ui.addToast({ type: 'info', message: newState ? 'Note archived' : 'Note restored' })
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to update note' })
  }
}

/**
 * Toggles the pin state of a note in search results.
 * @param note - The note to pin/unpin
 */
async function togglePin(note: Note) {
  try {
    const { notesApi } = await import('@/api/notes')
    const newState = !note.is_pinned
    await notesApi.pin(note.id, newState)
    note.is_pinned = newState
    ui.addToast({ type: 'success', message: newState ? 'Note pinned' : 'Note unpinned' })
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to update note' })
  }
}

/**
 * Deletes a note from search results after user confirmation.
 * @param note - The note to delete
 */
async function deleteNote(note: Note) {
  if (!confirm(`Delete "${note.title || 'Untitled'}"?`)) return
  try {
    const { notesApi } = await import('@/api/notes')
    await notesApi.delete(note.id)
    results.value = results.value.filter(n => n.id !== note.id)
    total.value--
    ui.addToast({ type: 'info', message: 'Note deleted' })
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to delete note' })
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Search</h1>
    </div>

    <!-- Search input and notebook filter dropdown -->
    <div class="flex gap-3 mb-6">
      <div class="flex-1">
        <UiInput
          v-model="query"
          icon="i-ph-magnifying-glass"
          placeholder="Search your notes..."
        />
      </div>
      <div class="relative">
        <select
          v-model="notebookId"
          class="appearance-none h-11 px-4 pr-10 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all cursor-pointer"
        >
          <option value="">All Notebooks</option>
          <option
            v-for="nb in notebooksStore.notebooks"
            :key="nb.id"
            :value="nb.id"
          >
            {{ nb.name }}
          </option>
        </select>
        <span class="i-ph-caret-down absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
      </div>
    </div>

    <!-- Active notebook filter indicator with clear button -->
    <div v-if="selectedNotebook" class="flex items-center gap-2 mb-4">
      <span
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium"
        :style="{ backgroundColor: selectedNotebook.color + '20', color: selectedNotebook.color }"
      >
        <span class="i-ph-notebook w-4 h-4" />
        {{ selectedNotebook.name }}
        <button
          class="ml-1 w-4 h-4 flex items-center justify-center rounded-full hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
          @click="clearNotebookFilter"
          title="Clear filter"
        >
          <span class="i-ph-x w-3 h-3" />
        </button>
      </span>
      <span v-if="total > 0" class="text-xs text-gray-400">{{ total }} results</span>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="glass-card p-4">
        <UiSkeleton width="60%" height="1.125rem" class="mb-2" />
        <UiSkeleton width="90%" height="0.875rem" />
      </div>
    </div>

    <!-- Empty state: no results found for the query -->
    <div v-else-if="query && results.length === 0">
      <UiEmpty
        icon="i-ph-magnifying-glass"
        title="No results"
        :description="emptyDescription"
      />
    </div>

    <!-- Search results list with archive/pin/delete actions -->
    <div v-else-if="results.length > 0" class="space-y-2">
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">{{ total }} results found</p>
      <NoteListItem
        v-for="note in results"
        :key="note.id"
        :note="note"
        @click="goToNote(note)"
        @archive="toggleArchive(note)"
        @pin="togglePin(note)"
        @delete="deleteNote(note)"
      />
    </div>
  </div>
</template>
