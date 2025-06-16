import api from '@/api';

// Initial state
const state = {
  cartItems: [],
  loading: false,
  error: null,
  lastAddedItem: null
};

// Getters
const getters = {
  cartItemsCount: (state) => {
    return state.cartItems.reduce((sum, item) => sum + item.quantity, 0);
  },
  cartTotal: (state) => {
    return state.cartItems.reduce((sum, item) => {
      return sum + (item.performance_schedule.price * item.quantity);
    }, 0);
  }
};

// Mutations
const mutations = {
  SET_CART_ITEMS(state, items) {
    state.cartItems = items;
  },
  SET_LOADING(state, status) {
    state.loading = status;
  },
  SET_ERROR(state, error) {
    state.error = error;
  },
  SET_LAST_ADDED(state, item) {
    state.lastAddedItem = item;
  },
  CLEAR_ERROR(state) {
    state.error = null;
  }
};

// Actions
const actions = {
  async fetchCartItems({ commit }) {
    try {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');
      
      const response = await api.get('cart/');
      commit('SET_CART_ITEMS', response.data);
      
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Ошибка загрузки корзины');
      return [];
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async addToCart({ commit, dispatch }, { performanceScheduleId, quantity }) {
    try {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');
      
      const response = await api.post('cart/add/', {
        performance_schedule_id: performanceScheduleId,
        quantity
      });
      
      commit('SET_LAST_ADDED', response.data);
      
      // Обновляем корзину после добавления
      await dispatch('fetchCartItems');
      
      return response.data;
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Ошибка добавления в корзину';
      commit('SET_ERROR', errorMessage);
      throw errorMessage;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async updateCartItemQuantity({ commit, dispatch }, { itemId, quantity }) {
    try {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');
      
      await api.post(`cart/update/${itemId}/`, { quantity });
      
      // Обновляем корзину после изменения
      await dispatch('fetchCartItems');
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Ошибка изменения количества');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async removeFromCart({ commit, dispatch }, itemId) {
    try {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');
      
      await api.delete(`cart/remove/${itemId}/`);
      
      // Обновляем корзину после удаления
      await dispatch('fetchCartItems');
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Ошибка удаления из корзины');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async clearCart({ commit }) {
    try {
      commit('SET_LOADING', true);
      commit('CLEAR_ERROR');
      
      await api.post('cart/clear/');
      commit('SET_CART_ITEMS', []);
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || 'Ошибка очистки корзины');
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