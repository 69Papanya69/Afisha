<template>
    <main class="main" aria-label="Страница авторизации">
        <section class="Secondary__left">
            <div class="form__wrapper" role="form" aria-label="Форма авторизации">
                <form @submit.prevent="handleLogin" class="auth-form" autocomplete="on">
                    <h2 class="Auth__h2">Авторизация</h2>
                    <label for="login-username">Имя пользователя
                        <input v-model="form.username" id="login-username" type="text" placeholder="Имя пользователя" class="input-field"
                            required aria-required="true" aria-label="Имя пользователя" />
                    </label>
                    <label for="login-password">Пароль
                        <input v-model="form.password" id="login-password" type="password" placeholder="Пароль" class="input-field"
                            required aria-required="true" aria-label="Пароль" />
                    </label>
                    <button type="submit" class="login-button" :disabled="loading" aria-busy="loading">
                        {{ loading ? 'Вход...' : 'Войти' }}
                    </button>
                    <div class="social-buttons">
                        <a href="#" tabindex="0" aria-label="Войти через Google"><img src="../assets/icons8-google.svg" alt="Google" /></a>
                        <a href="#" tabindex="0" aria-label="Войти через VK"><img src="../assets/icons8-vk.svg" alt="VK" /></a>
                    </div>
                    <p class="register-link">Нет аккаунта?
                        <router-link to="/register" aria-label="Зарегистрироваться">Зарегистрироваться</router-link>
                    </p>
                    <p v-if="error" class="error-message" aria-live="polite">{{ error }}</p>
                </form>
            </div>
        </section>
        <aside class="Secondary__right" aria-label="Новости и информация">
            <div class="news" v-for="i in 3" :key="i" tabindex="0" aria-label="Новость">
                <h2>Новость</h2>
                <p></p>
            </div>
        </aside>
    </main>
</template>

<script>
import { ref } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
    setup() {
        const store = useStore();
        const router = useRouter();
        const form = ref({
            username: '',
            password: '',
        });
        const loading = ref(false);
        const error = ref(null);

        const handleLogin = async () => {
            loading.value = true;
            error.value = null;
            try {
                // В процессе входа токены автоматически сохранятся в localStorage (см. store/modules/auth.js)
                await store.dispatch('auth/login', form.value);
                
                console.log('Вход успешен, перенаправляем на профиль...');
                router.push('/profile');
            } catch (err) {
                console.error('Ошибка входа:', err);
                error.value = 'Неверные имя пользователя или пароль';
            } finally {
                loading.value = false;
            }
        };

        return { form, loading, error, handleLogin };
    },
};
</script>

<style scoped>
.main {
    display: flex;
    flex-direction: row;
    gap: 50px;
    justify-content: space-around;
}

.Secondary__left {
    width: 100vh;
}

.form__wrapper {
    margin: 8% 10% 0%;
    background-color: rgb(217, 217, 217, 18%);
    border-radius: 30px;
    width: 57vh;
    height: 70vh;
}


.auth-form {
    display: flex;
    flex-direction: column;
    gap: 30px;
}


.Auth__h2 {
    color: #ffffff;
    font-size: 52px;
    text-align: center;
    padding: 4%;
}

label {
    font-size: 32px;
    color: #ffffff;
    font-family: 'Philosopher';
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.input-field {
    padding: 10px;
    margin: 0 auto;
    outline: none;
    border: 4px solid #000000;
    border-radius: 17px;
    background-color: #ffffff;
    color: #000000;
    width: 72%;
}

a {
    font-size: 28px;
    color: #ffffff;
    text-decoration: underline;
}

.login-button {
    padding: 15px;
    border-radius: 10px;
    border: 2px solid #000000;
    background-color: #ffffff;
    font-size: 32px;
    margin: 0 auto;
    padding: 7px 31px;
}



.social-buttons {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
}

.register-link {
    color: white;
    font-size: 28px;
    margin: 0 auto 50px;
}

.Secondary__right {
    margin-top: 40px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    width: 30%;
}

.news {
    background-color: rgb(217, 217, 217, 18%);
}

@media (max-width: 800px) {
    .main {
        flex-direction: column;
        padding: 10px;
    }
    .Secondary__left, .Secondary__right {
        width: 100%;
        padding: 0;
    }
    .form__wrapper {
        margin: 0 auto;
        width: 95vw;
    }
}
</style>