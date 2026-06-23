<script setup lang="ts">
/**
 * @component UiButton
 * @description Reusable button component with variant, size, loading, and disabled states.
 *   Renders a native <button> element with consistent styling.
 *
 * @props variant  - Visual style: 'primary' | 'secondary' | 'ghost' | 'danger' (default: 'secondary')
 * @props size     - Button size: 'sm' | 'md' | 'lg' (default: 'md')
 * @props disabled - Whether the button is disabled (default: false)
 * @props loading  - Whether to show a spinning loader icon (default: false)
 * @props type     - Native button type: 'button' | 'submit' | 'reset' (default: 'button')
 *
 * @emits click - Fired with the native MouseEvent on click
 *
 * @example
 * <UiButton variant="primary" size="md" @click="save">Save</UiButton>
 * <UiButton variant="danger" :loading="isDeleting">Delete</UiButton>
 */
withDefaults(defineProps<{
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  type?: 'button' | 'submit' | 'reset'
}>(), {
  variant: 'secondary',
  size: 'md',
  type: 'button',
})

defineEmits<{
  click: [e: MouseEvent]
}>()
</script>

<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-200',
      'active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100',
      {
        primary: 'bg-brand-500 text-white hover:bg-brand-600 shadow-sm hover:shadow-md',
        secondary: 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700',
        ghost: 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800',
        danger: 'bg-red-500 text-white hover:bg-red-600 shadow-sm',
      }[variant],
      {
        sm: 'px-3 py-1.5 text-sm gap-1.5',
        md: 'px-4 py-2 text-sm gap-2',
        lg: 'px-6 py-3 text-base gap-2.5',
      }[size],
    ]"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="i-ph-circle-notch animate-spin" />
    <slot />
  </button>
</template>
