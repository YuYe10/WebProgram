<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { searchApi } from '@/api/search'
import type { Note } from '@/types/note'
import UiInput from '@/components/ui/UiInput.vue'
import UiEmpty from '@/components/ui/UiEmpty.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import NoteListItem from '@/components/note/NoteListItem.vue'
import { useRouter } from 'vue-router'
import { useDebounceFn } from '@vueuse/core'

const route = useRoute()
const router = useRouter()
const query = ref((route.query.q as string) || '')
const results = ref<Note[]>([])
const isLoading = ref(false)
const total = ref(0)

const search = useDebounceFn(async () => {
  if (!query.value.trim()) {
    results.value = []
    total.value = 0
    return
  }
  isLoading.value = true
  try {
    const resp = await searchApi.search({ q: query.value.trim(), page: 1, size: 20 })
    results.value = resp.items
    total.value = resp.total
  } catch {
    results.value = []
  } finally {
    isLoading.value = false
  }
}, 300)

watch(query, () => {
  search()
}, { immediate: true })

function goToNote(note: Note) {
  router.push({ name: 'note-edit', params: { notebookId: note.notebook_id, noteId: note.id } })
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">Search</h1>
    <UiInput
      v-model="query"
      icon="i-ph-magnifying-glass"
      placeholder="Search your notes..."
      class="mb-6"
    />

    <div v-if="isLoading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="glass-card p-4">
        <UiSkeleton width="60%" height="1.125rem" class="mb-2" />
        <UiSkeleton width="90%" height="0.875rem" />
      </div>
    </div>

    <div v-else-if="query && results.length === 0">
      <UiEmpty
        icon="i-ph-magnifying-glass"
        title="No results"
        :description="`No notes found for \"${query}\"`"
      />
    </div>

    <div v-else-if="results.length > 0" class="space-y-2">
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">{{ total }} results found</p>
      <NoteListItem
        v-for="note in results"
        :key="note.id"
        :note="note"
        @click="goToNote(note)"
      />
    </div>
  </div>
</template>
