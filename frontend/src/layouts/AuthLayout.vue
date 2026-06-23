/**
 * @component AuthLayout
 * @description Full-screen centered layout for authentication pages (login, register).
 *   Features decorative gradient blobs, the app logo, a glass-card content area,
 *   and a tagline footer.
 *
 * @props None
 *
 * @emits None
 *
 * @example
 * <!-- Used as a route layout wrapping auth pages -->
 * <AuthLayout />
 */
<script setup lang="ts">
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center p-4 relative overflow-hidden bg-gray-50 dark:bg-gray-950">
    <!-- Decorative background -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-brand-200/30 dark:bg-brand-800/20 blur-3xl" />
      <div class="absolute -bottom-40 -left-40 w-96 h-96 rounded-full bg-purple-200/30 dark:bg-purple-800/20 blur-3xl" />
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-blue-100/20 dark:bg-blue-900/10 blur-3xl" />
    </div>

    <!-- Logo -->
    <div class="relative mb-8 flex items-center gap-3">
      <div class="w-10 h-10 rounded-xl bg-brand-500 flex items-center justify-center shadow-lg shadow-brand-500/25">
        <span class="i-ph-notepad w-6 h-6 text-white" />
      </div>
      <span class="font-bold text-2xl tracking-tight">Noteworthy</span>
    </div>

    <!-- Card -->
    <div class="relative w-full max-w-md glass-card p-8">
      <router-view />
    </div>

    <!-- Footer -->
    <p class="relative mt-6 text-xs text-gray-400 dark:text-gray-600">
      Lightweight online notes, beautifully crafted.
    </p>
  </div>
</template>
