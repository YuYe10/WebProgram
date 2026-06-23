/**
 * @component AppHeader
 * @description Sticky top header bar with a search bar (autocomplete + keyboard navigation),
 *   breadcrumb slot, theme toggle, and an actions slot. Exposes `focusSearch()` for the
 *   global Ctrl+K shortcut.
 * 
 * 粘性顶部头部栏，包含搜索栏（自动补全+键盘导航）、面包屑插槽、主题切换和操作插槽。
 * 暴露`focusSearch()`方法供DefaultLayout中的全局Ctrl+K快捷键使用。
 *
 * @props None (uses stores only)
 *        无属性（仅使用状态管理）
 *
 * @emits None
 *        无事件
 *
 * @example
 * <AppHeader>
 *   <template #breadcrumb>My Notebook</template>
 *   <template #actions><button>New</button></template>
 * </AppHeader>
 */
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

/** Current value of the search input
 * 搜索输入框的当前值
 */
const searchQuery = ref('')
/** Template ref to the search <input> element
 * 搜索<input>元素的模板引用
 */
const searchInputRef = ref<HTMLInputElement | null>(null)
/** Whether the autocomplete dropdown is visible
 * 自动补全下拉菜单是否可见
 */
const showDropdown = ref(false)
/** Autocomplete suggestion results
 * 自动补全建议结果
 */
const suggestions = ref<Note[]>([])
/** Whether a search request is in flight
 * 搜索请求是否正在进行中
 */
const isSearching = ref(false)
/** Index of the currently highlighted suggestion (-1 = none)
 * 当前高亮建议的索引（-1表示没有）
 */
const selectedIndex = ref(-1)
/** Timer handle for input debouncing
 * 输入防抖的计时器句柄
 */
let debounceTimer: ReturnType<typeof setTimeout> | null = null

/**
 * Focuses and selects the search input text.
 * 聚焦并选中搜索输入框文本。
 * Exposed for the global Ctrl+K shortcut in DefaultLayout.
 * 暴露供DefaultLayout中的全局Ctrl+K快捷键使用。
 */
function focusSearch() {
  searchInputRef.value?.focus()
  searchInputRef.value?.select()
}

defineExpose({ focusSearch })

/**
 * Navigates to the full search results page with the current query.
 * 使用当前查询导航到完整搜索结果页面。
 * Called on form submit (Enter) when no suggestion is selected.
 * 当没有选中建议时在表单提交（Enter）时调用。
 */
function handleSearch() {
  if (searchQuery.value.trim()) {
    showDropdown.value = false
    router.push({ name: 'search', query: { q: searchQuery.value.trim() } })
    searchQuery.value = ''
  }
}

/**
 * Navigates to the editor for a selected suggestion note.
 * 导航到选中建议笔记的编辑器。
 * @param note - The note to open
 *               要打开的笔记
 */
function selectSuggestion(note: Note) {
  showDropdown.value = false
  searchQuery.value = ''
  router.push({ name: 'note-edit', params: { notebookId: note.notebook_id, noteId: note.id } })
}

/**
 * Fetches autocomplete suggestions from the search API.
 * 从搜索API获取自动补全建议。
 * @param query - The search string (minimum 1 character)
 *                搜索字符串（至少1个字符）
 */
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

/** Debounced handler for input changes — fetches suggestions after 200ms idle
 * 输入变化的防抖处理器——空闲200毫秒后获取建议
 */
function onInputChange() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchSuggestions(searchQuery.value)
  }, 200)
}

/** Re-opens the dropdown on focus if suggestions are available
 * 如果有建议，在聚焦时重新打开下拉菜单
 */
function onInputFocus() {
  if (searchQuery.value.trim() && suggestions.value.length > 0) {
    showDropdown.value = true
  } else if (searchQuery.value.trim()) {
    fetchSuggestions(searchQuery.value)
  }
}

/** Closes the dropdown on blur with a delay to allow suggestion clicks
 * 在失焦时延迟关闭下拉菜单，以允许点击建议
 */
function onInputBlur() {
  setTimeout(() => {
    showDropdown.value = false
  }, 200)
}

/**
 * Handles keyboard navigation within the autocomplete dropdown.
 * 处理自动补全下拉菜单中的键盘导航。
 * - Escape: close dropdown and blur input
 *           关闭下拉菜单并失焦输入框
 * - ArrowDown/ArrowUp: move selection
 *                      移动选择
 * - Enter: select highlighted suggestion or submit search
 *          选中高亮建议或提交搜索
 */
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

/**
 * Truncates plain text for snippet display in the dropdown.
 * 截断纯文本用于下拉菜单中的片段显示。
 * @param text - The full text to truncate
 *               要截断的完整文本
 * @param maxLen - Maximum character length (default 80)
 *                 最大字符长度（默认80）
 * @returns Truncated string with ellipsis if needed, or 'No content'
 *          如果需要，返回带省略号的截断字符串，否则返回'No content'
 */
function snippet(text: string | null, maxLen = 80): string {
  if (!text) return 'No content'
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

/** Resets the selected index when the dropdown is closed
 * 当下拉菜单关闭时重置选中索引
 */
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

      <!-- Autocomplete dropdown — shown when suggestions are available -->
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
            <div v-if="note.notebook_name" class="flex items-center gap-0.5 text-xs text-brand-500 dark:text-brand-400 mb-0.5">
              <span class="i-ph-notebook w-3 h-3 shrink-0" />
              <span class="truncate">{{ note.notebook_name }}</span>
            </div>
            <div class="text-xs text-gray-400 truncate">{{ snippet(note.plain_text) }}</div>
          </div>
        </div>
      </div>

      <!-- Empty state shown when search yields no results -->
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
