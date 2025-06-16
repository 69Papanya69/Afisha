<template>
  <main class="orders-page">
    <h1>История заказов</h1>
    
    <div v-if="loading" class="loading">
      <div class="loader"></div>
      <p>Загрузка заказов...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="orders.length === 0" class="empty-orders">
      <i class="fas fa-shopping-bag"></i>
      <h2>У вас еще нет заказов</h2>
      <p>После оформления заказов они появятся здесь</p>
      <router-link to="/general" class="btn-primary">Перейти к спектаклям</router-link>
    </div>
    
    <div v-else class="orders-container">
      <div class="orders-tabs">
        <button 
          @click="activeTab = 'all'" 
          :class="{ 'active': activeTab === 'all' }"
        >
          Все ({{ orders.length }})
        </button>
        <button 
          @click="activeTab = 'pending'" 
          :class="{ 'active': activeTab === 'pending' }"
        >
          Обрабатываются ({{ pendingOrders.length }})
        </button>
        <button 
          @click="activeTab = 'confirmed'" 
          :class="{ 'active': activeTab === 'confirmed' }"
        >
          Подтверждены ({{ confirmedOrders.length }})
        </button>
        <button 
          @click="activeTab = 'completed'" 
          :class="{ 'active': activeTab === 'completed' }"
        >
          Выполнены ({{ completedOrders.length }})
        </button>
        <button 
          @click="activeTab = 'cancelled'" 
          :class="{ 'active': activeTab === 'cancelled' }"
        >
          Отменены ({{ cancelledOrders.length }})
        </button>
      </div>
      
      <div class="orders-list">
        <div 
          v-for="order in filteredOrders" 
          :key="order.id" 
          class="order-card"
          :class="{ 
            'order-pending': order.status === 'pending',
            'order-confirmed': order.status === 'confirmed',
            'order-completed': order.status === 'completed',
            'order-cancelled': order.status === 'cancelled'
          }"
        >
          <div class="order-header">
            <div class="order-id">
              <h3>Заказ #{{ order.id }}</h3>
              <span class="order-date">{{ formatDate(order.created_at) }}</span>
            </div>
            <div class="order-status">
              {{ order.status_display }}
            </div>
          </div>
          
          <div class="order-summary">
            <div class="order-info">
              <p><strong>Сумма:</strong> {{ formatPrice(order.total_amount) }} ₽</p>
              <p><strong>Способ оплаты:</strong> {{ order.payment_method }}</p>
            </div>
            <div class="order-actions">
              <button 
                @click="viewOrderDetails(order.id)" 
                class="btn-view"
              >
                <i class="fas fa-eye"></i> Подробнее
              </button>
              <button 
                v-if="order.status === 'pending'" 
                @click="cancelOrder(order.id)"
                class="btn-cancel"
                :disabled="loading"
              >
                <i class="fas fa-times"></i> Отменить
              </button>
            </div>
          </div>
          
          <div v-if="expandedOrderId === order.id" class="order-details">
            <div class="order-items">
              <h4>Билеты</h4>
              <div v-for="item in order.items" :key="item.id" class="order-item">
                <div class="item-info">
                  <p class="item-name">{{ item.performance_name }}</p>
                  <p class="item-details">
                    {{ formatDateTime(item.date_time) }}, {{ item.theater_name }}
                  </p>
                </div>
                <div class="item-quantity">
                  {{ item.quantity }} x {{ formatPrice(item.price_per_unit) }} ₽
                </div>
                <div class="item-subtotal">
                  {{ formatPrice(item.subtotal) }} ₽
                </div>
              </div>
            </div>
            
            <div class="customer-info">
              <h4>Информация о заказчике</h4>
              <p><strong>Имя:</strong> {{ order.customer_name }}</p>
              <p><strong>Email:</strong> {{ order.customer_email }}</p>
              <p v-if="order.customer_phone"><strong>Телефон:</strong> {{ order.customer_phone }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import { mapActions, mapState } from 'vuex';

export default {
  name: 'OrdersPage',
  
  data() {
    return {
      activeTab: 'all',
      expandedOrderId: null,
    };
  },
  
  computed: {
    ...mapState({
      orders: state => state.orders.orders,
      loading: state => state.orders.loading,
      error: state => state.orders.error
    }),
    
    pendingOrders() {
      return this.orders.filter(order => order.status === 'pending');
    },
    
    confirmedOrders() {
      return this.orders.filter(order => order.status === 'confirmed');
    },
    
    completedOrders() {
      return this.orders.filter(order => order.status === 'completed');
    },
    
    cancelledOrders() {
      return this.orders.filter(order => order.status === 'cancelled');
    },
    
    filteredOrders() {
      switch (this.activeTab) {
        case 'pending':
          return this.pendingOrders;
        case 'confirmed':
          return this.confirmedOrders;
        case 'completed':
          return this.completedOrders;
        case 'cancelled':
          return this.cancelledOrders;
        default:
          return this.orders;
      }
    }
  },
  
  mounted() {
    this.fetchOrders();
    
    // Загружаем иконки FontAwesome, если их еще нет
    if (!document.querySelector('link[href*="font-awesome"]')) {
      const fontAwesome = document.createElement('link');
      fontAwesome.rel = 'stylesheet';
      fontAwesome.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
      document.head.appendChild(fontAwesome);
    }
  },
  
  methods: {
    ...mapActions({
      fetchOrders: 'orders/fetchOrders',
      fetchOrderDetail: 'orders/fetchOrderDetail',
      cancelOrderAction: 'orders/cancelOrder'
    }),
    
    async viewOrderDetails(orderId) {
      if (this.expandedOrderId === orderId) {
        this.expandedOrderId = null;
      } else {
        this.expandedOrderId = orderId;
        await this.fetchOrderDetail(orderId);
      }
    },
    
    async cancelOrder(orderId) {
      if (confirm('Вы уверены, что хотите отменить этот заказ?')) {
        try {
          await this.cancelOrderAction(orderId);
        } catch (error) {
          alert(error.response?.data?.error || 'Ошибка отмены заказа');
        }
      }
    },
    
    formatPrice(price) {
      return parseFloat(price).toFixed(2);
    },
    
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    },
    
    formatDateTime(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  }
};
</script>

<style scoped>
.orders-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  color: #fff;
}

