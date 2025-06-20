<template>
  <div>
    <AppHeader></AppHeader>
    <router-view></router-view>
    <ErrorTestComponent v-if="isDevelopment" />
  </div>
</template>

<script>
import './assets/css/reset.css';
import './assets/css/fonts.css'
import AppHeader from './components/AppHeader.vue';
import { mapActions } from 'vuex';
import ErrorTestComponent from './components/ErrorTestComponent.vue';

export default {
  name: 'App',
  components: {
    AppHeader,
    ErrorTestComponent
  },
  data() {
    return {
      isDevelopment: process.env.NODE_ENV === 'development'
    }
  },
  methods: {
    ...mapActions('auth', ['loadUser']),
  },
  async created() {
    console.log('App created - проверка авторизации');
    // Загружаем данные пользователя, если есть токен
    await this.loadUser();
  }
}
</script>
<style>
body{ 
  width: 100%;
  height: 100%;
  background-image: url('./assets/Bad_img.webp');
  background-size: cover; /* или contain, или конкретные размеры */
  background-repeat: no-repeat;
}
</style>