/**
 * @component UiSpinner
 * @description A simple spinning loader icon using the brand color.
 *
 * @props size - Icon size: 'sm' | 'md' | 'lg' (default: 'md')
 *
 * @emits None
 *
 * @example
 * <UiSpinner size="lg" />
 */
<script setup lang="ts">
withDefaults(defineProps<{
  size?: 'sm' | 'md' | 'lg'
}>(), {
  size: 'md',
})
</script>

<template>
  <div class="flex items-center justify-center">
    <span
      :class="[
        'i-ph-circle-notch animate-spin text-brand-500',
        { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-8 h-8' }[size],
      ]"
    />
  </div>
</template>
