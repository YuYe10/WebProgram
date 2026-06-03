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
