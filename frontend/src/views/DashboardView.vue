<script setup lang="ts">
/**
 * @component DashboardView
 * @description Main dashboard view displaying the user's notebooks in a responsive grid.
 * Provides notebook creation via a modal dialog with customizable name, color, and icon.
 * Key features:
 * - Responsive notebook grid with skeleton loading states
 * - Empty state with call-to-action when no notebooks exist
 * - Create notebook modal with color and icon pickers
 * - Staggered entrance animation for notebook cards
 * 
 * 主仪表板视图，以响应式网格显示用户的笔记本。
 * 通过模态对话框提供笔记本创建功能，支持自定义名称、颜色和图标。
 * 主要特性：
 * - 带骨架加载状态的响应式笔记本网格
 * - 无笔记本时的空状态与操作提示
 * - 带颜色和图标选择器的创建笔记本模态框
 * - 笔记本卡片的交错入场动画
 *
 * @dependencies
 * - useNotebooksStore: manages notebook data and CRUD operations
 *                      管理笔记本数据和CRUD操作
 * - useUiStore: displays toast notifications
 *               显示Toast通知
 * - UiButton, UiModal, UiInput, UiEmpty, UiSkeleton: shared UI components
 *                                                    共享UI组件
 *
 * @example
 * <DashboardView /> <!-- Rendered at the root "/" route -->
 *                   <!-- 在根路由"/"渲染 -->
 */
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useNotebooksStore } from '@/stores/notebooks'
import { useUiStore } from '@/stores/ui'
import { notebooksApi } from '@/api/notebooks'
import UiButton from '@/components/ui/UiButton.vue'
import UiModal from '@/components/ui/UiModal.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiEmpty from '@/components/ui/UiEmpty.vue'
import UiSkeleton from '@/components/ui/UiSkeleton.vue'

const router = useRouter()
const notebooksStore = useNotebooksStore()
const ui = useUiStore()

/** Whether the create-notebook modal is visible
 * 创建笔记本模态框是否可见
 */
const showCreateModal = ref(false)
/** Name for the new notebook
 * 新笔记本的名称
 */
const newName = ref('')
/** Description for the new notebook
 * 新笔记本的描述
 */
const newDescription = ref('')
/** Selected icon class for the new notebook
 * 新笔记本的选中图标类
 */
const newIcon = ref('i-ph-notebook')
/** Selected color hex for the new notebook
 * 新笔记本的选中颜色十六进制值
 */
const newColor = ref('#6366f1')
/** Whether a notebook creation request is in progress
 * 笔记本创建请求是否正在进行中
 */
const creating = ref(false)

/** Available icon options using Phosphor icon classes
 * 使用Phosphor图标类的可用图标选项
 */
const ICON_OPTIONS = [
  'i-ph-notebook', 'i-ph-book-open', 'i-ph-code', 'i-ph-brain',
  'i-ph-lightbulb', 'i-ph-rocket', 'i-ph-heart', 'i-ph-star',
  'i-ph-flower', 'i-ph-globe', 'i-ph-coffee', 'i-ph-music-notes',
]

/** Available color options as hex values
 * 可用颜色选项（十六进制值）
 */
const COLOR_OPTIONS = [
  '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e',
  '#f97316', '#eab308', '#22c55e', '#14b8a6',
  '#06b6d4', '#3b82f6', '#6b7280', '#1e293b',
]

/** Fetch notebooks when the component mounts
 * 组件挂载时获取笔记本列表
 */
onMounted(() => {
  notebooksStore.fetchNotebooks()
})

/**
 * Creates a new notebook with the current form values.
 * 使用当前表单值创建新笔记本。
 * On success, closes the modal, resets the form, shows a toast,
 * and navigates to the newly created notebook's detail page.
 * 成功时，关闭模态框，重置表单，显示Toast通知，
 * 并导航到新创建的笔记本详情页面。
 */
