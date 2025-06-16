// src/plugins/axios.js
import axios from 'axios'

const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json'
    }
})

// Добавляем interceptor для обновления токена
api.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true
            try {
                const store = require('@/store').default
                await store.dispatch('refreshToken')
                const newToken = store.state.token
                originalRequest.headers['Authorization'] = `Bearer ${newToken}`
                return api(originalRequest)
            } catch (refreshError) {
                const store = require('@/store').default
                await store.dispatch('logout')
                return Promise.reject(refreshError)
            }
        }
        return Promise.reject(error)
    }
)

export default api