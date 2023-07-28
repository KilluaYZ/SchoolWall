import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import 'element-plus/dist/index.css';
import ElementPlus from 'element-plus';
import router from './router'
import store from './store'

createApp(App).use(store).use(router).use(ElementPlus).mount('#app')


