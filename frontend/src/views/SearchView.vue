<script setup lang="ts">
/**
 * @component SearchView
 * @description Full-text search view for notes with debounced query input
 * and optional notebook filtering.
 * 
 * 笔记的全文搜索视图，支持防抖查询输入和可选的笔记本过滤。
 *
 * Key features:
 * - Debounced search (300ms) to avoid excessive API calls
 *   防抖搜索（300ms）避免过多API调用
 * - Notebook filter via dropdown selector
 *   通过下拉选择器进行笔记本过滤
 * - Active filter indicator with clear button
 *   带清除按钮的活动过滤器指示器
 * - Archive, pin, and delete actions on search results
 *   搜索结果上的归档、置顶和删除操作
 * - Skeleton loading and empty states
 *   骨架加载和空状态
 *
 * @dependencies
 * - searchApi: performs full-text search queries
 *              执行全文搜索查询
 * - useNotebooksStore: provides notebooks for the filter dropdown
 *                      为过滤器下拉菜单提供笔记本
 * - useUiStore: toast notifications
 *               Toast通知
 * - useDebounceFn (VueUse): debounced search execution
 *                           防抖搜索执行
 * - NoteListItem: reusable note card component
 *                 可复用的笔记卡片组件
 *
 * @example
 * <!-- Route: /search?q=keyword&notebook_id=abc123 -->
 * <!-- 路由: /search?q=keyword&notebook_id=abc123 -->
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

/** Search query string, initialized from URL query param
 * 搜索查询字符串，从URL查询参数初始化
 */
const query = ref((route.query.q as string) || '')
/** Notebook ID filter, initialized from URL query param
 * 笔记本ID过滤器，从URL查询参数初始化
 */
const notebookId = ref((route.query.notebook_id as string) || '')
/** Search result notes
 * 搜索结果笔记
 */
const results = ref<Note[]>([])
/** Whether a search request is in progress
 * 搜索请求是否正在进行中
 */
const isLoading = ref(false)
/** Total number of matching results
 * 匹配结果总数
 */
const total = ref(0)

/** The notebook object for the active filter, if any
 * 活动过滤器的笔记本对象（如果有）
 */
const selectedNotebook = computed(() =>
  notebooksStore.notebooks.find(n => n.id === notebookId.value)
)

/** Fetch notebooks for the filter dropdown on mount
 * 挂载时获取笔记本用于过滤器下拉菜单
 */
onMounted(() => {
  notebooksStore.fetchNotebooks()
})

/**
 * Computed description for the empty state, including
 * the search query and optional notebook name.
 * 空状态的计算描述，包含搜索查询和可选的笔记本名称。
 */
const emptyDescription = computed(() => {
  const parts = [`No notes found for "${query.value}"`]
  if (selectedNotebook.value) parts.push(`in "${selectedNotebook.value.name}"`)
  return parts.join(' ')
})

/**
 * Debounced search function (300ms delay).
 * 防抖搜索函数（300ms延迟）。
 * Clears results when the query is empty; otherwise calls the search API
 * with optional notebook filter.
 * 查询为空时清除结果；否则调用搜索API并可选地使用笔记本过滤器。
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

/** Trigger search immediately when query or notebook filter changes
 * 查询或笔记本过滤器变化时立即触发搜索
 */
watch([query, notebookId], () => {
  search()
}, { immediate: true })

/**
 * Navigates to the note editor for the given search result.
 * 导航到给定搜索结果的笔记编辑器。
 * @param note - The note to open
 *               要打开的笔记
 */
function goToNote(note: Note) {
  router.push({ name: 'note-edit', params: { notebookId: note.notebook_id, noteId: note.id } })
}

/** Clears the notebook filter
 * 清除笔记本过滤器
 */
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
