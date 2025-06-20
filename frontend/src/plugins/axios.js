// src/plugins/axios.js
import axios from 'axios'
import hawk from './hawk'

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
        
        // Report API errors to Hawk
        if (error.response) {
            // Отправляем ошибки API в Hawk с контекстом
            hawk.send(error, {
                context: {
                    type: 'API Error',
                    url: originalRequest.url,
                    method: originalRequest.method,
                    status: error.response?.status,
                    statusText: error.response?.statusText,
                    data: error.response?.data
                }
            });
        } else if (error.request) {
            // Request made but no response received
            hawk.send(error, {
                context: {
                    type: 'API Request Error (No Response)',
                    url: originalRequest.url,
                    method: originalRequest.method
                }
            });
        } else {
            // Something happened in setting up the request
            hawk.send(error, {
                context: {
                    type: 'API Setup Error',
                    message: error.message
                }
            });
        }
        
        if (error.response?.status === 401 && !originalRequest._retry) {
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