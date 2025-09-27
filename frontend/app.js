// Vue entry wrapper (Vue mount) — this file replaces the old DOM-manipulating script.
// It simply mounts the Vue application (App.vue). The full Phone List logic
// lives in `src/views/Home.vue` as a proper Vue component.

import { createApp } from 'vue'
import App from './src/App.vue'
import router from './src/router'
import './src/style.css'

createApp(App).use(router).mount('#app')
