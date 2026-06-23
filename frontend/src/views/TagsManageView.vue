<script setup lang="ts">
/**
 * @component TagsManageView
 * @description Tag management view providing full CRUD operations for tags.
 * Tags are used to categorize and filter notes across notebooks.
 * 
 * 标签管理视图，提供标签的完整CRUD操作。
 * 标签用于在笔记本之间对笔记进行分类和过滤。
 *
 * Key features:
 * - Create tags with name and color
 *   创建带名称和颜色的标签
 * - Edit existing tag name and color with live preview
 *   编辑现有标签名称和颜色，带实时预览
 * - Delete tags with confirmation (removes from all notes)
 *   带确认的标签删除（从所有笔记中移除）
 * - Click a tag to navigate to filtered notes view
 *   点击标签导航到过滤后的笔记视图
 * - Color picker with preset palette
 *   预设调色板的颜色选择器
 *
 * @dependencies
 * - useTagsStore: tag data and CRUD operations
 *                 标签数据和CRUD操作
 * - useUiStore: toast notifications
 *               Toast通知
 * - UiButton, UiModal, UiInput, UiEmpty: shared UI components
 *                                       共享UI组件
 *
 * @example
 * <!-- Route: /tags -->
 * <!-- 路由: /tags -->
 * <TagsManageView />
 */
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTagsStore } from '@/stores/tags'
import { useUiStore } from '@/stores/ui'
import type { Tag } from '@/types/tag'
import UiButton from '@/components/ui/UiButton.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiEmpty from '@/components/ui/UiEmpty.vue'

const router = useRouter()
const tagsStore = useTagsStore()
const ui = useUiStore()

/** Whether the create-tag modal is visible
 * 创建标签模态框是否可见
 */
const showCreateModal = ref(false)
/** Whether the edit-tag modal is visible
 * 编辑标签模态框是否可见
 */
const showEditModal = ref(false)
/** The tag currently being edited
 * 当前正在编辑的标签
 */
const editingTag = ref<Tag | null>(null)
/** Create form: new tag name
 * 创建表单：新标签名称
 */
const newTagName = ref('')
/** Create form: new tag color
 * 创建表单：新标签颜色
 */
const newTagColor = ref('#a855f7')
/** Edit form: tag name
 * 编辑表单：标签名称
 */
const editTagName = ref('')
/** Edit form: tag color
 * 编辑表单：标签颜色
 */
const editTagColor = ref('#a855f7')
/** Whether a tag creation request is in progress
 * 标签创建请求是否正在进行中
 */
const creating = ref(false)
/** Whether a tag update request is in progress
 * 标签更新请求是否正在进行中
 */
const updating = ref(false)

/** Preset color palette for tag creation and editing
 * 标签创建和编辑的预设调色板
 */
const TAG_COLORS = ['#a855f7', '#6366f1', '#3b82f6', '#06b6d4', '#22c55e', '#eab308', '#f97316', '#ef4444', '#ec4899']

/** Fetch tags on mount
 * 挂载时获取标签
 */
onMounted(() => tagsStore.fetchTags())

// ── Create tag ──

/**
 * Creates a new tag with the provided name and color.
 * 使用提供的名称和颜色创建新标签。
 * Resets the form and closes the modal on success.
 * 成功时重置表单并关闭模态框。
 */
async function createTag() {
  if (!newTagName.value.trim()) return
  creating.value = true
  try {
    await tagsStore.createTag({ name: newTagName.value.trim(), color: newTagColor.value })
    showCreateModal.value = false
    newTagName.value = ''
    newTagColor.value = '#a855f7'
    ui.addToast({ type: 'success', message: 'Tag created' })
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to create tag' })
  } finally {
    creating.value = false
  }
}

// ── Edit tag ──

/**
 * Opens the edit modal, pre-filling the form with the tag's current values.
 * 打开编辑模态框，用标签当前值预填充表单。
 * @param tag - The tag to edit
 *              要编辑的标签
 */
function openEditModal(tag: Tag) {
  editingTag.value = tag
  editTagName.value = tag.name
  editTagColor.value = tag.color
  showEditModal.value = true
}

/**
 * Updates the tag being edited with the new name and color.
 * 用新名称和颜色更新正在编辑的标签。
 * Closes the modal on success.
 * 成功时关闭模态框。
 */
