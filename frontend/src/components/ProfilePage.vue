<template>
  <main class="profile_parent" aria-label="Профиль пользователя">
    <section class="profile">
      <h1 class="profile_h1">Профиль</h1>
      <div v-if="user" class="profile-info" role="form" aria-label="Редактирование профиля">
        <div class="profile-row">
          <label class="profile-label" for="profile-username">Имя пользователя:</label>
          <input v-model="editableUser.username" id="profile-username" class="profile-input" aria-label="Имя пользователя" />
        </div>
        <div class="profile-row">
          <label class="profile-label" for="profile-email">Электронная почта:</label>
          <input v-model="editableUser.email" id="profile-email" class="profile-input" aria-label="Электронная почта" />
        </div>
        <div class="profile-row">
          <span class="profile-label">Дата регистрации:</span>
          <span class="profile-value">{{ user.registrationDate }}</span>
        </div>
        <button @click="saveChanges" class="save-button" aria-label="Сохранить изменения">Сохранить изменения</button>
        <button @click="logout" class="logout-button" aria-label="Выйти из аккаунта">Выйти</button>
      </div>
      <div v-else>
        <p>Вы не авторизованы. <router-link to="/login" aria-label="Войти">Войти</router-link></p>
      </div>

      <!-- Блок с последними заказами -->
      <div v-if="user" class="recent-orders">
        <h2>Последние заказы</h2>
        
        <div v-if="loading" class="loading-indicator">
          <div class="spinner"></div>
          <p>Загрузка заказов...</p>
        </div>
        
        <div v-else-if="error" class="error-message">
          <p>{{ error }}</p>
        </div>
        
        <div v-else-if="orders.length === 0" class="no-orders">
          <p>У вас еще нет заказов</p>
          <router-link to="/general" class="action-button">Перейти к спектаклям</router-link>
        </div>
        
        <div v-else>
          <div v-for="order in recentOrders" :key="order.id" class="order-item">
            <div class="order-header">
              <span class="order-number">Заказ #{{ order.id }}</span>
              <span :class="['order-status', `status-${order.status}`]">{{ order.status_display }}</span>
            </div>
            <div class="order-details">
              <div class="order-date">{{ formatDate(order.created_at) }}</div>
              <div class="order-total">{{ formatPrice(order.total_amount) }} ₽</div>
            </div>
          </div>
          
          <div class="view-all-orders">
            <router-link to="/orders" class="view-all-button">
              Просмотреть все заказы
            </router-link>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  data() {
    return {
      editableUser: {
        username: '',
        email: ''
      }
    };
  },
  
  setup() {
    const router = useRouter();
    
    return {
      router
    };
  },
  
  computed: {
    ...mapGetters({
      isAuthenticated: 'auth/isAuthenticated',
      user: 'auth/getUser'
    }),
    
    orders() {
      return this.$store.state.orders?.orders || [];
    },
    
    loading() {
      return this.$store.state.orders?.loading || false;
    },
    
    error() {
      return this.$store.state.orders?.error || null;
    },
    
    recentOrders() {
      return [...this.orders].sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
      ).slice(0, 3);
    }
  },
  
  methods: {
    ...mapActions({
      updateProfile: 'auth/updateProfile',
      logout: 'auth/logout'
    }),
    
    saveChanges() {
      this.updateProfile(this.editableUser);
      alert('Изменения сохранены!');
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    },
    
    formatPrice(price) {
      return parseFloat(price).toFixed(2);
    }
  },
  
  mounted() {
    if (this.user) {
      this.editableUser.username = this.user.username || '';
      this.editableUser.email = this.user.email || '';
      
      // Загружаем заказы при монтировании компонента
      if (this.$store.state.orders) {
        this.$store.dispatch('orders/fetchOrders');
      }
    }
  },
  
  watch: {
    user(newUser) {
      if (newUser) {
        this.editableUser.username = newUser.username || '';
        this.editableUser.email = newUser.email || '';
      }
    }
  }
};
</script>

<style scoped>
.profile {
  width: 100vh;
  margin: 10px auto;
  background-color: rgb(217, 217, 217, 100%);
  border-radius: 30px;
  padding-bottom: 20px;
}

.profile_h1 {
  text-align: center;
  padding-top: 20px;
  font-size: 52px;
  font-family: 'philosopher', sans-serif;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
  padding: 0 20px;
}

.profile-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.profile-label {
  font-weight: bold;
  color: #333;
}

.profile-value {
  color: #555;
}

.profile-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 14px;
}

.save-button {
  margin-top: 20px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  background-color: #28a745;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.save-button:hover {
  background-color: #218838;
}

.logout-button {
  margin-top: 20px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  background-color: #dc3545;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-button:hover {
  background-color: #c82333;
}

/* Стили для блока заказов */
.recent-orders {
  margin-top: 30px;
  padding: 0 20px 10px;
}

.recent-orders h2 {
  font-size: 24px;
  margin-bottom: 15px;
  color: #333;
  font-family: 'philosopher', sans-serif;
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid #3498db;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message, .no-orders {
  padding: 15px;
  text-align: center;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 15px;
}

.error-message {
  color: #721c24;
  background-color: #f8d7da;
}

.order-item {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.order-number {
  font-weight: bold;
  font-size: 16px;
}

.order-status {
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 500;
}

.status-pending {
  background-color: #fff3cd;
  color: #856404;
}

.status-confirmed {
  background-color: #d1ecf1;
  color: #0c5460;
}

.status-completed {
  background-color: #d4edda;
  color: #155724;
}

.status-cancelled {
  background-color: #f8d7da;
  color: #721c24;
}

.order-details {
  display: flex;
  justify-content: space-between;
}

.order-date, .order-total {
  color: #555;
}

.order-total {
  font-weight: bold;
}

.view-all-orders {
  text-align: center;
  margin-top: 20px;
}

.view-all-button {
  display: inline-block;
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border-radius: 4px;
  text-decoration: none;
  transition: background-color 0.3s;
}

.view-all-button:hover {
  background-color: #0056b3;
}

.action-button {
  display: inline-block;
  padding: 8px 16px;
  background-color: #28a745;
  color: white;
  border-radius: 4px;
  text-decoration: none;
  margin-top: 10px;
  transition: background-color 0.3s;
}

.action-button:hover {
  background-color: #218838;
}

@media (max-width: 800px) {
  .profile {
    width: 98vw;
    min-width: unset;
    padding: 10px;
    margin: 10px 0;
  }
  .profile_parent {
    padding: 0;
  }
  .profile_h1 {
    font-size: 32px;
    padding-top: 10px;
  }
  .profile-info {
    gap: 8px;
  }
  .profile-row {
    flex-direction: column;
    align-items: flex-start;
    padding: 8px 5px;
  }
  .profile-label {
    margin-bottom: 4px;
  }
  .profile-input {
    font-size: 16px;
    width: 100%;
  }
  .save-button, .logout-button {
    width: 100%;
    margin-top: 10px;
    font-size: 15px;
    padding: 10px 0;
  }
  .recent-orders h2 {
    font-size: 20px;
  }
}
</style>