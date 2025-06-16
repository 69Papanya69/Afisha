<template>
  <main class="performance-detail" v-if="performance" aria-label="Детали спектакля">
    <h1>{{ performance.name }}</h1>
    <img :src="performance.image" :alt="performance.name" class="performance-detail-image" tabindex="0" />
    <p class="performance-description">{{ performance.description }}</p>
    <div class="performance-info">
    <p v-if="performance.category"><strong>Категория:</strong> {{ performance.category }}</p>
    <p v-if="performance.duration_time"><strong>Длительность:</strong> {{ formatDuration(performance.duration_time) }}</p>
    </div>
    
    <!-- Расписание и билеты на спектакль -->
    <div class="schedule-container">
      <h2 class="schedule-title">Расписание и билеты</h2>
      
      <div v-if="schedulesLoading" class="loading">
        <div class="loader"></div>
        <p>Загрузка расписания...</p>
      </div>
      
      <div v-else-if="schedulesError" class="error-message">
        <i class="fas fa-exclamation-circle"></i>
        <p>{{ schedulesError }}</p>
      </div>
      
      <div v-else-if="schedules.length === 0" class="empty-message">
        <i class="fas fa-ticket-alt"></i>
        <p>Нет доступных сеансов для этого спектакля</p>
      </div>
      
      <div v-else class="schedule-content">
        <!-- Фильтры для расписания -->
        <div class="schedule-filters">
          <div class="filter-group">
            <label for="date-filter">Дата:</label>
            <select id="date-filter" v-model="dateFilter" @change="applyFilters">
              <option value="">Все даты</option>
              <option v-for="date in availableDates" :key="date" :value="date">
                {{ formatDateShort(date) }}
              </option>
            </select>
        </div>
        
          <div class="filter-group">
            <label for="theater-filter">Театр:</label>
            <select id="theater-filter" v-model="theaterFilter" @change="applyFilters">
              <option value="">Все театры</option>
              <option v-for="theater in availableTheaters" :key="theater" :value="theater">
                {{ theater }}
              </option>
            </select>
        </div>
        
          <button class="reset-filters-btn" @click="resetFilters">
            <i class="fas fa-undo"></i> Сбросить фильтры
          </button>
            </div>
            
        <!-- Сетка расписания -->
        <div class="schedule-grid">
          <div v-for="item in filteredSchedules" :key="item.id" class="schedule-item">
            <div class="schedule-date">
              <div class="date-box">
                <div class="date-day">{{ getDayFromDate(item.date_time) }}</div>
                <div class="date-month">{{ getMonthFromDate(item.date_time) }}</div>
              </div>
              <div class="date-time">{{ getTimeFromDate(item.date_time) }}</div>
                </div>
                
            <div class="schedule-info">
              <div class="theater-name">{{ item.theater_name }}</div>
              <div class="hall-info">Зал: {{ item.hall_number }}</div>
              <div class="seats-info" :class="{'low-seats': item.available_seats < 10}">
                <i class="fas fa-chair"></i>
                <span>{{ item.available_seats }} {{ getSeatsPluralForm(item.available_seats) }}</span>
              </div>
            </div>
            
            <div class="schedule-purchase">
              <div class="price-tag">{{ formatPrice(item.price) }} ₽</div>
              
              <div class="quantity-selector">
                <button 
                  class="qty-btn decrease" 
                  @click="decreaseQuantity(item)" 
                  :disabled="quantities[item.id] <= 1"
                >
                  <i class="fas fa-minus"></i>
                </button>
                <span class="qty-value">{{ quantities[item.id] || 1 }}</span>
                <button 
                  class="qty-btn increase" 
                  @click="increaseQuantity(item)" 
                  :disabled="quantities[item.id] >= item.available_seats"
                >
                  <i class="fas fa-plus"></i>
                </button>
              </div>
              
              <button 
                class="add-to-cart-btn" 
                @click="addToCartItem(item)"
                :disabled="cartLoading || item.available_seats === 0"
              >
                <i class="fas fa-shopping-cart"></i>
                <span>
                  <template v-if="cartLoading">Добавление...</template>
                  <template v-else-if="item.available_seats === 0">Нет мест</template>
                  <template v-else>В корзину</template>
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <button v-if="isAdmin" class="admin-delete-btn" @click="deletePerformance" aria-label="Удалить спектакль">Удалить спектакль</button>
    
    <section class="reviews-block">
      <h2>Отзывы</h2>
      <ul v-if="performance.reviews && performance.reviews.length">
        <li v-for="review in performance.reviews" :key="review.id" class="review-item">
          <div v-if="isReviewEditing(review)">
            <textarea v-model="editReviewText" class="edit-review-textarea"></textarea>
            <button @click="saveReviewEdit(review)" :disabled="reviewLoading">Сохранить</button>
            <button @click="cancelReviewEdit">Отмена</button>
            <span v-if="reviewError" class="review-error">{{ reviewError }}</span>
          </div>
          <div v-else>
            <strong>{{ review.user || 'Аноним' }}</strong> <span class="review-date">({{ formatDate(review.created_at) }})</span><br />
            <span>{{ review.text }}</span>
            <template v-if="canEditOrDelete(review)">
              <button class="review-action-btn" @click="startReviewEdit(review)">Редактировать</button>
              <button class="review-action-btn" @click="deleteReview(review)">Удалить</button>
            </template>
          </div>
        </li>
      </ul>
      <span v-else>Пока нет отзывов</span>
      <form @submit.prevent="submitReview" class="review-form">
        <textarea v-model="newReview" placeholder="Оставьте свой отзыв..." required aria-label="Текст отзыва"></textarea>
        <button type="submit" :disabled="reviewLoading">{{ reviewLoading ? 'Отправка...' : 'Оставить отзыв' }}</button>
        <span v-if="reviewError" class="review-error">{{ reviewError }}</span>
      </form>
    </section>
    <router-link to="/general" class="back-link" aria-label="Назад к каталогу">
      <i class="fas fa-arrow-left"></i> Назад к спектаклям
    </router-link>
  </main>
  <div v-else class="loading" aria-live="polite">
    <div class="loader"></div>
    <p>Загрузка спектакля...</p>
  </div>
