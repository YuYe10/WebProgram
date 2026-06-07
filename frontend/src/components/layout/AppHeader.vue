<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import { searchApi } from '@/api/search'
import type { Note } from '@/types/note'

const router = useRouter()
const ui = useUiStore()
const auth = useAuthStore()
const searchQuery = ref('')
const searchInputRef = ref<HTMLInputElement | null>(null)
const showDropdown = ref(false)
const suggestions = ref<Note[]>([])
const isSearching = ref(false)
const selectedIndex = ref(-1)
let debounceTimer: ReturnType<typeof setTimeout> | null = null

// Expose focusSearch for global Ctrl+K shortcut
function focusSearch() {
  searchInputRef.value?.focus()
  searchInputRef.value?.select()
}

defineExpose({ focusSearch })

function handleSearch() {
  if (searchQuery.value.trim()) {
    showDropdown.value = false
    router.push({ name: 'search', query: { q: searchQuery.value.trim() } })
    searchQuery.value = ''
  }
}

function selectSuggestion(note: Note) {
  showDropdown.value = false
  searchQuery.value = ''
  router.push({ name: 'note-edit', params: { notebookId: note.notebook_id, noteId: note.id } })
}

async function fetchSuggestions(query: string) {
  if (query.length < 1) {
    suggestions.value = []
    showDropdown.value = false
    return
  }

  isSearching.value = true
  try {
    const response = await searchApi.search({ q: query, size: 6 })
    suggestions.value = response.items
    selectedIndex.value = -1
    showDropdown.value = suggestions.value.length > 0
  } catch {
    suggestions.value = []
    showDropdown.value = false
  } finally {
    isSearching.value = false
  }
}

function onInputChange() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchSuggestions(searchQuery.value)
  }, 200)
}

function onInputFocus() {
  if (searchQuery.value.trim() && suggestions.value.length > 0) {
    showDropdown.value = true
  } else if (searchQuery.value.trim()) {
    fetchSuggestions(searchQuery.value)
  }
}

function onInputBlur() {
  // Delay to allow click on suggestion
  setTimeout(() => {
    showDropdown.value = false
  }, 200)
}

function onInputKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    showDropdown.value = false
    searchInputRef.value?.blur()
    return
  }
  if (!showDropdown.value || suggestions.value.length === 0) return

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    selectedIndex.value = Math.min(selectedIndex.value + 1, suggestions.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    selectedIndex.value = Math.max(selectedIndex.value - 1, -1)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (selectedIndex.value >= 0 && selectedIndex.value < suggestions.value.length) {
      selectSuggestion(suggestions.value[selectedIndex.value])
    } else {
      handleSearch()
    }
  }
}

// Truncate plain text for snippet display
function snippet(text: string | null, maxLen = 80): string {
  if (!text) return 'No content'
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

// Cleanup
watch(showDropdown, (val) => {
  if (!val) selectedIndex.value = -1
})
</script>

<template>
  <header class="sticky top-0 z-20 h-14 flex items-center gap-4 px-4 glass border-b border-gray-200/50 dark:border-gray-800/50">
    <!-- Mobile menu toggle -->
    <button
      class="lg:hidden w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      @click="ui.toggleSidebar()"
    >
      <span class="i-ph-list w-5 h-5" />
    </button>

    <!-- Breadcrumb slot -->
    <div class="flex items-center gap-2 flex-1 min-w-0">
      <slot name="breadcrumb">
        <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Dashboard</span>
      </slot>
    </div>

    <!-- Search bar with autocomplete -->
    <div class="hidden sm:flex items-center gap-2 flex-1 max-w-md relative">
      <form class="relative w-full" @submit.prevent="handleSearch">
        <span class="i-ph-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          ref="searchInputRef"
          v-model="searchQuery"
          type="text"
          placeholder="Search notes... (Ctrl+K)"
          class="w-full pl-10 pr-4 py-1.5 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder:text-gray-400 outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
          @input="onInputChange"
          @focus="onInputFocus"
          @blur="onInputBlur"
          @keydown="onInputKeydown"
        />
      </form>

      <!-- Autocomplete dropdown -->
      <div
        v-if="showDropdown && suggestions.length > 0"
        class="absolute top-full mt-1 left-0 right-0 z-50 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-xl overflow-hidden"
      >
        <div
          v-for="(note, index) in suggestions"
          :key="note.id"
          class="flex items-center gap-3 px-4 py-2.5 cursor-pointer transition-colors text-sm"
          :class="{
            'bg-brand-50 dark:bg-brand-900/20': index === selectedIndex,
            'hover:bg-gray-50 dark:hover:bg-gray-800': index !== selectedIndex,
          }"
          @mousedown.prevent="selectSuggestion(note)"
          @mouseenter="selectedIndex = index"
        >
          <span class="i-ph-note w-4 h-4 text-gray-400 shrink-0" />
          <div class="min-w-0 flex-1">
            <div class="font-medium text-gray-900 dark:text-gray-100 truncate">{{ note.title }}</div>
            <div class="text-xs text-gray-400 truncate">{{ snippet(note.plain_text) }}</div>
          </div>
        </div>
      </div>

      <!-- No results -->
      <div
        v-if="showDropdown && suggestions.length === 0 && !isSearching && searchQuery.trim()"
        class="absolute top-full mt-1 left-0 right-0 z-50 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-xl p-4 text-center text-sm text-gray-400"
      >
        No notes found
      </div>
    </div>

    <!-- Right actions -->
    <div class="flex items-center gap-1">
      <!-- Theme toggle -->
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        :title="ui.resolvedTheme === 'dark' ? 'Switch to light' : 'Switch to dark'"
        @click="ui.setTheme(ui.resolvedTheme === 'dark' ? 'light' : 'dark')"
      >
        <span v-if="ui.resolvedTheme === 'dark'" class="i-ph-sun w-5 h-5" />
        <span v-else class="i-ph-moon w-5 h-5" />
      </button>

      <slot name="actions" />
    </div>
  </header>
</template>