async function createNotebook() {
  if (!newName.value.trim()) return
  creating.value = true
  try {
    const nb = await notebooksStore.createNotebook({
      name: newName.value.trim(),
      description: newDescription.value.trim() || undefined,
      icon: newIcon.value,
      color: newColor.value,
    })
    showCreateModal.value = false
    newName.value = ''
    newDescription.value = ''
    ui.addToast({ type: 'success', message: 'Notebook created!' })
    router.push({ name: 'notebook-detail', params: { id: nb.id } })
  } catch (e: any) {
    const detail = e.response?.data?.detail || 'Failed to create notebook'
    ui.addToast({ type: 'error', message: detail })
  } finally {
    creating.value = false
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold">Your Notebooks</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Organize your thoughts into notebooks
        </p>
      </div>
      <UiButton variant="primary" @click="showCreateModal = true">
        <span class="i-ph-plus w-5 h-5" />
        New Notebook
      </UiButton>
    </div>

    <!-- Notebooks Grid: show skeleton placeholders while loading -->
    <div v-if="notebooksStore.isLoading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div v-for="i in 8" :key="i" class="glass-card p-6">
        <UiSkeleton width="2.5rem" height="2.5rem" rounded="rounded-xl" class="mb-4" />
        <UiSkeleton width="70%" height="1.25rem" class="mb-2" />
        <UiSkeleton width="90%" height="0.875rem" />
      </div>
    </div>

    <!-- Empty state: no notebooks exist yet -->
    <div v-else-if="notebooksStore.notebooks.length === 0">
      <UiEmpty
        icon="i-ph-notebook"
        title="No notebooks yet"
        description="Create your first notebook to start organizing your notes."
      >
        <UiButton variant="primary" class="mt-4" @click="showCreateModal = true">
          <span class="i-ph-plus w-5 h-5" />
          Create Notebook
        </UiButton>
      </UiEmpty>
    </div>

    <!-- Notebook grid: each card navigates to its detail page -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div
        v-for="(nb, idx) in notebooksStore.notebooks"
        :key="nb.id"
        :style="{ animationDelay: `${idx * 50}ms` }"
        class="glass-card p-6 cursor-pointer group hover:scale-[1.02] transition-all duration-300 bounce-in"
        @click="router.push({ name: 'notebook-detail', params: { id: nb.id } })"
      >
        <!-- Notebook icon with dynamic background color -->
        <div
          class="w-10 h-10 rounded-xl flex items-center justify-center mb-4 transition-transform duration-300 group-hover:scale-110"
          :style="{ backgroundColor: nb.color + '20', color: nb.color }"
        >
          <span :class="nb.icon || 'i-ph-notebook'" class="w-6 h-6" />
        </div>
        <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-1 truncate">
          {{ nb.name }}
        </h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 min-h-[2.5rem]">
          {{ nb.description || 'No description' }}
        </p>
        <div class="flex items-center gap-1 mt-3 text-xs text-gray-400">
          <span class="i-ph-note-pencil w-4 h-4" />
          {{ nb.note_count || 0 }} notes
        </div>
      </div>
    </div>

    <!-- Create Notebook Modal with name, color, and icon pickers -->
    <UiModal v-model:open="showCreateModal" title="New Notebook" size="sm">
      <div class="flex flex-col gap-4">
        <UiInput
          v-model="newName"
          label="Name"
          placeholder="My Notebook"
          icon="i-ph-notebook"
        />
        <!-- Color picker: selected color gets a ring indicator -->
        <div>
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300 block mb-1.5">Color</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="c in COLOR_OPTIONS"
              :key="c"
              :class="['w-7 h-7 rounded-full transition-transform', newColor === c ? 'scale-125 ring-2 ring-offset-2 ring-gray-400 dark:ring-offset-gray-900' : 'hover:scale-110']"
              :style="{ backgroundColor: c }"
              @click="newColor = c"
            />
          </div>
        </div>
        <!-- Icon picker: selected icon gets a brand highlight -->
        <div>
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300 block mb-1.5">Icon</label>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="icon in ICON_OPTIONS"
              :key="icon"
              :class="[
                'w-8 h-8 flex items-center justify-center rounded-lg transition-all',
                newIcon === icon
                  ? 'bg-brand-100 dark:bg-brand-900/40 text-brand-600 dark:text-brand-400 ring-1 ring-brand-300'
                  : 'text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800',
              ]"
              @click="newIcon = icon"
            >
              <span :class="icon" class="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      <template #footer>
        <UiButton variant="ghost" @click="showCreateModal = false">Cancel</UiButton>
        <UiButton variant="primary" :loading="creating" @click="createNotebook">Create</UiButton>
      </template>
    </UiModal>
  </div>
</template>
