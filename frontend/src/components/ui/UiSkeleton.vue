/**
 * @component UiSkeleton
 * @description A lightweight skeleton placeholder for loading states.
 *   Renders a pulsing rectangle with configurable dimensions and border radius.
 *
 * 用于加载状态的轻量级骨架占位组件。渲染一个带有脉冲动画的矩形，尺寸和边框半径可配置。
 *
 * @props width   - CSS width value (default: '100%')
 *                  CSS宽度值（默认：'100%'）
 * @props height  - CSS height value (default: '1rem')
 *                  CSS高度值（默认：'1rem'）
 * @props rounded - Tailwind border-radius class (default: 'rounded-md')
 *                  Tailwind边框圆角类（默认：'rounded-md'）
 *
 * @emits None
 *        无事件
 *
 * @example
 * <UiSkeleton height="2rem" />
 * <UiSkeleton width="60%" height="1.5rem" rounded="rounded-full" />
 */
<script setup lang="ts">
withDefaults(defineProps<{
  width?: string
  height?: string
  rounded?: string
}>(), {
  width: '100%',
  height: '1rem',
  rounded: 'rounded-md',
})
</script>

<template>
  <div class="skeleton" :style="{ width, height }" :class="rounded" />
</template>
