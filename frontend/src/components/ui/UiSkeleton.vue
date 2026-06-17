/**
 * @component UiSkeleton
 * @description A lightweight skeleton placeholder for loading states.
 *   Renders a pulsing rectangle with configurable dimensions and border radius.
 *
 * @props width   - CSS width value (default: '100%')
 * @props height  - CSS height value (default: '1rem')
 * @props rounded - Tailwind border-radius class (default: 'rounded-md')
 *
 * @emits None
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
