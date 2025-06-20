import { createRouter, createWebHistory } from 'vue-router'
import RegistrationPage from './components/RegistrationPage.vue'
import AuthorizationPage from './components/AuthorizationPage.vue'
import ProfilePage from './components/ProfilePage.vue'
import GeneralPage from './components/GeneralPage.vue'
import CartPage from './components/CartPage.vue'
import CheckoutPage from './components/CheckoutPage.vue'
import OrdersPage from './components/OrdersPage.vue'
import CatalogPage from './components/CatalogPage.vue'
import HawkTest from './components/HawkTest.vue'
import PerformancePage from './components/PerfomancePage.vue'
import store from './store'
// import CategoryPage from './components/CategoryPage.vue'
// import ProductPage from './components/ProductPage.vue'

const routes = [
    { path: '/', redirect: '/general' },
    { path: '/register', component: RegistrationPage },
    { path: '/login', component: AuthorizationPage},
    { 
      path: '/profile', 
      component: ProfilePage,
      meta: { requiresAuth: true }
    },
    { path: '/general', component: GeneralPage},
    {
      path: '/performances/:id',
      name: 'PerformancePage',
      component: PerformancePage,
    },
    {
      path: '/cart',
      name: 'CartPage',
      component: CartPage,
      meta: { requiresAuth: true }
    },
    {
      path: '/checkout',
      name: 'CheckoutPage',
      component: CheckoutPage,
      meta: { requiresAuth: true }
    },
    {
      path: '/orders',
      name: 'OrdersPage',
      component: OrdersPage,
      meta: { requiresAuth: true }
    },
    {
      path: '/catalog',
      name: 'CatalogPage',
      component: CatalogPage
    },
    {
      path: '/hawk-test',
      name: 'HawkTest',
      component: HawkTest
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Защита маршрутов
router.beforeEach((to, from, next) => {
    const isAuthenticated = store.getters['auth/isAuthenticated'];
    
    // Если маршрут требует авторизации и пользователь не авторизован
    if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
        console.log('Попытка доступа к защищенному маршруту без авторизации');
        // Перенаправляем на страницу входа
        next('/login');
    } else {
        next();
    }
});

export default router