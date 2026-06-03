import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useEditorStore = defineStore('editor', () => {
  const currentNoteId = ref<string | null>(null)
  const isDirty = ref(false)
  const lastSavedAt = ref<Date | null>(null)
  const isSaving = ref(false)
  const wordCount = ref(0)
  const charCount = ref(0)

  function markDirty() {
    isDirty.value = true
  }

  function markClean() {
    isDirty.value = false
    lastSavedAt.value = new Date()
  }

  function setSaving(saving: boolean) {
    isSaving.value = saving
  }

  function setCounts(words: number, chars: number) {
    wordCount.value = words
    charCount.value = chars
  }

  function reset() {
    currentNoteId.value = null
    isDirty.value = false
    lastSavedAt.value = null
    isSaving.value = false
    wordCount.value = 0
    charCount.value = 0
  }

  const saveStatus = ref<'saved' | 'saving' | 'unsaved'>('saved')

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
