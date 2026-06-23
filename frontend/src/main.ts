/**
 * @file Application entry point.
 * Creates the Vue app instance, registers Pinia state management and Vue Router,
 * imports global styles (UnoCSS, reset, custom CSS), and mounts the app to #app.
 * 
 * 应用程序入口点。
 * 创建Vue应用实例，注册Pinia状态管理和Vue Router，
 * 导入全局样式（UnoCSS、重置样式、自定义CSS），并将应用挂载到#app。
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

import 'virtual:uno.css'
import '@unocss/reset/tailwind.css'
import './assets/styles/global.css'
import './assets/styles/animations.css'

/** Root Vue application instance
 * 根Vue应用实例
 */
const app = createApp(App)

/** Register Pinia for global state management
 * 注册Pinia用于全局状态管理
 */
app.use(createPinia())
/** Register Vue Router for page navigation
 * 注册Vue Router用于页面导航
 */
app.use(router)

/** Mount the application to the #app DOM element
 * 将应用挂载到#app DOM元素
 */
app.mount('#app')
