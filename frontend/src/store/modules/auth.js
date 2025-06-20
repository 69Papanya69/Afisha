import api from '@/api';
import hawk from '@/plugins/hawk';

const state = {
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    user: null,  // Добавляем поле для хранения данных пользователя
};

const mutations = {
    setTokens(state, { access, refresh }) {
        state.accessToken = access;
        state.refreshToken = refresh;
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
    },
    setUser(state, user) {
        state.user = user;
        
        // При установке пользователя, обновляем информацию в Hawk
        if (user) {
            hawk.setUser({
                id: user.id?.toString() || 'unknown',
                name: user.username || 'unknown',
                // image: user.avatar // если у пользователя есть аватар
            });
        }
    },
    clearTokens(state) {
        state.accessToken = null;
        state.refreshToken = null;
        state.user = null;  // Очищаем данные пользователя при выходе
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        // При выходе пользователя, сбрасываем пользовательские данные в Hawk
        hawk.resetUser();
    },
};

const actions = {
    async login({ commit }, { username, password }) {
        try {
            const response = await api.post('/token/', { username, password });
            commit('setTokens', {
                access: response.data.access,
                refresh: response.data.refresh,
            });
            // После успешного входа запрашиваем данные пользователя
            const userResponse = await api.get('/user/');  // Предполагаемый эндпоинт для получения данных пользователя
            commit('setUser', userResponse.data);
        } catch (error) {
            // Отправляем ошибку аутентификации в Hawk
            hawk.send(error, {
                context: {
                    action: 'login',
                    username: username // Не отправляем пароль в целях безопасности
                }
            });
            throw error; // Пробрасываем ошибку дальше для обработки в компоненте
        }
    },
    async register({ commit }, { username, email, password }) {
        try {
            const response = await api.post('/register/', { username, email, password });
            commit('setTokens', {
                access: response.data.access,
                refresh: response.data.refresh,
            });
            // После регистрации тоже запрашиваем данные пользователя
            const userResponse = await api.get('/user/');
            commit('setUser', userResponse.data);
        } catch (error) {
            // Отправляем ошибку регистрации в Hawk
            hawk.send(error, {
                context: {
                    action: 'register',
                    username,
                    email
                    // Не отправляем пароль в целях безопасности
                }
            });
            throw error;
        }
    },
    logout({ commit }) {
        try {
            commit('clearTokens');
        } catch (error) {
            hawk.send(error, {
                context: {
                    action: 'logout'
                }
            });
        }
    },
    async updateProfile({ commit, state }, updatedData) {
        if (!state.accessToken) {
            const error = new Error('Пользователь не авторизован');
            hawk.send(error, {
                context: {
                    action: 'updateProfile',
                    message: 'Попытка обновить профиль без авторизации'
                }
            });
            throw error;
        }
        
        try {
            const response = await api.put('/user/', updatedData, {
                headers: {
                    Authorization: `Bearer ${state.accessToken}`,
                },
            });
            commit('setUser', response.data);
        } catch (error) {
            hawk.send(error, {
                context: {
                    action: 'updateProfile'
                }
            });
            throw error;
        }
    },
    async loadUser({ commit, state, dispatch }) {
        if (!state.accessToken) return;
        
        try {
            const response = await api.get('/user/', {
                headers: {
                    Authorization: `Bearer ${state.accessToken}`
                }
            });
            commit('setUser', response.data);
        } catch (error) {
            // Если токен устарел, попытаемся обновить его
            if (error.response && error.response.status === 401) {
                try {
                    await dispatch('refreshToken');
                    // Повторная попытка получить данные пользователя
                    const retryResponse = await api.get('/user/', {
                        headers: {
                            Authorization: `Bearer ${state.accessToken}`
                        }
                    });
                    commit('setUser', retryResponse.data);
                } catch (refreshError) {
                    hawk.send(refreshError, {
                        context: {
                            action: 'loadUser',
                            message: 'Не удалось обновить токен'
                        }
                    });
                    commit('clearTokens');
                }
            } else {
                hawk.send(error, {
                    context: {
                        action: 'loadUser'
                    }
                });
            }
        }
    },
    async refreshToken({ commit, state }) {
        if (!state.refreshToken) {
            const error = new Error('Отсутствует токен обновления');
            hawk.send(error, {
                context: {
                    action: 'refreshToken',
                    message: 'Попытка обновить токен без refresh токена'
                }
            });
            throw error;
        }
        
        try {
            const response = await api.post('/token/refresh/', { refresh: state.refreshToken });
            commit('setTokens', {
                access: response.data.access,
                refresh: response.data.refresh || state.refreshToken
            });
            return response.data.access;
        } catch (error) {
            hawk.send(error, {
                context: {
                    action: 'refreshToken'
                }
            });
            commit('clearTokens');
            throw error;
        }
    }
};

const getters = {
    isAuthenticated: (state) => !!state.accessToken,
    getUser: (state) => state.user,
};

export default {
    namespaced: true,
    state,
    mutations,
    actions,
    getters,
};