</template>

<script>
import api from '@/api';
import { mapState, mapActions } from 'vuex';
import { reactive } from 'vue';

export default {
  data() {
    return {
      performance: null,
      error: null,
      newReview: '',
      reviewLoading: false,
      reviewError: null,
      editingReviewId: null,
      editReviewText: '',
      
      // Данные для расписания и товаров
      schedules: [],
      products: [], // Добавляем отдельный массив для товаров
      schedulesLoading: false,
      schedulesError: null,
      quantities: reactive({}),
      cartLoading: false,
      dateFilter: '',
      theaterFilter: '',
      availableDates: [],
      availableTheaters: []
    };
  },
  computed: {
    ...mapState({
      user: state => state.auth?.user,
      cartLoadingState: state => state.cart?.loading,
      cartError: state => state.cart?.error
    }),
    isAdmin() {
      return this.user && (this.user.is_admin || this.user.is_superuser || this.user.is_staff);
    },
    filteredSchedules() {
      return this.schedules.filter(schedule => {
        // Фильтр по дате (без учёта времени)
        const dateMatch = !this.dateFilter || 
          (schedule.date_time && new Date(schedule.date_time).toISOString().split('T')[0] === this.dateFilter);
        
        // Фильтр по театру
        const theaterMatch = !this.theaterFilter || schedule.theater_name === this.theaterFilter;
        
        return dateMatch && theaterMatch;
      });
    }
  },
  mounted() {
    this.fetchPerformance();
    this.fetchSchedules();
    
    // Загружаем иконки FontAwesome, если их еще нет
    if (!document.querySelector('link[href*="font-awesome"]')) {
      const fontAwesome = document.createElement('link');
      fontAwesome.rel = 'stylesheet';
      fontAwesome.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
      document.head.appendChild(fontAwesome);
    }
  },
  methods: {
    ...mapActions('cart', ['addToCart', 'fetchCartItems']),
    
    // Метод добавления в корзину
    async addToCartItem(item) {
      if (!this.$store.getters['auth/isAuthenticated']) {
        alert('Пожалуйста, войдите в систему, чтобы добавить товар в корзину');
        this.$router.push('/login');
        return;
      }
      
      try {
        this.cartLoading = true;
        
        // Добавляем в корзину через Vuex
        await this.addToCart({
          performanceScheduleId: item.id,
          quantity: this.quantities[item.id] || 1
        });
        
        // Показываем сообщение об успешном добавлении
        alert(`Билет успешно добавлен в корзину: ${item.performance_name || 'Спектакль'} (${this.quantities[item.id] || 1} шт.)`);
      } catch (error) {
        console.error('Ошибка при добавлении в корзину:', error);
        alert(error.response?.data?.error || 'Произошла ошибка при добавлении в корзину');
      } finally {
        this.cartLoading = false;
      }
    },
    
    // Методы для управления количеством
    increaseQuantity(item) {
      if (!this.quantities[item.id]) {
        this.quantities[item.id] = 1;
      }
      if (this.quantities[item.id] < item.available_seats) {
        this.quantities[item.id]++;
      }
    },
    
    decreaseQuantity(item) {
      if (!this.quantities[item.id]) {
        this.quantities[item.id] = 1;
      }
      if (this.quantities[item.id] > 1) {
        this.quantities[item.id]--;
      }
    },
    
    formatPrice(price) {
      return parseFloat(price).toFixed(2);
    },
    
    // Методы для работы с отзывами
    canEditOrDelete(review) {
      // Только если пользователь авторизован и это его отзыв, либо админ
      return (
        (this.user && review.user && this.user.username === review.user) ||
        (this.user && (this.user.is_admin || this.user.is_superuser || this.user.is_staff))
      );
    },
    isReviewEditing(review) {
      return this.editingReviewId === review.id;
    },
    startReviewEdit(review) {
      this.editingReviewId = review.id;
      this.editReviewText = review.text;
      this.reviewError = null;
    },
    cancelReviewEdit() {
      this.editingReviewId = null;
      this.editReviewText = '';
      this.reviewError = null;
    },
    async saveReviewEdit(review) {
      this.reviewLoading = true;
      this.reviewError = null;
      try {
        await api.put(`reviews/${review.id}/update/`, { text: this.editReviewText });
        review.text = this.editReviewText;
        this.cancelReviewEdit();
      } catch (err) {
        this.reviewError = 'Ошибка при редактировании отзыва';
      } finally {
        this.reviewLoading = false;
      }
    },
    async deleteReview(review) {
      if (!this.canEditOrDelete(review)) return;
      if (!confirm('Удалить этот отзыв?')) return;
      this.reviewLoading = true;
      this.reviewError = null;
      try {
        if (this.isAdmin) {
          await api.delete(`reviews/${review.id}/admin_delete/`);
        } else {
          await api.delete(`reviews/${review.id}/delete/`);
        }
        this.performance.reviews = this.performance.reviews.filter(r => r.id !== review.id);
      } catch (err) {
        this.reviewError = 'Ошибка при удалении отзыва';
      } finally {
        this.reviewLoading = false;
      }
    },
    async deletePerformance() {
      if (!this.isAdmin) return;
      if (!confirm('Удалить этот спектакль?')) return;
      this.reviewLoading = true;
      try {
        await api.delete(`performances/${this.performance.id}/admin_delete/`);
        this.$router.push('/catalog');
      } catch (err) {
        alert('Ошибка при удалении спектакля');
      } finally {
        this.reviewLoading = false;
      }
    },
    async fetchPerformance() {
      try {
        const id = this.$route.params.id;
        const response = await api.get(`performances/${id}/`);
        this.performance = response.data;
      } catch (err) {
        this.error = 'Не удалось загрузить спектакль';
      }
    },
    async submitReview() {
      this.reviewLoading = true;
      this.reviewError = null;
      try {
        const id = this.$route.params.id;
        const response = await api.post(`performances/${id}/add_review/`, { text: this.newReview });
        // Добавляем новый отзыв в список отзывов без перезагрузки
        const newReviewObj = response.data || {
          id: Date.now(),
          user: this.user?.username || 'Вы',
          text: this.newReview,
          created_at: new Date().toISOString(),
        };
        if (this.performance && Array.isArray(this.performance.reviews)) {
          this.performance.reviews.unshift(newReviewObj);
        }
        this.newReview = '';
      } catch (err) {
        this.reviewError = 'Ошибка при отправке отзыва';
      } finally {
        this.reviewLoading = false;
      }
    },
    
    // Получение данных о расписаниях
    async fetchSchedules() {
      this.schedulesLoading = true;
      this.schedulesError = null;
      
      try {
        const performanceId = this.$route.params.id;
        const scheduleResponse = await api.get(`performances/${performanceId}/schedules/`);
        this.schedules = scheduleResponse.data || [];
          
        // Инициализируем количества для каждого расписания
          this.schedules.forEach(item => {
            this.quantities[item.id] = 1;
          });
        
        // Извлекаем уникальные даты и театры для фильтров
        this.processScheduleData();
        
      } catch (error) {
        console.error('Ошибка при загрузке расписания:', error);
        this.schedulesError = 'Не удалось загрузить расписание спектакля';
      } finally {
        this.schedulesLoading = false;
      }
    },
    
    // Обработка данных расписания для фильтров
    processScheduleData() {
      // Извлечение уникальных дат
      const dateSet = new Set();
      this.schedules.forEach(item => {
        if (item.date_time) {
          // Получаем только дату без времени (YYYY-MM-DD)
          const dateOnly = new Date(item.date_time).toISOString().split('T')[0];
          dateSet.add(dateOnly);
        }
      });
      this.availableDates = [...dateSet].sort();
        
      // Извлечение уникальных театров
      const theaterSet = new Set();
      this.schedules.forEach(item => {
        if (item.theater_name) {
          theaterSet.add(item.theater_name);
        }
      });
      this.availableTheaters = [...theaterSet].sort();
    },
    
    // Применение фильтров
    applyFilters() {
      // Уже реализовано через computed свойство filteredSchedules
      console.log('Фильтры применены:', { date: this.dateFilter, theater: this.theaterFilter });
    },
    
    // Сброс фильтров
    resetFilters() {
      this.dateFilter = '';
      this.theaterFilter = '';
    },
    
    // Вспомогательные методы форматирования
    formatDateTime(dateTimeString) {
      if (!dateTimeString) return '';
      
      const date = new Date(dateTimeString);
      return new Intl.DateTimeFormat('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    },
    
    formatDuration(duration) {
      // Ожидается формат "HH:MM:SS" или "PT1H30M"
      if (!duration) return '';
      if (typeof duration === 'string' && duration.includes(':')) {
        const [h, m] = duration.split(':');
        return `${h} ч ${m} мин`;
      }
      return duration;
    },
    
    formatDate(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString('ru-RU', { year: 'numeric', month: 'short', day: 'numeric' });
    },
    
    formatDateShort(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
    },
    

    
    getDayFromDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      return date.toLocaleDateString('ru-RU', { day: '2-digit' });
    },
    
    getMonthFromDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      return date.toLocaleDateString('ru-RU', { month: 'short' });
    },
    
    getTimeFromDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    },
    
    getSeatsPluralForm(seats) {
      if (seats === 1) {
        return 'место';
      } else if (seats >= 2 && seats <= 4) {
        return 'места';
      } else {
        return 'мест';
      }
    },
  }
};
</script>

