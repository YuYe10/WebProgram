<script setup lang="ts">
/**
 * @component AllNotesView
 * @description Displays a paginated list of all notes across notebooks,
 * with optional filtering by tag via query parameter.
 * 
 * 显示跨笔记本的所有笔记的分页列表，支持通过查询参数按标签过滤。
 *
 * Key features:
 * - Paginated note list with "Load more" support
 *   带"加载更多"支持的分页笔记列表
 * - Tag filtering via `?tag_id=` query parameter
 *   通过`?tag_id=`查询参数进行标签过滤
 * - Archive, pin, and delete actions per note
 *   每条笔记的归档、置顶和删除操作
 * - Skeleton loading states and empty states
 *   骨架加载状态和空状态
 *
 * @dependencies
 * - useNotesStore: note data management
 *                  笔记数据管理
 * - useTagsStore: tag data for filter indicator
 *                 过滤器指示器的标签数据
 * - useUiStore: toast notifications
 *               Toast通知
 * - NoteListItem: reusable note card component
 *                 可复用的笔记卡片组件
 *
 * @example
 * <!-- Route: /all-notes or /all-notes?tag_id=abc123 -->
 * <!-- 路由: /all-notes 或 /all-notes?tag_id=abc123 -->
 * <AllNotesView />
 */
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

/** Current page of notes
 * 当前页面的笔记列表
 */
const notes = ref<Note[]>([])
/** Whether notes are being loaded
 * 笔记是否正在加载中
 */
const isLoading = ref(true)
/** Total number of notes matching the current filter
 * 匹配当前过滤器的笔记总数
 */
const total = ref(0)
/** Current page number for pagination
 * 分页的当前页码
 */
const page = ref(1)
/** Number of notes per page
 * 每页笔记数
 */
const pageSize = 20
/** Whether more pages are available to load
 * 是否有更多页面可加载
 */
const hasMore = ref(false)

/** Tag ID from the query string, used to filter notes
 * 查询字符串中的标签ID，用于过滤笔记
 */
const tagId = computed(() => (route.query.tag_id as string) || '')
/** The full tag object for the active filter, if any
 * 活动过滤器的完整标签对象（如果有）
 */
const activeTag = computed(() => tagsStore.tags.find(t => t.id === tagId.value))

/** Fetch tags and notes on mount
 * 挂载时获取标签和笔记
 */
onMounted(() => {
  tagsStore.fetchTags()
  fetchNotes()
})

/** Reset to page 1 and re-fetch when the tag filter changes
 * 标签过滤器变化时重置到第1页并重新获取
 */
watch(tagId, () => {
  page.value = 1
  fetchNotes()
})

/**
 * Fetches the first page of notes, optionally filtered by tag.
 * 获取第一页笔记，可选地按标签过滤。
 * Replaces the current notes list with the response items.
 * 用响应项替换当前笔记列表。
 */
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

/**
 * Loads the next page of notes and appends them to the list.
 * 加载下一页笔记并追加到列表。
 * Reverts the page number on failure.
 * 失败时回滚页码。
 */
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

/**
 * Navigates to the note editor for the given note.
 * 导航到给定笔记的编辑器。
 * @param note - The note to open
 *               要打开的笔记
 */
function goToNote(note: Note) {
  router.push({ name: 'note-edit', params: { notebookId: note.notebook_id, noteId: note.id } })
}

/** Removes the tag filter by navigating to the base all-notes route
 * 通过导航到基础all-notes路由来移除标签过滤器
 */
function clearTagFilter() {
  router.replace({ name: 'all-notes' })
}

// ── Archive / Pin / Delete actions ──

/**
 * Toggles the archive state of a note.
 * Archived notes are removed from the list.
 * @param note - The note to archive/unarchive
 */
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

/**
 * Toggles the pin state of a note.
 * @param note - The note to pin/unpin
 */
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

/**
 * Deletes a note after user confirmation.
 * Removes the note from the list on success.
 * @param note - The note to delete
 */
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

    <!-- Tag filter indicator: shows active tag with clear button -->
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

    <!-- Note count when no tag filter is active -->
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

    <!-- Empty state: different messages for tag-filtered vs. unfiltered -->
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

    <!-- Note list with archive/pin/delete actions -->
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