async function updateTag() {
  if (!editTagName.value.trim() || !editingTag.value) return
  updating.value = true
  try {
    await tagsStore.updateTag(editingTag.value.id, {
      name: editTagName.value.trim(),
      color: editTagColor.value,
    })
    showEditModal.value = false
    editingTag.value = null
    ui.addToast({ type: 'success', message: 'Tag updated' })
  } catch {
    ui.addToast({ type: 'error', message: 'Failed to update tag' })
  } finally {
    updating.value = false
  }
}

// ── Delete tag ──

/**
 * Deletes a tag after user confirmation.
 * 用户确认后删除标签。
 * The tag will be removed from all associated notes.
 * 标签将从所有关联笔记中移除。
 * @param id - The tag ID to delete
 *             要删除的标签ID
 * @param name - The tag name for the confirmation message
 *               确认消息中显示的标签名称
 */
async function deleteTag(id: string, name: string) {
  if (!confirm(`Delete tag "${name}"? It will be removed from all notes.`)) return
  await tagsStore.deleteTag(id)
  ui.addToast({ type: 'info', message: 'Tag deleted' })
}

// ── Navigate to filtered notes ──

/**
 * Navigates to the all-notes view filtered by the given tag.
 * 导航到按给定标签过滤的所有笔记视图。
 * @param tag - The tag to filter by
 *              用于过滤的标签
 */
function viewTaggedNotes(tag: Tag) {
  router.push({ name: 'all-notes', query: { tag_id: tag.id } })
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

    <!-- Empty state -->
    <div v-if="tagsStore.tags.length === 0 && !tagsStore.isLoading">
      <UiEmpty icon="i-ph-tag" title="No tags" description="Create tags to categorize your notes." />
    </div>

    <!-- Tag list: each row shows color dot, name, note count, and edit/delete buttons -->
    <div v-else class="space-y-2">
      <div
        v-for="tag in tagsStore.tags"
        :key="tag.id"
        class="glass-card p-4 flex items-center justify-between group cursor-pointer hover:border-brand-200 dark:hover:border-brand-800 transition-all duration-200"
        @click="viewTaggedNotes(tag)"
      >
        <div class="flex items-center gap-3">
          <div
            class="w-4 h-4 rounded-full flex-shrink-0"
            :style="{ backgroundColor: tag.color, boxShadow: '0 0 0 2px ' + tag.color + '40' }"
          />
          <div>
            <span class="font-medium">{{ tag.name }}</span>
            <span class="ml-2 text-xs text-gray-400">{{ tag.note_count || 0 }} notes</span>
          </div>
        </div>

        <div class="flex items-center gap-0.5">
          <span class="text-xs text-gray-400 mr-2 opacity-0 group-hover:opacity-100 transition-opacity">
            Click to view notes
          </span>
          <button
            class="w-7 h-7 flex items-center justify-center rounded-md text-gray-400 hover:text-brand-500 hover:bg-brand-50 dark:hover:bg-brand-900/30 transition-colors"
            title="Edit tag"
            @click.stop="openEditModal(tag)"
          >
            <span class="i-ph-pencil-simple w-4 h-4" />
          </button>
          <button
            class="w-7 h-7 flex items-center justify-center rounded-md text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
            title="Delete tag"
            @click.stop="deleteTag(tag.id, tag.name)"
          >
            <span class="i-ph-trash w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- ── Create Tag Modal ── -->
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

    <!-- ── Edit Tag Modal ── -->
    <UiModal v-model:open="showEditModal" title="Edit Tag" size="sm">
      <div class="flex flex-col gap-4">
        <UiInput v-model="editTagName" label="Tag Name" placeholder="Tag name" />
        <div>
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300 block mb-1.5">Color</label>
          <div class="flex gap-2">
            <button
              v-for="c in TAG_COLORS"
              :key="c"
              :class="['w-7 h-7 rounded-full transition-transform', editTagColor === c ? 'scale-125 ring-2 ring-offset-2 ring-gray-400 dark:ring-offset-gray-900' : 'hover:scale-110']"
              :style="{ backgroundColor: c }"
              @click="editTagColor = c"
            />
          </div>
        </div>
        <!-- Preview -->
        <div class="flex items-center gap-2 p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
          <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: editTagColor }" />
          <span class="text-sm font-medium">{{ editTagName || 'Preview' }}</span>
        </div>
      </div>
      <template #footer>
        <UiButton variant="ghost" @click="showEditModal = false">Cancel</UiButton>
        <UiButton variant="primary" :loading="updating" @click="updateTag">Save</UiButton>
      </template>
    </UiModal>
  </div>
</template>
