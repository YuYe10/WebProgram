/**
 * @component UiModal
 * @description A modal dialog teleported to the body, with backdrop, Escape-to-close,
 *   title bar, body slot, and optional footer slot. Manages body scroll lock while open.
 *
 * @props open  - Whether the modal is visible (supports v-model:open)
 * @props title - Optional title displayed in the modal header
 * @props size  - Width preset: 'sm' | 'md' | 'lg' (default: 'md')
 *
 * @emits update:open - Emitted with `false` when the modal should close (v-model support)
 * @emits close       - Emitted when the modal is closed (backdrop click, Escape, or X button)
 *
 * @example
 * <UiModal v-model:open="showDialog" title="Confirm" size="sm">
 *   <p>Are you sure?</p>
 *   <template #footer>
 *     <UiButton @click="showDialog = false">Cancel</UiButton>
 *     <UiButton variant="primary" @click="confirm">Confirm</UiButton>
 *   </template>
 * </UiModal>
 */
<script setup lang="ts">
import { watch } from 'vue'

const props = withDefaults(defineProps<{
  open: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg'
}>(), {
  size: 'md',
})

const emit = defineEmits<{
  'update:open': [value: boolean]
  close: []
}>()

/** Closes the modal by emitting both update:open and close events */
function close() {
  emit('update:open', false)
  emit('close')
}

/** Closes the modal on Escape key press */
function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') close()
}

/**
 * Watches the `open` prop to register/unregister the Escape listener
 * and toggle body scroll lock.
 */
watch(() => props.open, (val) => {
  if (val) {
    document.addEventListener('keydown', onKeydown)
    document.body.style.overflow = 'hidden'
  } else {
    document.removeEventListener('keydown', onKeydown)
    document.body.style.overflow = ''
  }
})
</script>

<template>
  <Teleport to="body">
    <transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
        @click.self="close"
      >
        <transition name="scale">
          <div
            v-if="open"
            :class="[
              'relative w-full rounded-xl glass shadow-xl',
              {
                sm: 'max-w-sm',
                md: 'max-w-md',
                lg: 'max-w-lg',
              }[size],
            ]"
          >
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h3 class="text-lg font-semibold">{{ title }}</h3>
              <button
                class="p-1 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                @click="close"
              >
                <span class="i-ph-x w-5 h-5" />
              </button>
            </div>
            <div class="px-6 py-4">
              <slot />
            </div>
            <div v-if="$slots.footer" class="flex justify-end gap-3 px-6 py-4 border-t border-gray-200 dark:border-gray-700">
              <slot name="footer" />
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </Teleport>
</template>
