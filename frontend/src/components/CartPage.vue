<template>
  <main class="cart-page">
    <h1>Корзина</h1>
    
    <div v-if="loading" class="loading">
      <div class="loader"></div>
      <p>Загрузка корзины...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="cartItems.length === 0" class="empty-cart">
      <i class="fas fa-shopping-cart"></i>
      <h2>Ваша корзина пуста</h2>
      <p>Добавьте билеты на спектакли, чтобы увидеть их здесь</p>
      <router-link to="/general" class="btn-primary">Перейти к спектаклям</router-link>
    </div>
    
    <div v-else class="cart-content">
      <div class="cart-items">
        <div v-for="item in cartItems" :key="item.id" class="cart-item">
          <div class="item-details">
            <h3>{{ item.performance_schedule.performance_name }}</h3>
            <p class="theater">{{ item.performance_schedule.theater_name }}</p>
            <p class="date-time">{{ formatDateTime(item.performance_schedule.date_time) }}</p>
            <p class="hall">Зал: {{ item.performance_schedule.hall_number }}</p>
          </div>
          
          <div class="item-price">
            <p class="price">{{ formatPrice(item.performance_schedule.price) }} ₽</p>
          </div>
          
          <div class="item-actions">
            <div class="quantity-control">
              <button @click="decreaseQuantity(item)" :disabled="loading || item.quantity <= 1">-</button>
              <span>{{ item.quantity }}</span>
              <button @click="increaseQuantity(item)" :disabled="loading || item.quantity >= item.performance_schedule.available_seats">+</button>
            </div>
            
            <div class="item-total">
              <p>Итого: {{ formatPrice(item.performance_schedule.price * item.quantity) }} ₽</p>
            </div>
            
            <button class="remove-btn" @click="removeItem(item.id)" :disabled="loading">
              <i class="fas fa-trash"></i> Удалить
            </button>
          </div>
        </div>
      </div>
      
      <div class="cart-summary">
        <div class="summary-item">
          <span>Количество билетов:</span>
          <span>{{ cartItemsCount }}</span>
        </div>
        <div class="summary-item">
          <span>Итоговая сумма:</span>
          <span>{{ formatPrice(cartTotal) }} ₽</span>
        </div>
        <div class="cart-actions">
          <router-link to="/checkout" class="checkout-btn" :disabled="loading">
            <i class="fas fa-credit-card"></i> Оформить заказ
          </router-link>
          <button class="clear-btn" @click="clearCart" :disabled="loading">
            <i class="fas fa-trash-alt"></i> Очистить корзину
          </button>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
  name: 'CartPage',
  
  computed: {
    ...mapState({
      cartItems: state => state.cart.cartItems,
      loading: state => state.cart.loading,
      error: state => state.cart.error
    }),
    ...mapGetters({
      cartItemsCount: 'cart/cartItemsCount',
      cartTotal: 'cart/cartTotal'
    })
  },
  
  mounted() {
    // Загружаем содержимое корзины при загрузке компонента
    this.fetchCartItems();
    
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
      fetchCartItems: 'cart/fetchCartItems',
      updateCartItemQuantity: 'cart/updateCartItemQuantity',
      removeFromCart: 'cart/removeFromCart',
      clearCartAction: 'cart/clearCart'
    }),
    
    async increaseQuantity(item) {
      try {
        await this.updateCartItemQuantity({
          itemId: item.id,
          quantity: item.quantity + 1
        });
      } catch (error) {
        alert(error.response?.data?.error || 'Не удалось обновить количество');
      }
    },
    
    async decreaseQuantity(item) {
      if (item.quantity <= 1) return;
      
      try {
        await this.updateCartItemQuantity({
          itemId: item.id,
          quantity: item.quantity - 1
        });
      } catch (error) {
        alert(error.response?.data?.error || 'Не удалось обновить количество');
      }
    },
    
    async removeItem(itemId) {
      if (confirm('Вы действительно хотите удалить этот билет из корзины?')) {
        try {
          await this.removeFromCart(itemId);
        } catch (error) {
          alert(error.response?.data?.error || 'Не удалось удалить товар из корзины');
        }
      }
    },
    
    async clearCart() {
      if (confirm('Вы действительно хотите очистить корзину?')) {
        try {
          await this.clearCartAction();
        } catch (error) {
          alert(error.response?.data?.error || 'Не удалось очистить корзину');
        }
      }
    },
    
    checkout() {
      this.$router.push('/checkout');
    },
    
    formatPrice(price) {
      return parseFloat(price).toFixed(2);
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
.cart-page {
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

.loading, .error-message, .empty-cart {
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

.error-message i, .empty-cart i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #ff4081;
}

.empty-cart h2 {
  margin-bottom: 1rem;
}

.empty-cart p {
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

.cart-content {
  display: grid;
  gap: 2rem;
  grid-template-columns: 1fr 300px;
}

.cart-items {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  padding: 1.5rem;
}

.cart-item {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  gap: 1rem;
}

.cart-item:last-child {
  border-bottom: none;
}

.item-details {
  flex: 2;
}

.item-details h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.theater, .date-time, .hall {
  color: rgba(255, 255, 255, 0.7);
  margin: 0.25rem 0;
}

.item-price {
  flex: 1;
  text-align: right;
}

.price {
  font-weight: bold;
  font-size: 1.2rem;
}

.item-actions {
  flex: 2;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.quantity-control button {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.2s;
}

.quantity-control button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
}

.quantity-control button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quantity-control span {
  min-width: 30px;
  text-align: center;
}

.item-total {
  margin-right: 1rem;
  font-weight: bold;
}

.remove-btn {
  background: none;
  border: none;
  color: #ff4081;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.remove-btn:hover:not(:disabled) {
  text-decoration: underline;
}

.remove-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cart-summary {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  padding: 1.5rem;
  height: fit-content;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.summary-item:last-of-type {
  font-weight: bold;
  font-size: 1.2rem;
}

.cart-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1.5rem;
}

.checkout-btn, .clear-btn {
  padding: 0.8rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.checkout-btn {
  background: linear-gradient(135deg, #ff4081 0%, #c2185b 100%);
  color: white;
}

.clear-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.checkout-btn:hover:not(:disabled), .clear-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.checkout-btn:disabled, .clear-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 900px) {
  .cart-content {
    grid-template-columns: 1fr;
  }
  
  .cart-item {
    flex-direction: column;
  }
  
  .item-price {
    text-align: left;
  }
}
</style> 