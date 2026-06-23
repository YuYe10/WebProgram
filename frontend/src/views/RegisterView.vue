<script setup lang="ts">
/**
 * @component RegisterView
 * @description Registration form view for creating a new user account.
 * Validates required fields, password match, and minimum length before submission.
 * On success, the auth store handles redirect to the dashboard.
 *
 * Key features:
 * - Username, email, optional display name, and password fields
 * - Client-side validation: required fields, password match, min length
 * - Error message display from API responses
 * - Loading state during registration
 * - Link to the login page
 *
 * @dependencies
 * - useAuthStore: handles register API call and auth state
 * - useUiStore: displays success toast
 * - UiButton, UiInput: shared UI components
 *
 * @example
 * <!-- Route: /auth/register -->
 * <RegisterView />
 */
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'

const auth = useAuthStore()
const ui = useUiStore()

/** Desired username */
const username = ref('')
/** User email address */
const email = ref('')
/** Desired password */
const password = ref('')
/** Password confirmation for match validation */
const confirmPassword = ref('')
/** Optional display name */
const displayName = ref('')
/** Whether the registration request is in progress */
const isLoading = ref(false)
/** Error message from validation or API response */
const error = ref('')

/**
 * Handles form submission: validates required fields, password match,
 * and minimum password length, then calls the auth store's register method.
 * Displays a success toast or error message accordingly.
 */
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

    <!-- Registration form with validation and error display -->
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

      <!-- Error message display -->
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

    <!-- Link to login page -->
    <p class="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
      Already have an account?
      <router-link to="/auth/login" class="text-brand-500 hover:text-brand-600 font-medium">
        Sign in
      </router-link>
    </p>
  </div>
</template>
