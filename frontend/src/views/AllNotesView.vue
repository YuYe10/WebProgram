<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { notesApi } from '@/api/notes'
import { useNotesStore } from '@/stores/notes'
import { useTagsStore } from '@/stores/tags'
import { useUiStore } from '@/stores/ui'
import type { Note } from '@/types/note'
import UiEmpty from '@/components/ui/UiEmpty.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiButton from '@/components/ui/UiButton.vue'
import NoteListItem from '@/components/note/NoteListItem.vue'

const route = useRoute()
const router = useRouter()
const notesStore = useNotesStore()
const tagsStore = useTagsStore()
const ui = useUiStore()

const notes = ref<Note[]>([])
const isLoading = ref(true)
const total = ref(0)
const page = ref(1)
const pageSize = 20
const hasMore = ref(false)

const tagId = computed(() => (route.query.tag_id as string) || '')
const activeTag = computed(() => tagsStore.tags.find(t => t.id === tagId.value))

onMounted(() => {
  tagsStore.fetchTags()
  fetchNotes()
})

watch(tagId, () => {
  page.value = 1
  fetchNotes()
})

async function fetchNotes() {
  isLoading.value = true
  try {
    const params: { page: number; size: number; tag_id?: string } = {
      page: page.value,
      size: pageSize,
    }
    if (tagId.value) params.tag_id = tagId.value
    const resp = await notesApi.getAllNotes(params)
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
    const params: { page: number; size: number; tag_id?: string } = {
      page: page.value,
      size: pageSize,
    }
    if (tagId.value) params.tag_id = tagId.value
    const resp = await notesApi.getAllNotes(params)
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

function clearTagFilter() {
  router.replace({ name: 'all-notes' })
}

// ── Archive / Pin / Delete actions ──
async function toggleArchive(note: Note) {
  try {
    const newState = !note.is_archived
    await notesApi.archive(note.id, newState)
    if (newState) {
      notes.value = notes.value.filter(n => n.id !== note.id)
      total.value--
      ui.addToast({ type: 'info', message: 'Note archived' })
    } else {
      note.is_archived = false
      ui.addToast({ type: 'success', message: 'Note restored' })
    }
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to update note' })
  }
}

async function togglePin(note: Note) {
  try {
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
    await notesApi.delete(note.id)
    notes.value = notes.value.filter(n => n.id !== note.id)
    total.value--
    ui.addToast({ type: 'info', message: 'Note deleted' })
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to delete note' })
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-2">
      <div>
        <h1 class="text-2xl font-bold">All Notes</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Browse all your notes across notebooks.
        </p>
      </div>
    </div>

    <!-- Tag filter indicator -->
    <div v-if="activeTag" class="flex items-center gap-2 mb-6">
      <span
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium"
        :style="{ backgroundColor: activeTag.color + '20', color: activeTag.color }"
      >
        <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: activeTag.color }" />
        {{ activeTag.name }}
        <button
          class="ml-1 w-4 h-4 flex items-center justify-center rounded-full hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
          @click="clearTagFilter"
          title="Clear filter"
        >
          <span class="i-ph-x w-3 h-3" />
        </button>
      </span>
      <span class="text-xs text-gray-400">{{ total }} notes</span>
    </div>

    <p v-else-if="!isLoading && notes.length > 0" class="text-sm text-gray-500 dark:text-gray-400 mb-6">
      {{ total }} {{ total === 1 ? 'note' : 'notes' }} total
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
        v-if="activeTag"
        icon="i-ph-tag"
        title="No notes with this tag"
        description="No notes are tagged with this tag yet."
      >
        <UiButton variant="ghost" class="mt-4" @click="clearTagFilter">
          Clear filter
        </UiButton>
      </UiEmpty>
      <UiEmpty
        v-else
        icon="i-ph-note-pencil"
        title="No notes yet"
        description="Create your first note in a notebook to get started."
      />
    </div>

    <!-- Note list -->
    <div v-else class="space-y-2">
      <NoteListItem
        v-for="note in notes"
        :key="note.id"
        :note="note"
        @click="goToNote(note)"
        @archive="toggleArchive(note)"
        @pin="togglePin(note)"
        @delete="deleteNote(note)"
      />

      <!-- Load more -->
      <div v-if="hasMore" class="flex justify-center pt-4">
        <UiButton variant="ghost" @click="loadMore">
          <span class="i-ph-arrow-down w-4 h-4" />
          Load more
        </UiButton>
      </div>
    </div>
  </div>
</template>
