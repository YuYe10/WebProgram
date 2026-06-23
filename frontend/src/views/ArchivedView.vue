<script setup lang="ts">
/**
 * @component ArchivedView
 * @description Displays archived notes with restore and permanent delete capabilities.
 * Provides a confirmation modal before permanent deletion to prevent accidents.
 * 
 * 显示已归档笔记，支持恢复和永久删除功能。
 * 在永久删除前提供确认模态框以防止误操作。
 *
 * Key features:
 * - Paginated list of archived notes
 *   已归档笔记的分页列表
 * - Restore notes back to their original notebooks
 *   将笔记恢复到原始笔记本
 * - Permanent deletion with confirmation modal
 *   带确认模态框的永久删除
 * - Skeleton loading and empty states
 *   骨架加载和空状态
 *
 * @dependencies
 * - useUiStore: toast notifications
 *               Toast通知
 * - notesApi: fetch archived notes, restore, and delete
 *             获取归档笔记、恢复和删除
 * - NoteListItem: reusable note card component
 *                 可复用的笔记卡片组件
 *
 * @example
 * <!-- Route: /archived -->
 * <!-- 路由: /archived -->
 * <ArchivedView />
 */
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { notesApi } from '@/api/notes'
import type { Note } from '@/types/note'
import UiEmpty from '@/components/ui/UiEmpty.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiModal from '@/components/ui/UiModal.vue'
import NoteListItem from '@/components/note/NoteListItem.vue'
import { useUiStore } from '@/stores/ui'

const router = useRouter()
const ui = useUiStore()
/** List of archived notes for the current page
 * 当前页面的归档笔记列表
 */
const notes = ref<Note[]>([])
/** Whether archived notes are being loaded
 * 归档笔记是否正在加载中
 */
const isLoading = ref(true)
/** Total number of archived notes
 * 归档笔记总数
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
/** Whether more archived notes are available
 * 是否有更多归档笔记可加载
 */
const hasMore = ref(false)

/** Whether the delete confirmation modal is visible
 * 删除确认模态框是否可见
 */
const showDeleteConfirm = ref(false)
/** The note pending permanent deletion
 * 等待永久删除的笔记
 */
const noteToDelete = ref<Note | null>(null)
/** Whether a permanent delete request is in progress
 * 永久删除请求是否正在进行中
 */
const deleting = ref(false)

/** Fetch archived notes on mount
 * 挂载时获取归档笔记
 */
onMounted(() => {
  fetchArchived()
})

/**
 * Fetches the first page of archived notes.
 * 获取第一页归档笔记。
 * Replaces the current list with the response items.
 * 用响应项替换当前列表。
 */
async function fetchArchived() {
  isLoading.value = true
  try {
    const resp = await notesApi.getArchivedNotes({ page: page.value, size: pageSize })
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
 * Loads the next page of archived notes and appends them.
 * 加载下一页归档笔记并追加到列表。
 * Reverts the page number on failure.
 * 失败时回滚页码。
 */
async function loadMore() {
  page.value++
  try {
    const resp = await notesApi.getArchivedNotes({ page: page.value, size: pageSize })
    notes.value.push(...resp.items)
    total.value = resp.total
    hasMore.value = notes.value.length < resp.total
  } catch {
    page.value--
  }
}

/**
 * Navigates to the note editor for the given archived note.
 * 导航到给定归档笔记的编辑器。
 * @param note - The note to open
 *               要打开的笔记
 */
function goToNote(note: Note) {
  router.push({ name: 'note-edit', params: { notebookId: note.notebook_id, noteId: note.id } })
}

/**
 * Restores an archived note by setting its archive state to false.
 * 通过将归档状态设置为false来恢复归档笔记。
 * Removes the note from the local list on success.
 * 成功时从本地列表中移除该笔记。
 * @param note - The note to restore
 *               要恢复的笔记
 */
async function restoreNote(note: Note) {
  try {
    await notesApi.archive(note.id, false)
    notes.value = notes.value.filter(n => n.id !== note.id)
    total.value--
    ui.addToast({ type: 'success', message: 'Note restored' })
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to restore note' })
  }
}

/**
 * Opens the delete confirmation modal for the given note.
 * 打开给定笔记的删除确认模态框。
 * @param note - The note to be deleted
 *               要删除的笔记
 */
function confirmDelete(note: Note) {
  noteToDelete.value = note
  showDeleteConfirm.value = true
}

/**
 * Permanently deletes the note stored in `noteToDelete`.
 * 永久删除存储在`noteToDelete`中的笔记。
 * Closes the modal and removes the note from the list on success.
 * 成功时关闭模态框并从列表中移除该笔记。
 */
async function deletePermanently() {
  if (!noteToDelete.value) return
  deleting.value = true
  try {
    await notesApi.delete(noteToDelete.value.id)
    notes.value = notes.value.filter(n => n.id !== noteToDelete.value!.id)
    total.value--
    showDeleteConfirm.value = false
    noteToDelete.value = null
    ui.addToast({ type: 'success', message: 'Note permanently deleted' })
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to delete note' })
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-2">
      <div>
        <h1 class="text-2xl font-bold">Archived</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          View and restore your archived notes.
        </p>
      </div>
    </div>

    <p v-if="!isLoading && notes.length > 0" class="text-sm text-gray-500 dark:text-gray-400 mb-6">
      {{ total }} archived {{ total === 1 ? 'note' : 'notes' }}
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
        icon="i-ph-archive-box"
        title="No archived items"
        description="Archive notes to keep your workspace clean. They will appear here."
      />
    </div>

    <!-- Archived note list with restore and delete actions -->
    <div v-else class="space-y-2">
      <NoteListItem
        v-for="note in notes"
        :key="note.id"
        :note="note"
        @click="goToNote(note)"
        @archive="restoreNote(note)"
        @delete="confirmDelete(note)"
      />

      <!-- Load more -->
      <div v-if="hasMore" class="flex justify-center pt-4">
        <UiButton variant="ghost" @click="loadMore">
          <span class="i-ph-arrow-down w-4 h-4" />
          Load more
        </UiButton>
      </div>
    </div>

    <!-- Delete confirmation modal -->
    <UiModal v-model:open="showDeleteConfirm" title="Delete Permanently" size="sm">
      <div class="flex flex-col gap-3">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          This will permanently delete <strong>"{{ noteToDelete?.title || 'Untitled' }}"</strong>.
          This action cannot be undone.
        </p>
      </div>
      <template #footer>
        <UiButton variant="ghost" @click="showDeleteConfirm = false">Cancel</UiButton>
        <UiButton variant="danger" :loading="deleting" @click="deletePermanently">
          Delete Permanently
        </UiButton>
      </template>
    </UiModal>
  </div>
</template>
