<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useTagsStore } from '@/stores/tags'
import { useUiStore } from '@/stores/ui'
import UiButton from '@/components/ui/UiButton.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiEmpty from '@/components/ui/UiEmpty.vue'

const tagsStore = useTagsStore()
const ui = useUiStore()
const showCreateModal = ref(false)
const newTagName = ref('')
const newTagColor = ref('#a855f7')
const creating = ref(false)

const TAG_COLORS = ['#a855f7', '#6366f1', '#3b82f6', '#06b6d4', '#22c55e', '#eab308', '#f97316', '#ef4444', '#ec4899']

onMounted(() => tagsStore.fetchTags())

async function createTag() {
  if (!newTagName.value.trim()) return
  creating.value = true
  try {
    await tagsStore.createTag({ name: newTagName.value.trim(), color: newTagColor.value })
    showCreateModal.value = false
    newTagName.value = ''
    ui.addToast({ type: 'success', message: 'Tag created' })
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to create tag' })
  } finally {
    creating.value = false
  }
}

async function deleteTag(id: string, name: string) {
  if (!confirm(`Delete tag "${name}"?`)) return
  await tagsStore.deleteTag(id)
  ui.addToast({ type: 'info', message: 'Tag deleted' })
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold">Tags</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Organize your notes with tags</p>
      </div>
      <UiButton variant="primary" @click="showCreateModal = true">
        <span class="i-ph-plus w-5 h-5" /> New Tag
      </UiButton>
    </div>

    <div v-if="tagsStore.tags.length === 0">
      <UiEmpty icon="i-ph-tag" title="No tags" description="Create tags to categorize your notes." />
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="tag in tagsStore.tags"
        :key="tag.id"
        class="glass-card p-4 flex items-center justify-between group"
      >
        <div class="flex items-center gap-3">
          <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: tag.color }" />
          <span class="font-medium">{{ tag.name }}</span>
          <span class="text-xs text-gray-400">{{ tag.note_count || 0 }} notes</span>
        </div>
        <button
          class="w-7 h-7 flex items-center justify-center rounded-md text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors opacity-0 group-hover:opacity-100"
          @click="deleteTag(tag.id, tag.name)"
        >
          <span class="i-ph-trash w-4 h-4" />
        </button>
      </div>
    </div>

    <UiModal v-model:open="showCreateModal" title="New Tag" size="sm">
      <div class="flex flex-col gap-4">
        <UiInput v-model="newTagName" label="Tag Name" placeholder="e.g. important" />
        <div>
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300 block mb-1.5">Color</label>
          <div class="flex gap-2">
            <button
              v-for="c in TAG_COLORS"
              :key="c"
              :class="['w-7 h-7 rounded-full transition-transform', newTagColor === c ? 'scale-125 ring-2 ring-offset-2 ring-gray-400 dark:ring-offset-gray-900' : 'hover:scale-110']"
              :style="{ backgroundColor: c }"
              @click="newTagColor = c"
            />
          </div>
        </div>
      </div>
      <template #footer>
        <UiButton variant="ghost" @click="showCreateModal = false">Cancel</UiButton>
        <UiButton variant="primary" :loading="creating" @click="createTag">Create</UiButton>
      </template>
    </UiModal>
  </div>
</template>
