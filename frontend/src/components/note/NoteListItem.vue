/**
 * @component NoteListItem
 * @description A card-style list item representing a single note. Displays the note title,
 *   a text preview, notebook name, update date, deletion countdown (for archived notes),
 *   tags, and action buttons (pin, archive, delete).
 *
 * @props note - The Note object to display
 *
 * @emits click  - Fired when the card body is clicked
 * @emits delete - Fired when the delete button is clicked
 * @emits archive - Fired when the archive/restore button is clicked
 * @emits pin - Fired when the pin/unpin button is clicked
 *
 * @example
 * <NoteListItem :note="note" @click="openNote" @delete="onDelete" @archive="onArchive" @pin="onPin" />
 */
<script setup lang="ts">
import { computed } from 'vue'
import type { Note } from '@/types/note'
import { format } from 'date-fns'

const props = defineProps<{ note: Note }>()
const emit = defineEmits<{
  click: []
  delete: []
  archive: []
  pin: []
}>()

/**
 * Generates a plain-text preview of the note content (up to 150 characters).
 * Prefers `plain_text`; falls back to recursively extracting text from the
 * structured `content` JSON.
 * @returns A truncated preview string
 */
function getPreview(): string {
  if (props.note.plain_text) {
    return props.note.plain_text.slice(0, 150)
  }
  if (props.note.content) {
    const extractText = (node: any): string => {
      if (node.text) return node.text
      if (node.content) return node.content.map(extractText).join(' ')
      return ''
    }
    return extractText(props.note.content).slice(0, 150)
  }
  return 'No content'
}

/**
 * Computed countdown until auto-deletion for archived notes.
 * Archived notes are permanently deleted 7 days after `archived_at`.
 * Returns `null` for non-archived notes.
 */
const deletionCountdown = computed(() => {
  if (!props.note.is_archived || !props.note.archived_at) return null

  const archivedAt = new Date(props.note.archived_at)
  const deletionAt = new Date(archivedAt.getTime() + 7 * 24 * 60 * 60 * 1000)
  const now = new Date()
  const remainingMs = deletionAt.getTime() - now.getTime()

  if (remainingMs <= 0) {
    return { text: 'Deleting soon...', urgent: true }
  }

  const days = Math.floor(remainingMs / (1000 * 60 * 60 * 24))
  const hours = Math.floor((remainingMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((remainingMs % (1000 * 60 * 60)) / (1000 * 60))

  if (days > 0) {
    return {
      text: `Auto-delete in ${days}d ${hours}h`,
      urgent: days < 1,
    }
  }
  if (hours > 0) {
    return {
      text: `Auto-delete in ${hours}h ${minutes}m`,
      urgent: true,
    }
  }
  return {
    text: `Auto-delete in ${minutes}m`,
    urgent: true,
  }
})
</script>

<template>
  <!-- Note card — click emits 'click' for navigation -->
  <div
    class="glass-card p-4 cursor-pointer group hover:border-brand-200 dark:hover:border-brand-800 transition-all duration-200"
    @click="emit('click')"
  >
    <div class="flex items-start justify-between gap-4">
      <div class="flex-1 min-w-0">
        <!-- Title row with status icons -->
        <div class="flex items-center gap-2 mb-1">
          <span v-if="note.is_pinned" class="i-ph-push-pin w-4 h-4 text-brand-500 flex-shrink-0" />
          <span v-if="note.is_archived" class="i-ph-archive-box w-4 h-4 text-amber-500 flex-shrink-0" />
          <h3 class="font-medium text-gray-900 dark:text-gray-100 truncate">
            {{ note.title || 'Untitled' }}
          </h3>
        </div>
        <!-- Content preview (up to 2 lines) -->
        <p class="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-1.5">
          {{ getPreview() }}
        </p>
        <!-- Notebook badge -->
        <div v-if="note.notebook_name" class="flex items-center gap-1 mb-1.5">
          <span class="i-ph-notebook w-3.5 h-3.5 text-brand-400 flex-shrink-0" />
          <span class="text-xs text-brand-500 dark:text-brand-400 truncate">
            {{ note.notebook_name }}
          </span>
        </div>
        <!-- Metadata row: date, deletion countdown, tags -->
        <div class="flex items-center gap-3">
          <span class="text-xs text-gray-400 dark:text-gray-500">
            {{ format(new Date(note.updated_at), 'MMM d, yyyy') }}
          </span>
          <!-- Deletion countdown shown only for archived notes approaching auto-delete -->
          <span
            v-if="deletionCountdown"
            class="text-xs font-medium"
            :class="deletionCountdown.urgent
              ? 'text-red-500 dark:text-red-400'
              : 'text-amber-500 dark:text-amber-400'"
          >
            <span class="i-ph-timer w-3 h-3 inline-block mr-0.5 -mt-0.5" />
            {{ deletionCountdown.text }}
          </span>
          <!-- Show up to 3 tags with a "+N" overflow indicator -->
          <div v-if="note.tags?.length" class="flex gap-1">
            <span
              v-for="tag in note.tags?.slice(0, 3)"
              :key="tag.id"
              class="px-1.5 py-0.5 rounded-full text-xs font-medium"
              :style="{ backgroundColor: tag.color + '20', color: tag.color }"
            >
              {{ tag.name }}
            </span>
            <span v-if="note.tags.length > 3" class="text-xs text-gray-400">
              +{{ note.tags.length - 3 }}
            </span>
          </div>
        </div>
      </div>

      <!-- Hover-revealed action buttons: pin, archive/restore, delete -->
      <div class="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
        <!-- Pin/unpin toggle — rotated icon when unpinned -->
        <button
          class="w-7 h-7 flex items-center justify-center rounded-md transition-colors"
          :class="note.is_pinned
            ? 'text-brand-500 bg-brand-50 dark:bg-brand-900/30'
            : 'text-gray-400 hover:text-brand-500 hover:bg-brand-50 dark:hover:bg-brand-900/20'"
          :title="note.is_pinned ? 'Unpin' : 'Pin'"
          @click.stop="emit('pin')"
        >
          <span class="i-ph-push-pin w-4 h-4" :class="{ 'rotate-45': !note.is_pinned }" />
        </button>
        <!-- Archive/restore toggle — icon changes based on state -->
        <button
          class="w-7 h-7 flex items-center justify-center rounded-md transition-colors"
          :class="note.is_archived
            ? 'text-amber-500 bg-amber-50 dark:bg-amber-900/30'
            : 'text-gray-400 hover:text-amber-500 hover:bg-amber-50 dark:hover:bg-amber-900/20'"
          :title="note.is_archived ? 'Restore' : 'Archive'"
          @click.stop="emit('archive')"
        >
          <span :class="note.is_archived ? 'i-ph-arrow-u-up-left' : 'i-ph-archive-box'" class="w-4 h-4" />
        </button>
        <!-- Delete button -->
        <button
          class="w-7 h-7 flex items-center justify-center rounded-md text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
          title="Delete note"
          @click.stop="emit('delete')"
        >
          <span class="i-ph-trash w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>
