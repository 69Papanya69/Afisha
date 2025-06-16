import axios from 'axios';
import router from './router';
import store from './store';

const api = axios.create({
    baseURL: 'http://localhost:8000/api/',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
});

// Request interceptor
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    // Проверяем, что это не запрос на регистрацию или авторизацию
    if (token && config.url && !config.url.includes('/register/') && !config.url.includes('/token/')) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor
api.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;
        
        // Если ошибка 401 (неавторизован) и не пытались восстановить 
        if (error.response && error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            
            console.log('Перехвачен ответ 401. Пробуем обновить токен...');
            
            // Пробуем обновить токен
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
                try {
                    console.log('Запрашиваем новый токен с помощью refresh token...');
                    const response = await axios.post('http://localhost:8000/api/token/refresh/', {
                        refresh: refreshToken
                    });
                    
                    console.log('Получен новый токен, обновляем...');
                    const newToken = response.data.access;
                    
                    // Обновляем токен в локальном хранилище
                    localStorage.setItem('access_token', newToken);
                    
                    // Также обновляем токен в Vuex если имеется доступ к store
                    if (store && store.commit) {
                        store.commit('auth/setTokens', {
                            access: newToken,
                            refresh: refreshToken
                        });
                    }
                    
                    // Повторяем исходный запрос с новым токеном
                    originalRequest.headers.Authorization = `Bearer ${newToken}`;
                    return api(originalRequest);
                } catch (refreshError) {
                    console.error('Ошибка обновления токена:', refreshError);
                    
                    // При ошибке обновления очищаем токены
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    
                    // Если есть доступ к Vuex, выполняем logout
                    if (store && store.dispatch) {
                        try {
                            console.log('Выполняем выход из системы...');
                            await store.dispatch('auth/logout');
                        } catch (e) {
                            console.error('Ошибка при выходе из системы:', e);
                        }
                    }
                    
                    // Перенаправляем на страницу логина если не там
                    if (router.currentRoute.value && router.currentRoute.value.path !== '/login') {
                        console.log('Перенаправляем на страницу логина...');
                        router.push('/login');
                    }
                }
            } else {
                console.log('Нет refresh токена, перенаправляем на страницу логина...');
                
                // Если нет refresh токена, тоже перенаправляем на логин
                if (router.currentRoute.value && router.currentRoute.value.path !== '/login') {
                    router.push('/login');
                }
            }
        }
        
        return Promise.reject(error);
    }
);

export default api;