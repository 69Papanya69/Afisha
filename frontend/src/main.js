// src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from './router.js';
import store from './store'; // Импортируй store
import './assets/css/fonts.css';
import toastPlugin from './plugins/toast';

const app = createApp(App);
app.use(store);
app.use(router);
app.use(toastPlugin);
app.mount('#app');