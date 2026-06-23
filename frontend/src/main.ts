/**
 * @file Application entry point.
 * Creates the Vue app instance, registers Pinia state management and Vue Router,
 * imports global styles (UnoCSS, reset, custom CSS), and mounts the app to #app.
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

import 'virtual:uno.css'
import '@unocss/reset/tailwind.css'
import './assets/styles/global.css'
import './assets/styles/animations.css'

/** Root Vue application instance */
const app = createApp(App)

/** Register Pinia for global state management */
app.use(createPinia())
/** Register Vue Router for page navigation */
app.use(router)

/** Mount the application to the #app DOM element */
app.mount('#app')