<style scoped>
.performance-detail {
  max-width: 1000px;
  margin: 40px auto;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  padding: 32px;
  color: #ffffff;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 1.5rem;
  color: #ffffff;
  font-family: 'Vogue', sans-serif;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.performance-detail-image {
  width: 100%;
  max-width: 600px;
  border-radius: 8px;
  margin: 20px auto;
  box-shadow: 0 8px 20px rgba(0,0,0,0.3);
  display: block;
}

.performance-description {
  font-size: 18px;
  margin: 1.5rem 0;
  line-height: 1.6;
  text-align: justify;
}

.performance-info {
  display: flex;
  gap: 2rem;
  justify-content: center;
  margin: 1rem 0;
}

/* Стили для расписания */
.schedule-container {
  margin: 2rem 0;
  padding: 1.5rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
}

.schedule-title {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  color: #ffffff;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 0.5rem;
  text-align: center;
}

.schedule-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  justify-content: center;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: bold;
  font-size: 0.9rem;
}

.filter-group select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.5rem;
  border-radius: 4px;
  color: white;
  font-size: 0.9rem;
}

.filter-group select option {
  background: #333;
  color: white;
}

.reset-filters-btn {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.reset-filters-btn:hover {
  background: rgba(255, 255, 255, 0.25);
}

.schedule-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.schedule-item {
  display: grid;
  grid-template-columns: 100px 1fr 200px;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 1rem;
  align-items: center;
  transition: all 0.3s ease;
}

.schedule-item:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.schedule-date {
  text-align: center;
}

.date-box {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.5rem;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.date-day {
  font-size: 1.5rem;
  font-weight: bold;
}

.date-month {
  font-size: 0.9rem;
  opacity: 0.8;
}

.date-time {
  font-size: 1.1rem;
  font-weight: bold;
  color: #ff4081;
}

.schedule-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.theater-name {
  font-weight: bold;
  font-size: 1.1rem;
}

.hall-info {
  font-size: 0.9rem;
  opacity: 0.8;
}

.seats-info {
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.low-seats {
  color: #ff4081;
}

.schedule-purchase {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.price-tag {
  font-size: 1.4rem;
  font-weight: bold;
  color: #ffffff;
}

.quantity-selector {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 0.25rem 0.5rem;
}

.qty-btn {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.qty-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}

.qty-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.qty-value {
  min-width: 30px;
  text-align: center;
  font-weight: bold;
}

.add-to-cart-btn {
  background: linear-gradient(135deg, #ff4081 0%, #c2185b 100%);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  color: white;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.3s;
  width: 100%;
  justify-content: center;
}

.add-to-cart-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.add-to-cart-btn:disabled {
  background: #666;
  cursor: not-allowed;
  opacity: 0.7;
}

/* Стили для отзывов */
.reviews-block {
  margin-top: 3rem;
  padding: 1.5rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
}

.reviews-block h2 {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 0.5rem;
}

.review-item {
  background: rgba(255, 255, 255, 0.1);
  margin-bottom: 1rem;
  padding: 1rem;
  border-radius: 8px;
  list-style-type: none;
}

.review-date {
  opacity: 0.7;
  font-size: 0.9rem;
}

.review-action-btn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  margin-top: 0.5rem;
  margin-right: 0.5rem;
  cursor: pointer;
}

.review-action-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.review-form {
  margin-top: 1.5rem;
}

.review-form textarea {
  width: 100%;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  min-height: 100px;
  margin-bottom: 1rem;
  resize: vertical;
}

.review-form button {
  background: linear-gradient(135deg, #ff4081 0%, #c2185b 100%);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.review-form button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.review-form button:disabled {
  background: #666;
  cursor: not-allowed;
  opacity: 0.7;
}

.review-error {
  color: #ff4081;
  display: block;
  margin-top: 0.5rem;
}

.edit-review-textarea {
  width: 100%;
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  min-height: 80px;
  margin-bottom: 0.75rem;
  resize: vertical;
}

.admin-delete-btn {
  background: #e53935;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  cursor: pointer;
  font-weight: bold;
  margin: 1rem 0;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
  text-decoration: none;
  margin-top: 1.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  transition: all 0.3s;
}

.back-link:hover {
  background: rgba(255, 255, 255, 0.2);
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: white;
}

.loader {
  border: 5px solid rgba(255, 255, 255, 0.2);
  border-top: 5px solid #ff4081;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message, .empty-message {
  text-align: center;
  padding: 2rem;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.2);
}

.error-message i, .empty-message i {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: #ff4081;
}

@media (max-width: 768px) {
  .performance-detail {
    padding: 1.5rem;
  }
  
  .schedule-item {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
  }
  
  .schedule-date {
    display: flex;
    gap: 1rem;
    align-items: center;
    justify-content: center;
  }
  
  .date-box {
    margin-bottom: 0;
  }
  
  .schedule-info, .schedule-purchase {
    text-align: center;
  }
  
  .performance-info {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>