import api from '@/api';

// Initial state
const state = {
  orders: [],
  currentOrder: null,
  loading: false,
  error: null,
};

// Getters
const getters = {
  orderCount: (state) => state.orders.length,
  pendingOrders: (state) => state.orders.filter(order => order.status === 'pending'),
  completedOrders: (state) => state.orders.filter(order => order.status === 'completed'),
  cancelledOrders: (state) => state.orders.filter(order => order.status === 'cancelled')
};

// Mutations
const mutations = {
  SET_ORDERS(state, orders) {
    state.orders = orders;
  },
  SET_CURRENT_ORDER(state, order) {
    state.currentOrder = order;
  },
  SET_LOADING(state, status) {
    state.loading = status;
  },
  SET_ERROR(state, error) {
    state.error = error;
  },
  CLEAR_ERROR(state) {
    state.error = null;
  }
};

// Actions
const actions = {
  async fetchOrders({ commit }) {
    try {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');
      
      const response = await api.get('orders/');
      commit('SET_ORDERS', response.data);
      
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Ошибка загрузки заказов');
      return [];
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async fetchOrderDetail({ commit }, orderId) {
    try {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');
      
      const response = await api.get(`orders/${orderId}/`);
      commit('SET_CURRENT_ORDER', response.data);
      
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Ошибка загрузки заказа');
      return null;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async createOrder({ commit }, orderData) {
    try {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');
      
      const response = await api.post('orders/create/', orderData);
      commit('SET_CURRENT_ORDER', response.data);
      
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Ошибка создания заказа');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async cancelOrder({ commit, dispatch }, orderId) {
    try {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');
      
      const response = await api.post(`orders/${orderId}/cancel/`);
      
      // Обновляем текущий заказ
      commit('SET_CURRENT_ORDER', response.data);
      
      // Обновляем список заказов
      await dispatch('fetchOrders');
      
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Ошибка отмены заказа');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  }
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}; 