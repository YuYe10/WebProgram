<script setup lang="ts">
/**
 * @component LoginView
 * @description Login form view for user authentication.
 * Submits email and password credentials to the auth store.
 * On success, the auth store handles redirect to the dashboard.
 * 
 * 用户认证的登录表单视图。
 * 将邮箱和密码凭证提交到认证状态管理。
 * 成功时，认证状态管理处理重定向到仪表板。
 *
 * Key features:
 * - Email and password input fields with validation
 *   带验证的邮箱和密码输入字段
 * - Error message display from API responses
 *   显示API响应的错误消息
 * - Loading state during authentication
 *   认证期间的加载状态
 * - Link to the registration page
 *   指向注册页面的链接
 *
 * @dependencies
 * - useAuthStore: handles login API call and auth state
 *                 处理登录API调用和认证状态
 * - useUiStore: displays welcome toast on success
 *               成功时显示欢迎Toast
 * - UiButton, UiInput: shared UI components
 *                      共享UI组件
 *
 * @example
 * <!-- Route: /auth/login -->
 * <!-- 路由: /auth/login -->
 * <LoginView />
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import UiButton from '@/components/ui/UiButton.vue'
import UiInput from '@/components/ui/UiInput.vue'

const router = useRouter()
const auth = useAuthStore()
const ui = useUiStore()

/** User email input
 * 用户邮箱输入
 */
const email = ref('')
/** User password input
 * 用户密码输入
 */
const password = ref('')
/** Whether the login request is in progress
 * 登录请求是否正在进行中
 */
const isLoading = ref(false)
/** Error message from validation or API response
 * 验证或API响应的错误消息
 */
const error = ref('')

/**
 * Handles form submission: validates required fields,
 * calls the auth store's login method, and displays
 * a welcome toast on success or an error message on failure.
 * 处理表单提交：验证必填字段，
 * 调用认证状态管理的登录方法，
 * 成功时显示欢迎Toast，失败时显示错误消息。
 */
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

    <!-- Login form with email, password, error display, and submit button -->
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

      <!-- Error message display -->
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

    <!-- Link to registration page -->
    <p class="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
      Don't have an account?
      <router-link to="/auth/register" class="text-brand-500 hover:text-brand-600 font-medium">
        Sign up
      </router-link>
    </p>
  </div>
</template>
