<template>
    <nav class="navbar" aria-label="Главная навигация">
        <router-link to="/general" class="logo" aria-label="На главную страницу">Teatral</router-link>
        <div class="nav-links" role="menubar">
            <router-link to="/catalog" class="nav-item" role="menuitem" tabindex="0" aria-label="Каталог спектаклей">Каталог</router-link>
            <router-link v-if="isAdmin" to="/admin/products" class="nav-item" role="menuitem" tabindex="0" aria-label="Админ-панель">Админ</router-link>
            <router-link v-if="isAdmin" to="/hawk-test" class="nav-item hawk-test-link" role="menuitem" tabindex="0" aria-label="Тестирование Hawk">
                <span class="hawk-icon">🦅</span> Hawk
            </router-link>
            <router-link
                v-if="isAuthenticated"
                to="/cart"
                class="nav-item cart-item"
                role="menuitem"
                tabindex="0"
                aria-label="Корзина покупок"
            >
                <i class="fas fa-shopping-cart"></i>
                <span class="cart-count" v-if="cartItemsCount > 0">{{ cartItemsCount }}</span>
            </router-link>
            <router-link
                v-if="isAuthenticated"
                to="/profile"
                class="nav-item"
                role="menuitem"
                tabindex="0"
                aria-label="Профиль пользователя"
            >
                Профиль
            </router-link>
            <router-link
                v-else
                to="/login"
                class="nav-item"
                role="menuitem"
                tabindex="0"
                aria-label="Войти в аккаунт"
            >
                Войти
            </router-link>
        </div>
    </nav>
</template>

<script>
import { computed, onMounted } from 'vue';
import { useStore } from 'vuex';

export default {
    name: "AppHeader",
    setup() {
        const store = useStore();
        const isAuthenticated = computed(() => store.getters['auth/isAuthenticated']);
        const user = computed(() => store.state.auth.user);
        const cartItemsCount = computed(() => store.getters['cart/cartItemsCount'] || 0);
        const isAdmin = computed(() => {
            return user.value && (user.value.is_admin || user.value.is_superuser || user.value.is_staff);
        });

        // Автоматически подгружать пользователя при монтировании
        onMounted(async () => {
            if (isAuthenticated.value) {
                try {
                    // Просто загружаем данные пользователя из токена
                    await store.dispatch('auth/loadUser');
                    // Загружаем содержимое корзины
                    await store.dispatch('cart/fetchCartItems');
                } catch (e) {
                    console.error('Ошибка загрузки данных:', e);
                }
            }
        });

        return { isAuthenticated, isAdmin, cartItemsCount };
    },
};
</script>

<style scoped>
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 60px 75px;
    color: #ffffff;
    gap: 200px;
}

.logo {
    font-size: 48px;
    margin-right: 20px;
    font-family: "Vogue";
    letter-spacing: 2px;
    text-decoration: none;
    color: inherit;
}

.nav-links {
    display: flex;
    gap: 120px;
    font-family: 'Philosopher';
    align-items: center; /* Ensure vertical alignment */
}

.nav-item {
    color: #ffffff;
    text-decoration: none;
    font-size: 32px;
}

.nav-item:hover {
    text-decoration: underline;
}

.cart-item {
    position: relative;
}

.cart-count {
    position: absolute;
    top: -10px;
    right: -10px;
    background-color: #ff4081;
    color: white;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 14px;
    font-weight: bold;
}

.hawk-test-link {
    display: flex;
    align-items: center;
    gap: 5px;
    color: #ffd700; /* Gold color for the Hawk link */
}

.hawk-icon {
    font-size: 16px;
}

@media (max-width: 1200px) {
    .navbar {
        gap: 60px;
        padding: 30px 20px;
    }
    .nav-links {
        gap: 40px;
    }
    .logo {
        font-size: 36px;
    }
    .nav-item {
        font-size: 24px;
    }
}
@media (max-width: 800px) {
    .navbar {
        flex-direction: column;
        gap: 20px;
        padding: 20px 5px;
    }
    .nav-links {
        gap: 20px;
        flex-direction: column;
        align-items: center;
    }
    .logo {
        font-size: 28px;
    }
    .nav-item {
        font-size: 18px;
    }
}
@media (max-width: 500px) {
    .navbar {
        padding: 10px 2px;
        gap: 10px;
    }
    .logo {
        font-size: 20px;
    }
    .nav-item {
        font-size: 14px;
    }
}
</style>