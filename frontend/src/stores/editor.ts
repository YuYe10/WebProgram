/**
 * @module stores/editor
 * @description Pinia store for the note editor state. Tracks the current note's
 * dirty flag, save status, word/character counts, and timestamps. Used by
 * auto-save / debounce-save logic in the editor component.
 * Pinia笔记编辑器状态管理。跟踪当前笔记的脏标记、保存状态、字数/字符数和时间戳。
 * 供编辑器组件中的自动保存/防抖保存逻辑使用。
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useEditorStore = defineStore('editor', () => {
  // ── State ──────────────────────────────────────────────────────────────────
  // ── 状态 ──────────────────────────────────────────────────────────────────

  /** ID of the note currently open in the editor, or `null`.
   * 当前在编辑器中打开的笔记的ID，或`null`。
   */
  const currentNoteId = ref<string | null>(null)

  /** Whether the editor has unsaved changes since the last save.
   * 编辑器自上次保存以来是否有未保存的更改。
   */
  const isDirty = ref(false)

  /** Timestamp of the last successful save, or `null` if never saved.
   * 最后一次成功保存的时间戳，如果从未保存则为`null`。
   */
  const lastSavedAt = ref<Date | null>(null)

  /** Whether a save request is currently in flight.
   * 保存请求是否正在进行中。
   */
  const isSaving = ref(false)

  /** Word count of the current editor content.
   * 当前编辑器内容的字数。
   */
  const wordCount = ref(0)

  /** Character count of the current editor content.
   * 当前编辑器内容的字符数。
   */
  const charCount = ref(0)

  /**
   * High-level save status indicator for UI display.
   * UI显示的高级保存状态指示器。
   * - `'saved'`  — no unsaved changes
   *               没有未保存的更改
   * - `'saving'` — save in progress
   *               正在保存
   * - `'unsaved'` — local changes not yet persisted
   *                本地更改尚未持久化
   */
  const saveStatus = ref<'saved' | 'saving' | 'unsaved'>('saved')

  // ── Actions ────────────────────────────────────────────────────────────────
  // ── 操作 ────────────────────────────────────────────────────────────────

  /**
   * Mark the editor as having unsaved changes.
   * 将编辑器标记为有未保存的更改。
   * Typically called on every content keystroke before debounce-save fires.
   * 通常在防抖保存触发前的每次内容按键时调用。
   */
  function markDirty() {
    isDirty.value = true
  }

  /**
   * Mark the editor as saved (no unsaved changes).
   * 将编辑器标记为已保存（没有未保存的更改）。
   * Updates the last-saved timestamp to now.
   * 将最后保存时间戳更新为现在。
   */
  function markClean() {
    isDirty.value = false
    lastSavedAt.value = new Date()
  }

  /**
   * Set the saving-in-progress flag.
   * 设置保存进行中标志。
   *
   * @param saving - `true` when a save request starts, `false` when it ends.
   *                 保存请求开始时为`true`，结束时为`false`。
   */
  function setSaving(saving: boolean) {
    isSaving.value = saving
  }

  /**
   * Update the word and character counts for the current content.
   * 更新当前内容的字数和字符数。
   *
   * @param words - Current word count.
   *                当前字数。
   * @param chars - Current character count.
   *                当前字符数。
   */
  function setCounts(words: number, chars: number) {
    wordCount.value = words
    charCount.value = chars
  }

  /**
   * Reset all editor state to defaults.
   * 将所有编辑器状态重置为默认值。
   * Called when switching to a different note or closing the editor.
   * 在切换到其他笔记或关闭编辑器时调用。
   */
  function reset() {
    currentNoteId.value = null
    isDirty.value = false
    lastSavedAt.value = null
    isSaving.value = false
    wordCount.value = 0
    charCount.value = 0
  }

  return {
    currentNoteId,
    isDirty,
    lastSavedAt,
    isSaving,
    wordCount,
    charCount,
    saveStatus,
    markDirty,
    markClean,
    setSaving,
    setCounts,
    reset,
  }
})
