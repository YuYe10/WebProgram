<script setup lang="ts">
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()
</script>

<template>
  <div class="fixed top-4 right-4 z-100 flex flex-col gap-2 pointer-events-none">
    <transition-group name="slide-in-right" tag="div" class="flex flex-col gap-2">
      <div
        v-for="toast in ui.toasts"
        :key="toast.id"
        :class="[
          'pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg backdrop-blur-xl border text-sm font-medium max-w-sm cursor-pointer',
          {
            success: 'bg-emerald-50/90 dark:bg-emerald-900/80 border-emerald-200 dark:border-emerald-700 text-emerald-800 dark:text-emerald-100',
            error: 'bg-red-50/90 dark:bg-red-900/80 border-red-200 dark:border-red-700 text-red-800 dark:text-red-100',
            info: 'bg-blue-50/90 dark:bg-blue-900/80 border-blue-200 dark:border-blue-700 text-blue-800 dark:text-blue-100',
            warning: 'bg-amber-50/90 dark:bg-amber-900/80 border-amber-200 dark:border-amber-700 text-amber-800 dark:text-amber-100',
          }[toast.type],
        ]"
        @click="ui.removeToast(toast.id)"
      >
        <span
          :class="[
            'w-5 h-5 flex-shrink-0',
            {
              success: 'i-ph-check-circle text-emerald-500',
              error: 'i-ph-x-circle text-red-500',
              info: 'i-ph-info text-blue-500',
              warning: 'i-ph-warning text-amber-500',
            }[toast.type],
          ]"
        />
        <span>{{ toast.message }}</span>
      </div>
    </transition-group>
  </div>
</template>
