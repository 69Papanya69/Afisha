// src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from './router.js';
import store from './store'; // Импортируй store
import './assets/css/fonts.css';
import toastPlugin from './plugins/toast';
import { hawkPlugin } from './plugins/hawk';

// Проверка инициализации Hawk в режиме разработки
if (process.env.NODE_ENV === 'development') {
  import('./check-hawk');
}

const app = createApp(App);
app.use(store);
app.use(router);
app.use(toastPlugin);
app.use(hawkPlugin); // Initialize Hawk error tracking
app.mount('#app');