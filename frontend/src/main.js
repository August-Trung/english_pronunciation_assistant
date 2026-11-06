/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Composables
import { createApp } from 'vue'
import { registerPlugins } from '@/plugins'
import router from '@/router'
import '@/styles/kids-theme.scss'
import App from './App.vue'

const app = createApp(App)
registerPlugins(app)
app.use(router)
app.mount('#app')
