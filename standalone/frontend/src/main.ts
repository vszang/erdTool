import './assets/main.css'
import { createApp } from 'vue'
import App from './App.vue'
import { applyCssVars } from './store/colors'

applyCssVars()
createApp(App).mount('#app')
