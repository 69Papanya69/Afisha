<template>
  <main class="checkout-page">
    <h1>Оформление заказа</h1>
    
    <div v-if="loading" class="loading">
      <div class="loader"></div>
      <p>Загрузка...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="orderPlaced" class="order-success">
      <i class="fas fa-check-circle"></i>
      <h2>Ваш заказ успешно оформлен!</h2>
      <p>Заказ #{{ orderPlaced.id }} успешно создан</p>
      <div class="order-details">
        <p><strong>Имя заказчика:</strong> {{ orderPlaced.customer_name }}</p>
        <p><strong>Email:</strong> {{ orderPlaced.customer_email }}</p>
        <p><strong>Телефон:</strong> {{ orderPlaced.customer_phone || 'Не указан' }}</p>
        <p><strong>Метод оплаты:</strong> {{ orderPlaced.payment_method }}</p>
        <p><strong>Сумма заказа:</strong> {{ formatPrice(orderPlaced.total_amount) }} ₽</p>
        <p><strong>Статус заказа:</strong> {{ orderPlaced.status_display }}</p>
      </div>
      <div class="navigation-buttons">
        <router-link to="/profile" class="btn-primary">
          <i class="fas fa-user"></i> Перейти в профиль
        </router-link>
        <router-link to="/general" class="btn-secondary">
          <i class="fas fa-home"></i> На главную
        </router-link>
      </div>
    </div>
    
    <div v-else class="checkout-content">
      <div class="cart-summary">
        <h2>Ваш заказ</h2>
        <div v-if="cartItems.length === 0" class="empty-cart-message">
          <p>Ваша корзина пуста</p>
          <router-link to="/general" class="btn-primary">Перейти к спектаклям</router-link>
        </div>
        <div v-else class="cart-items-summary">
          <div v-for="item in cartItems" :key="item.id" class="cart-item-row">
            <div class="item-info">
              <h3>{{ item.performance_schedule.performance_name }}</h3>
              <p>{{ formatDateTime(item.performance_schedule.date_time) }}, {{ item.performance_schedule.theater_name }}</p>
            </div>
            <div class="item-quantity">
              {{ item.quantity }} x {{ formatPrice(item.performance_schedule.price) }} ₽
            </div>
            <div class="item-subtotal">
              {{ formatPrice(item.performance_schedule.price * item.quantity) }} ₽
            </div>
          </div>
          <div class="cart-total">
            <span>Итого:</span>
            <span>{{ formatPrice(cartTotal) }} ₽</span>
          </div>
        </div>
      </div>
      
      <div class="checkout-form">
        <h2>Информация для заказа</h2>
        <form @submit.prevent="placeOrder">
          <div class="form-group">
            <label for="customer_name">Имя заказчика *</label>
            <input 
              id="customer_name" 
              v-model="formData.customer_name" 
              type="text" 
              required
              :disabled="loading"
              placeholder="Введите ваше имя"
            >
          </div>
          
          <div class="form-group">
            <label for="customer_email">Email *</label>
            <input 
              id="customer_email" 
              v-model="formData.customer_email" 
              type="email" 
              required
              :disabled="loading"
              placeholder="Введите ваш email"
            >
          </div>
          
          <div class="form-group">
            <label for="customer_phone">Телефон</label>
            <input 
              id="customer_phone" 
              v-model="formData.customer_phone" 
              type="tel"
              :disabled="loading"
              placeholder="Введите ваш номер телефона"
            >
          </div>
          
          <div class="form-group">
            <label for="delivery_address">Адрес доставки (формат: ул. Название, д. Номер, г. Город, индекс 123456)</label>
            <textarea 
              id="delivery_address" 
              v-model="formData.delivery_address" 
              :disabled="loading"
              placeholder="Введите адрес в формате: ул. Пушкина, д. 10, г. Москва, индекс 123456"
              rows="3"
            ></textarea>
            <div class="form-help">
              Адрес должен содержать улицу, номер дома, город и почтовый индекс из 6 цифр.
            </div>
          </div>
          
          <div class="form-group">
            <label for="payment_method">Способ оплаты *</label>
            <select 
              id="payment_method" 
              v-model="formData.payment_method" 
              required
              :disabled="loading"
            >
              <option value="Онлайн">Онлайн оплата</option>
              <option value="Наличными">Оплата наличными при получении</option>
              <option value="Картой">Оплата картой при получении</option>
            </select>
          </div>
          
          <div class="checkout-actions">
            <button type="submit" class="order-btn" :disabled="loading || cartItems.length === 0">
              <i class="fas fa-check"></i> Оформить заказ
            </button>
            <router-link to="/cart" class="back-btn">
              <i class="fas fa-arrow-left"></i> Вернуться в корзину
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </main>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import api from '@/api';

