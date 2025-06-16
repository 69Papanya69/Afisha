import api from '@/api';

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
    },
    clearTokens(state) {
        state.accessToken = null;
        state.refreshToken = null;
        state.user = null;  // Очищаем данные пользователя при выходе
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },
};

const actions = {
    async login({ commit }, { username, password }) {
        const response = await api.post('/token/', { username, password });
        commit('setTokens', {
            access: response.data.access,
            refresh: response.data.refresh,
        });
        // После успешного входа запрашиваем данные пользователя
        const userResponse = await api.get('/user/');  // Предполагаемый эндпоинт для получения данных пользователя
        commit('setUser', userResponse.data);
    },
    async register({ commit }, { username, email, password }) {
        const response = await api.post('/register/', { username, email, password });
        commit('setTokens', {
            access: response.data.access,
            refresh: response.data.refresh,
        });
        // После регистрации тоже запрашиваем данные пользователя
        const userResponse = await api.get('/user/');
        commit('setUser', userResponse.data);
    },
    logout({ commit }) {
        commit('clearTokens');
    },
    async updateProfile({ commit, state }, updatedData) {
        if (!state.accessToken) {
            throw new Error('Пользователь не авторизован');
        }
        const response = await api.put('/user/', updatedData, {
            headers: {
                Authorization: `Bearer ${state.accessToken}`,
            },
        });
        commit('setUser', response.data);
    },
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