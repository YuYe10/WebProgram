<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'

const auth = useAuthStore()
const ui = useUiStore()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const displayName = ref('')
const isLoading = ref(false)
const error = ref('')

async function handleSubmit() {
  error.value = ''

  if (!username.value || !email.value || !password.value) {
    error.value = 'Please fill in all required fields'
    return
  }
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }
  if (password.value.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }

  isLoading.value = true
  try {
    await auth.register({
      username: username.value,
      email: email.value,
      password: password.value,
      display_name: displayName.value || undefined,
    })
    ui.addToast({ type: 'success', message: 'Account created successfully!' })
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Registration failed'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-1">Create account</h2>
    <p class="text-sm text-gray-500 dark:text-gray-400 mb-6">
      Start your note-taking journey
    </p>

    <form @submit.prevent="handleSubmit" class="flex flex-col gap-4">
      <UiInput
        v-model="username"
        label="Username"
        placeholder="Choose a username"
        icon="i-ph-user"
      />
      <UiInput
        v-model="email"
        label="Email"
        type="email"
        placeholder="you@example.com"
        icon="i-ph-envelope"
      />
      <UiInput
        v-model="displayName"
        label="Display Name (optional)"
        placeholder="How should we call you?"
        icon="i-ph-identification-card"
      />
      <UiInput
        v-model="password"
        label="Password"
        type="password"
        placeholder="At least 6 characters"
        icon="i-ph-lock"
      />
      <UiInput
        v-model="confirmPassword"
        label="Confirm Password"
        type="password"
        placeholder="Repeat your password"
        icon="i-ph-lock-key"
      />

      <p v-if="error" class="text-sm text-red-500">{{ error }}</p>

      <UiButton
        variant="primary"
        size="lg"
        type="submit"
        :loading="isLoading"
        class="w-full mt-2"
      >
        Create Account
      </UiButton>
    </form>

    <p class="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
      Already have an account?
      <router-link to="/auth/login" class="text-brand-500 hover:text-brand-600 font-medium">
        Sign in
      </router-link>
    </p>
  </div>
</template>
