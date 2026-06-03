<script setup lang="ts">
withDefaults(defineProps<{
  modelValue: string
  label?: string
  placeholder?: string
  type?: string
  error?: string
  disabled?: boolean
  icon?: string
}>(), {
  type: 'text',
})

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <div class="flex flex-col gap-1.5">
    <label v-if="label" class="text-sm font-medium text-gray-700 dark:text-gray-300">
      {{ label }}
    </label>
    <div class="relative">
      <span
        v-if="icon"
        :class="icon"
        class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4"
      />
      <input
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :class="[
          'w-full rounded-lg border px-3 py-2 text-sm transition-all duration-200 outline-none',
          'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100',
          'placeholder:text-gray-400 dark:placeholder:text-gray-500',
          icon ? 'pl-10' : '',
          error
            ? 'border-red-300 dark:border-red-600 focus:ring-2 focus:ring-red-500/20 focus:border-red-500'
            : 'border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500',
        ]"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      />
    </div>
    <p v-if="error" class="text-xs text-red-500">{{ error }}</p>
  </div>
</template>
