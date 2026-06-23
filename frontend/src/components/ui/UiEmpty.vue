/**
 * @component UiEmpty
 * @description A centered empty-state placeholder with an icon, title, description,
 *   and an optional default slot for action buttons.
 *
 * 居中的空状态占位组件，包含图标、标题、描述和可选的操作按钮插槽。
 *
 * @props icon        - CSS class for the icon (default: 'i-ph-notepad')
 *                      图标的CSS类（默认：'i-ph-notepad'）
 * @props title       - Heading text (default: 'No items found')
 *                      标题文本（默认：'No items found'）
 * @props description - Subtitle text (default: 'Get started by creating your first item.')
 *                      副标题文本（默认：'Get started by creating your first item.'）
 *
 * @emits None
 *        无事件
 *
 * @example
 * <UiEmpty icon="i-ph-note" title="No notes" description="Create your first note.">
 *   <UiButton variant="primary">New Note</UiButton>
 * </UiEmpty>
 */
<script setup lang="ts">
withDefaults(defineProps<{
  icon?: string
  title?: string
  description?: string
}>(), {
  icon: 'i-ph-notepad',
  title: 'No items found',
  description: 'Get started by creating your first item.',
})
</script>

<template>
  <div class="flex flex-col items-center justify-center py-16 px-4 text-center">
    <div class="w-20 h-20 rounded-2xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-4 float">
      <span :class="icon" class="w-10 h-10 text-gray-400 dark:text-gray-500" />
    </div>
    <h3 class="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-1">{{ title }}</h3>
    <p class="text-sm text-gray-500 dark:text-gray-400 max-w-xs">{{ description }}</p>
    <slot />
  </div>
</template>
