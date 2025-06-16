<template>
    <main class="main" aria-label="Страница регистрации">
        <section class="Secondary__left">
            <div class="Registration__wrapper" role="form" aria-label="Форма регистрации">
                <h2 class="Registration__h2">Регистрация</h2>
                <form @submit.prevent="handleRegister" class="Form_registration" autocomplete="on">
                    <label for="username">Имя пользователя
                        <input v-model="form.username" id="username" type="text" placeholder="Имя пользователя" class="input-field"
                            required aria-required="true" aria-label="Имя пользователя" />
                    </label> 
                    <label for="email">Электронная Почта   
                        <input v-model="form.email" id="email" type="email" placeholder="Почта" class="input-field" required aria-required="true" aria-label="Электронная почта" />
                    </label>
                    <label for="password">Пароль
                        <input v-model="form.password" id="password" type="password" placeholder="Пароль" class="input-field" required aria-required="true" aria-label="Пароль" />
                    </label>
                    <button type="submit" class="button_registration" :disabled="loading" aria-busy="loading">
                        {{ loading ? 'Загрузка...' : 'Зарегистрироваться' }}
                    </button>
                    <p class="login_link">Уже есть аккаунт?
                        <router-link to="/login" aria-label="Войти в аккаунт">Войти</router-link>
                    </p>
                    <p v-if="error" class="error-message" aria-live="polite">{{ error }}</p>
                </form>
            </div>
        </section>
        <aside class="Secondary__right" aria-label="Информация о сервисе">
            <div class="Secondary_right_wrapper">
                <h2 class="h2_secondary_right">Teatral</h2>
                <p class="secondary_right_text">
                    Ваш гид по самым ярким событиям в мире театра.
                </p> 
                <p class="secondary_right_text">
                    Афиша спектаклей, премьеры, билеты и эксклюзивные материалы - всё в одном месте
                </p>
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
            email: '',
            password: '',
        });
        const loading = ref(false);
        const error = ref(null);

        const handleRegister = async () => {
            console.log('Отправляемые данные:', form.value); // Проверяем, что отправляем
            loading.value = true;
            error.value = null;
            try {
                await store.dispatch('auth/register', form.value);
                router.push('/'); // Перенаправление после успешной регистрации
            } catch (err) {
                console.log('Полная ошибка:', err); // Выводим полную ошибку
                console.log('Ответ сервера:', err.response); // Выводим ответ сервера
                error.value = err.response?.data?.error || 'Ошибка регистрации';
            } finally {
                loading.value = false;
            }
        };

        return { form, loading, error, handleRegister };
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
    width: 74vh;
}

.Registration__wrapper {
    background-color: rgb(217, 217, 217, 18%);
    border-radius: 30px;
    display: flex;
    flex-direction: column;
    margin: 10px auto 10px;
    width: 57vh;
    height: 80vh;
}

.Registration__h2 {
    font-size: 52px;
    color: #ffffff;
    font-family: 'Philosopher';
    text-align: center;
    padding: 4%;
}

.Form_registration {
    display: flex;
    flex-direction: column;
    gap: 40px;
}

.input-field {
    padding: 10px;
    margin: 0 auto;
    outline: none;
    border: 4px solid #000000;
    border-radius: 17px;
    background-color: #ffffff;
    color: #000000;
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


.button_registration {
    padding: 15px ;
    border-radius: 10px;
    border: 2px solid #000000;
    background-color: #ffffff;
    font-size: 32px;
    margin: 0 auto;
}

.login_link {
    color: white;
    font-size: 28px;
    margin: 0 auto 50px;
}

a {
    font-size: 28px;
    color: #ffffff;
    text-decoration: underline;
}
.Secondary__right {
    display: flex;
    flex-direction: column;
    width: 100vh;
    
}

.Secondary_right_wrapper {
    background-color: rgb(50, 50, 50, 18%);
    display: flex;
    flex-direction: column;
    text-align: center;
    gap: 50px;
    border-radius: 18px;
    width: 55vh;
    height: 60vh;
    margin: 15% 2% 1% 36%;
}

.h2_secondary_right{
    font-family: 'Philosopher';
    font-size: 52px;
}

.secondary_right_text {
    font-family: 'Philosopher';
    font-size: 40px;
}
.text {
    color: #fff2df;
    font-size: 24px;
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
    .Registration__wrapper {
        margin: 0 auto;
        width: 95vw;
    }
}
</style>