export default {
  name: 'CheckoutPage',
  
  data() {
    return {
      formData: {
        customer_name: '',
        customer_email: '',
        customer_phone: '',
        payment_method: 'Онлайн',
        delivery_address: '',
      },
      loading: false,
      error: null,
      orderPlaced: null
    };
  },
  
  computed: {
    ...mapState({
      cartItems: state => state.cart.cartItems,
      user: state => state.auth.user
    }),
    ...mapGetters({
      cartItemsCount: 'cart/cartItemsCount',
      cartTotal: 'cart/cartTotal'
    })
  },
  
  mounted() {
    // Загружаем содержимое корзины при загрузке компонента
    this.fetchCartItems();
    
    // Предзаполняем форму данными пользователя, если они есть
    if (this.user) {
      this.formData.customer_name = this.user.username || '';
      this.formData.customer_email = this.user.email || '';
      this.formData.customer_phone = this.user.phone || '';
    }
  },
  
  methods: {
    ...mapActions({
      fetchCartItems: 'cart/fetchCartItems'
    }),
    
    async placeOrder() {
      if (this.cartItems.length === 0) {
        this.error = 'Невозможно оформить заказ: корзина пуста';
        return;
      }
      
      try {
        this.loading = true;
        this.error = null;
        
        const response = await api.post('orders/create/', this.formData);
        this.orderPlaced = response.data;
        
      } catch (error) {
        console.error('Ошибка при оформлении заказа:', error);
        
        // Обрабатываем различные форматы ошибок с сервера
        if (error.response?.data) {
          const data = error.response.data;
          
          // Обработка ошибок не-поле (общие ошибки)
          if (data.non_field_errors) {
            this.error = data.non_field_errors.join('\n');
          }
          // Обработка ошибок конкретного поля
          else if (data.delivery_address) {
            this.error = `Ошибка в адресе доставки: ${data.delivery_address.join('\n')}`;
          }
          // Обработка общей ошибки
          else if (data.error) {
            this.error = data.error;
          }
          // Если это массив ошибок
          else if (Array.isArray(data)) {
            this.error = data.join('\n');
          }
          // Если формат ошибки неизвестен
          else {
            this.error = 'Произошла ошибка при оформлении заказа';
          }
        } else {
          this.error = 'Произошла ошибка при оформлении заказа';
        }
      } finally {
        this.loading = false;
      }
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
.checkout-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  color: #fff;
}

h1, h2 {
  font-family: 'Vogue', sans-serif;
}

h1 {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2.5rem;
}

h2 {
  margin-bottom: 1rem;
  font-size: 1.8rem;
}

.loading, .error-message, .order-success {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  margin-bottom: 2rem;
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

.error-message i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #ff4081;
}

.order-success i {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: #4caf50;
}

.order-success h2 {
  margin-bottom: 1rem;
}

.order-details {
  margin: 1.5rem 0;
  text-align: left;
  width: 100%;
  max-width: 500px;
  background: rgba(0, 0, 0, 0.2);
  padding: 1.5rem;
  border-radius: 10px;
}

.order-details p {
  margin: 0.5rem 0;
}

.navigation-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.btn-primary, .btn-secondary {
  display: inline-block;
  padding: 0.8rem 1.5rem;
  border-radius: 30px;
  text-decoration: none;
  font-weight: bold;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #ff4081 0%, #c2185b 100%);
  color: white;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-primary:hover, .btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.checkout-content {
  display: grid;
  gap: 2rem;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.cart-summary, .checkout-form {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  padding: 1.5rem;
}

.empty-cart-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem 0;
}

.cart-item-row {
  display: grid;
  grid-template-columns: 3fr 2fr 1fr;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.item-info h3 {
  font-size: 1rem;
  margin-bottom: 0.25rem;
}

.item-info p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.item-quantity, .item-subtotal {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.item-subtotal {
  font-weight: bold;
}

.cart-total {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.3);
  font-weight: bold;
  font-size: 1.2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border-radius: 5px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.2);
  color: white;
  font-size: 1rem;
}

.form-group input::placeholder, .form-group textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-group input:focus, .form-group select:focus, .form-group textarea:focus {
  outline: none;
  border-color: #ff4081;
}

.form-help {
  margin-top: 0.25rem;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
}

.checkout-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.order-btn, .back-btn {
  padding: 0.8rem 1.5rem;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
  text-decoration: none;
}

.order-btn {
  background: linear-gradient(135deg, #ff4081 0%, #c2185b 100%);
  color: white;
  border: none;
  flex: 1;
  font-size: 1rem;
}

.back-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.order-btn:hover:not(:disabled), .back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.order-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .cart-item-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .item-quantity, .item-subtotal {
    justify-content: flex-start;
  }
  
  .checkout-actions {
    flex-direction: column;
  }
}
</style> 