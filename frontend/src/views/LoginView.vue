<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'

const router = useRouter()
const auth = useAuthStore()
const ui = useUiStore()

const email = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')

async function handleSubmit() {
  if (!email.value || !password.value) {
    error.value = 'Please fill in all fields'
    return
  }
  isLoading.value = true
  error.value = ''
  try {
    await auth.login({ email: email.value, password: password.value })
    ui.addToast({ type: 'success', message: 'Welcome back!' })
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Login failed'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-1">Welcome back</h2>
    <p class="text-sm text-gray-500 dark:text-gray-400 mb-6">
      Sign in to continue to your notes
    </p>

    <form @submit.prevent="handleSubmit" class="flex flex-col gap-4">
      <UiInput
        v-model="email"
        label="Email"
        type="email"
        placeholder="you@example.com"
        icon="i-ph-envelope"
      />
      <UiInput
        v-model="password"
        label="Password"
        type="password"
        placeholder="Enter your password"
        icon="i-ph-lock"
      />

      <p v-if="error" class="text-sm text-red-500">{{ error }}</p>

      <UiButton
        variant="primary"
        size="lg"
        type="submit"
        :loading="isLoading"
        class="w-full mt-2"
      >
        Sign In
      </UiButton>
    </form>

    <p class="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
      Don't have an account?
      <router-link to="/auth/register" class="text-brand-500 hover:text-brand-600 font-medium">
        Sign up
      </router-link>
    </p>
  </div>
</template>