h1 {
  text-align: center;
  margin-bottom: 2rem;
  font-family: 'Vogue', sans-serif;
  font-size: 2.5rem;
}

.loading, .error-message, .empty-orders {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
}

.loader {
  border: 5px solid rgba(255,255,255,0.2);
  border-top: 5px solid #fff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message i, .empty-orders i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #ff4081;
}

.empty-orders h2 {
  margin-bottom: 1rem;
}

.empty-orders p {
  margin-bottom: 2rem;
}

.btn-primary {
  display: inline-block;
  background: linear-gradient(135deg, #ff4081 0%, #c2185b 100%);
  color: white;
  padding: 0.8rem 1.5rem;
  border-radius: 30px;
  text-decoration: none;
  font-weight: bold;
  transition: all 0.3s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.orders-tabs {
  display: flex;
  overflow-x: auto;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px 10px 0 0;
  padding: 0.5rem;
  margin-bottom: 1rem;
}

.orders-tabs button {
  background: none;
  border: none;
  color: #fff;
  padding: 0.75rem 1.5rem;
  border-radius: 5px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.orders-tabs button:hover {
  background: rgba(255, 255, 255, 0.1);
}

.orders-tabs button.active {
  background: rgba(255, 255, 255, 0.2);
  font-weight: bold;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.order-card {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  padding: 1.5rem;
  border-left: 5px solid #ccc;
}

.order-pending {
  border-left-color: #ff9800;
}

.order-confirmed {
  border-left-color: #2196f3;
}

.order-completed {
  border-left-color: #4caf50;
}

.order-cancelled {
  border-left-color: #f44336;
}

.order-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.order-id h3 {
  margin: 0;
  font-size: 1.2rem;
}

.order-date {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.order-status {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: bold;
  background: rgba(255, 255, 255, 0.1);
}

.order-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.order-info p {
  margin: 0.25rem 0;
}

.order-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-view, .btn-cancel {
  padding: 0.5rem 0.75rem;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  border: none;
  transition: all 0.2s;
}

.btn-view {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.btn-cancel {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

.btn-view:hover, .btn-cancel:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-cancel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.order-details {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.order-items {
  margin-bottom: 1.5rem;
}

h4 {
  font-size: 1rem;
  margin-bottom: 0.75rem;
  color: rgba(255, 255, 255, 0.9);
}

.order-item {
  display: grid;
  grid-template-columns: 3fr 2fr 1fr;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.item-info .item-name {
  font-weight: bold;
  margin: 0;
}

.item-info .item-details {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin: 0.25rem 0 0;
}

.item-quantity, .item-subtotal {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.item-subtotal {
  font-weight: bold;
}

.customer-info p {
  margin: 0.25rem 0;
}

@media (max-width: 768px) {
  .order-item {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .item-quantity, .item-subtotal {
    justify-content: flex-start;
  }
  
  .order-actions {
    margin-top: 1rem;
    width: 100%;
    justify-content: flex-end;
  }
}
</style> 