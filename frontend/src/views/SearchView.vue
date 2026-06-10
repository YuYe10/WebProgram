<script setup lang="ts">
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

const query = ref((route.query.q as string) || '')
const notebookId = ref((route.query.notebook_id as string) || '')
const results = ref<Note[]>([])
const isLoading = ref(false)
const total = ref(0)

const selectedNotebook = computed(() =>
  notebooksStore.notebooks.find(n => n.id === notebookId.value)
)

onMounted(() => {
  notebooksStore.fetchNotebooks()
})

const emptyDescription = computed(() => {
  const parts = [`No notes found for "${query.value}"`]
  if (selectedNotebook.value) parts.push(`in "${selectedNotebook.value.name}"`)
  return parts.join(' ')
})

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

watch([query, notebookId], () => {
  search()
}, { immediate: true })

function goToNote(note: Note) {
  router.push({ name: 'note-edit', params: { notebookId: note.notebook_id, noteId: note.id } })
}

function clearNotebookFilter() {
  notebookId.value = ''
}

// Archive / Pin / Delete actions for search results
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

    <!-- Search input + notebook filter -->
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

    <!-- Active filter indicator -->
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

    <!-- Empty -->
    <div v-else-if="query && results.length === 0">
      <UiEmpty
        icon="i-ph-magnifying-glass"
        title="No results"
        :description="emptyDescription"
      />
    </div>

    <!-- Results -->
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
