/**
 * @module stores/editor
 * @description Pinia store for the note editor state. Tracks the current note's
 * dirty flag, save status, word/character counts, and timestamps. Used by
 * auto-save / debounce-save logic in the editor component.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useEditorStore = defineStore('editor', () => {
  // ── State ──────────────────────────────────────────────────────────────────

  /** ID of the note currently open in the editor, or `null`. */
  const currentNoteId = ref<string | null>(null)

  /** Whether the editor has unsaved changes since the last save. */
  const isDirty = ref(false)

  /** Timestamp of the last successful save, or `null` if never saved. */
  const lastSavedAt = ref<Date | null>(null)

  /** Whether a save request is currently in flight. */
  const isSaving = ref(false)

  /** Word count of the current editor content. */
  const wordCount = ref(0)

  /** Character count of the current editor content. */
  const charCount = ref(0)

  /**
   * High-level save status indicator for UI display.
   * - `'saved'`  — no unsaved changes
   * - `'saving'` — save in progress
   * - `'unsaved'` — local changes not yet persisted
   */
  const saveStatus = ref<'saved' | 'saving' | 'unsaved'>('saved')

  // ── Actions ────────────────────────────────────────────────────────────────

  /**
   * Mark the editor as having unsaved changes.
   * Typically called on every content keystroke before debounce-save fires.
   */
  function markDirty() {
    isDirty.value = true
  }

  /**
   * Mark the editor as saved (no unsaved changes).
   * Updates the last-saved timestamp to now.
   */
  function markClean() {
    isDirty.value = false
    lastSavedAt.value = new Date()
  }

  /**
   * Set the saving-in-progress flag.
   *
   * @param saving - `true` when a save request starts, `false` when it ends.
   */
  function setSaving(saving: boolean) {
    isSaving.value = saving
  }

  /**
   * Update the word and character counts for the current content.
   *
   * @param words - Current word count.
   * @param chars - Current character count.
   */
  function setCounts(words: number, chars: number) {
    wordCount.value = words
    charCount.value = chars
  }

  /**
   * Reset all editor state to defaults.
   * Called when switching to a different note or closing the editor.
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
