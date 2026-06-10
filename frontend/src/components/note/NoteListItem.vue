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
  <div
    class="glass-card p-4 cursor-pointer group hover:border-brand-200 dark:hover:border-brand-800 transition-all duration-200"
    @click="emit('click')"
  >
    <div class="flex items-start justify-between gap-4">
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 mb-1">
          <span v-if="note.is_pinned" class="i-ph-push-pin w-4 h-4 text-brand-500 flex-shrink-0" />
          <span v-if="note.is_archived" class="i-ph-archive-box w-4 h-4 text-amber-500 flex-shrink-0" />
          <h3 class="font-medium text-gray-900 dark:text-gray-100 truncate">
            {{ note.title || 'Untitled' }}
          </h3>
        </div>
        <p class="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-1.5">
          {{ getPreview() }}
        </p>
        <div v-if="note.notebook_name" class="flex items-center gap-1 mb-1.5">
          <span class="i-ph-notebook w-3.5 h-3.5 text-brand-400 flex-shrink-0" />
          <span class="text-xs text-brand-500 dark:text-brand-400 truncate">
            {{ note.notebook_name }}
          </span>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-xs text-gray-400 dark:text-gray-500">
            {{ format(new Date(note.updated_at), 'MMM d, yyyy') }}
          </span>
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

      <!-- Action buttons -->
      <div class="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
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
