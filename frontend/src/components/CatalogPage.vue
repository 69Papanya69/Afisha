<template>
  <div class="catalog-page">
    <h1>Каталог спектаклей</h1>

    <!-- Панель фильтров -->
    <div class="filters-panel">
      <div class="filter-section">
        <h3>Фильтры</h3>
        
        <div class="filter-group">
          <label for="category-filter">Категория:</label>
          <select id="category-filter" v-model="filters.category">
            <option value="">Все категории</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }} ({{ category.performances_count }})
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label for="price-min">Цена от:</label>
          <input type="number" id="price-min" v-model="filters.minPrice" min="0">
        </div>

        <div class="filter-group">
          <label for="price-max">Цена до:</label>
          <input type="number" id="price-max" v-model="filters.maxPrice" min="0">
        </div>

        <div class="filter-group">
          <label for="date-from">Дата от:</label>
          <input type="date" id="date-from" v-model="filters.dateFrom">
        </div>

        <div class="filter-group">
          <label for="date-to">Дата до:</label>
          <input type="date" id="date-to" v-model="filters.dateTo">
        </div>

        <div class="filter-group">
          <label for="search-query">Поиск:</label>
          <input type="text" id="search-query" v-model="filters.keyword" placeholder="Название спектакля...">
        </div>

        <div class="filter-buttons">
          <button @click="applyFilters" class="btn btn-primary">Применить</button>
          <button @click="resetFilters" class="btn btn-secondary">Сбросить</button>
        </div>
      </div>
    </div>

    <!-- Статистика каталога -->
    <div v-if="stats" class="catalog-stats">
      <div class="stat-item">
        <span class="stat-value">{{ stats.total_performances }}</span>
        <span class="stat-label">Спектаклей</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ stats.upcoming_shows }}</span>
        <span class="stat-label">Показов</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ stats.categories_count }}</span>
        <span class="stat-label">Категорий</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ formatPrice(stats.price_range.min) }} - {{ formatPrice(stats.price_range.max) }}</span>
        <span class="stat-label">Диапазон цен</span>
      </div>
    </div>

    <!-- Показ подборок на главной странице каталога -->
    <div v-if="!isFiltering && !selectedCategory" class="catalog-featured">
      <!-- Последние добавленные спектакли -->
      <div class="performances-section" v-if="featured.latest_performances && featured.latest_performances.length > 0">
        <h2>Новинки</h2>
        <div class="performances-grid">
          <div v-for="performance in featured.latest_performances" :key="performance.id" class="performance-card">
            <div class="performance-content" @click="goToPerformance(performance.id)">
              <div class="performance-image">
                <img :src="performance.image || require('@/assets/Bad_img.webp')" :alt="performance.name">
              </div>
              <div class="performance-info">
                <h3>{{ performance.name }}</h3>
                <div class="performance-category">{{ performance.category }}</div>
                <div class="performance-details">
                  <span class="duration">{{ performance.duration_formatted }}</span>
                  <span class="price">{{ performance.min_price }}</span>
                </div>
                <div v-if="performance.nearest_date" class="performance-date">
                  {{ formatDate(performance.nearest_date) }}
                </div>
              </div>
            </div>
            <button @click.stop="addToCart(performance)" class="add-to-cart-btn">В корзину</button>
          </div>
        </div>
      </div>

      <!-- Популярные спектакли -->
      <div class="performances-section" v-if="featured.popular_performances && featured.popular_performances.length > 0">
        <h2>Популярные</h2>
        <div class="performances-grid">
          <div v-for="performance in featured.popular_performances" :key="performance.id" class="performance-card">
            <div class="performance-content" @click="goToPerformance(performance.id)">
              <div class="performance-image">
                <img :src="performance.image || require('@/assets/Bad_img.webp')" :alt="performance.name">
              </div>
              <div class="performance-info">
                <h3>{{ performance.name }}</h3>
                <div class="performance-category">{{ performance.category }}</div>
                <div class="performance-details">
                  <span class="duration">{{ performance.duration_formatted }}</span>
                  <span class="price">{{ performance.min_price }}</span>
                </div>
                <div v-if="performance.nearest_date" class="performance-date">
                  {{ formatDate(performance.nearest_date) }}
                </div>
              </div>
            </div>
            <button @click.stop="addToCart(performance)" class="add-to-cart-btn">В корзину</button>
          </div>
        </div>
      </div>

      <!-- Ближайшие спектакли -->
      <div class="performances-section" v-if="featured.upcoming_performances && featured.upcoming_performances.length > 0">
        <h2>Ближайшие</h2>
        <div class="performances-grid">
          <div v-for="performance in featured.upcoming_performances" :key="performance.id" class="performance-card">
            <div class="performance-content" @click="goToPerformance(performance.id)">
              <div class="performance-image">
                <img :src="performance.image || require('@/assets/Bad_img.webp')" :alt="performance.name">
              </div>
              <div class="performance-info">
                <h3>{{ performance.name }}</h3>
                <div class="performance-category">{{ performance.category }}</div>
                <div class="performance-details">
                  <span class="duration">{{ performance.duration_formatted }}</span>
                  <span class="price">{{ performance.min_price }}</span>
                </div>
                <div v-if="performance.nearest_date" class="performance-date">
                  {{ formatDate(performance.nearest_date) }}
                </div>
              </div>
            </div>
            <button @click.stop="addToCart(performance)" class="add-to-cart-btn">В корзину</button>
          </div>
        </div>
      </div>

      <!-- Бюджетные спектакли -->
      <div class="performances-section" v-if="featured.budget_performances && featured.budget_performances.length > 0">
        <h2>Бюджетные</h2>
        <div class="performances-grid">
          <div v-for="performance in featured.budget_performances" :key="performance.id" class="performance-card">
            <div class="performance-content" @click="goToPerformance(performance.id)">
              <div class="performance-image">
                <img :src="performance.image || require('@/assets/Bad_img.webp')" :alt="performance.name">
              </div>
              <div class="performance-info">
                <h3>{{ performance.name }}</h3>
                <div class="performance-category">{{ performance.category }}</div>
                <div class="performance-details">
                  <span class="duration">{{ performance.duration_formatted }}</span>
                  <span class="price">{{ performance.min_price }}</span>
                </div>
                <div v-if="performance.nearest_date" class="performance-date">
                  {{ formatDate(performance.nearest_date) }}
                </div>
              </div>
            </div>
            <button @click.stop="addToCart(performance)" class="add-to-cart-btn">В корзину</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Результаты поиска или отфильтрованные спектакли -->
    <div v-if="isFiltering && !loading" class="search-results">
      <h2>Результаты поиска</h2>
      <div v-if="filteredPerformances.length > 0" class="performances-grid">
        <div v-for="performance in filteredPerformances" :key="performance.id" class="performance-card">
          <div class="performance-content" @click="goToPerformance(performance.id)">
            <div class="performance-image">
              <img :src="performance.image || require('@/assets/Bad_img.webp')" :alt="performance.name">
            </div>
            <div class="performance-info">
              <h3>{{ performance.name }}</h3>
              <div class="performance-category">{{ performance.category }}</div>
              <div class="performance-details">
                <span class="duration">{{ performance.duration_formatted }}</span>
                <span class="price">{{ performance.min_price }}</span>
              </div>
              <div v-if="performance.nearest_date" class="performance-date">
                {{ formatDate(performance.nearest_date) }}
              </div>
            </div>
          </div>
          <button @click.stop="addToCart(performance)" class="add-to-cart-btn">В корзину</button>
        </div>
      </div>
      <div v-else class="no-results">
        <p>По вашему запросу ничего не найдено</p>
      </div>
    </div>

    <!-- Детали категории -->
    <div v-if="selectedCategory && !loading" class="category-details">
      <div class="category-header">
        <h2>{{ selectedCategory.name }}</h2>
        <button @click="selectedCategory = null" class="btn-back">← К каталогу</button>
      </div>
      <p v-if="selectedCategory.description">{{ selectedCategory.description }}</p>

      <div v-if="selectedCategory.performances.length > 0" class="performances-grid">
        <div v-for="performance in selectedCategory.performances" :key="performance.id" class="performance-card">
          <div class="performance-content" @click="goToPerformance(performance.id)">
            <div class="performance-image">
              <img :src="performance.image || require('@/assets/Bad_img.webp')" :alt="performance.name">
            </div>
            <div class="performance-info">
              <h3>{{ performance.name }}</h3>
              <div class="performance-category">{{ performance.category }}</div>
              <div class="performance-details">
                <span class="duration">{{ performance.duration_formatted }}</span>
                <span class="price">{{ performance.min_price }}</span>
              </div>
              <div v-if="performance.nearest_date" class="performance-date">
                {{ formatDate(performance.nearest_date) }}
              </div>
            </div>
          </div>
          <button @click.stop="addToCart(performance)" class="add-to-cart-btn">В корзину</button>
        </div>
      </div>
      <div v-else class="no-results">
        <p>В этой категории пока нет спектаклей</p>
      </div>
    </div>

    <!-- Навигация по категориям -->
    <div v-if="!isFiltering && !selectedCategory" class="categories-nav">
      <h2>Категории спектаклей</h2>
      <div class="categories-grid">
        <div v-for="category in categories" :key="category.id" class="category-card" @click="viewCategory(category.id)">
          <h3>{{ category.name }}</h3>
          <div class="category-count">{{ category.performances_count }} спектаклей</div>
        </div>
      </div>
    </div>

    <!-- Индикатор загрузки -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Загрузка...</p>
    </div>

    <!-- Сообщение об ошибке -->
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script>
import api from '@/api';
import { mapActions } from 'vuex';

export default {
  name: 'CatalogPage',
  data() {
    return {
      loading: false,
      error: null,
      categories: [],
      featured: {
        latest_performances: [],
        popular_performances: [],
        upcoming_performances: [],
        budget_performances: []
      },
      filters: {
        category: '',
        minPrice: '',
        maxPrice: '',
        dateFrom: '',
        dateTo: '',
        keyword: ''
      },
      filteredPerformances: [],
      selectedCategory: null,
      stats: null,
      isFiltering: false
    };
  },
  async created() {
    this.loading = true;
    try {
      // Загружаем подборки спектаклей и категории одновременно
      const [featuredRes, categoriesRes, statsRes] = await Promise.all([
        api.get('catalog/'),
        api.get('catalog/categories/'),
        api.get('catalog/stats/')
      ]);
      
      this.featured = featuredRes.data;
      this.categories = categoriesRes.data;
      this.stats = statsRes.data;
    } catch (error) {
      console.error('Ошибка при загрузке данных каталога:', error);
      this.error = 'Произошла ошибка при загрузке каталога. Пожалуйста, попробуйте позже.';
    } finally {
      this.loading = false;
    }
  },
  methods: {
    ...mapActions('cart', ['addToCart']),
    
    formatDate(dateString) {
      if (!dateString) return '';
      const options = { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' };
      return new Date(dateString).toLocaleDateString('ru-RU', options);
    },
    
    formatPrice(price) {
      if (price === undefined || price === null) return 'Цена не указана';
      return `${price} ₽`;
    },
    
    async viewCategory(categoryId) {
      this.loading = true;
      try {
        const response = await api.get(`catalog/categories/${categoryId}/`);
        this.selectedCategory = response.data;
      } catch (error) {
        console.error('Ошибка при загрузке категории:', error);
        this.error = 'Не удалось загрузить информацию о категории.';
      } finally {
        this.loading = false;
      }
    },
    
    async applyFilters() {
      this.loading = true;
      this.isFiltering = true;
      this.error = null;
      
      try {
        // Формируем параметры запроса на основе заполненных фильтров
        const params = {};
        
        if (this.filters.category) params.category = this.filters.category;
        if (this.filters.minPrice) params.min_price = this.filters.minPrice;
        if (this.filters.maxPrice) params.max_price = this.filters.maxPrice;
        if (this.filters.dateFrom) params.date_after = this.filters.dateFrom;
        if (this.filters.dateTo) params.date_before = this.filters.dateTo;
        if (this.filters.keyword) params.keyword = this.filters.keyword;
        
        const response = await api.get('catalog/search/', { params });
        this.filteredPerformances = response.data;
        
        // Сбрасываем выбранную категорию при поиске
        this.selectedCategory = null;
      } catch (error) {
        console.error('Ошибка при фильтрации спектаклей:', error);
        this.error = 'Не удалось выполнить поиск по заданным параметрам.';
        this.filteredPerformances = [];
      } finally {
        this.loading = false;
      }
    },
    
    resetFilters() {
      this.filters = {
        category: '',
        minPrice: '',
        maxPrice: '',
        dateFrom: '',
        dateTo: '',
        keyword: ''
      };
      this.isFiltering = false;
      this.filteredPerformances = [];
    },
    
    addToCart(performance) {
      // Получение расписания (для примера берем первый элемент)
      this.loading = true;
      
      api.get(`performances/${performance.id}/schedules/`)
        .then(response => {
          if (response.data && response.data.length > 0) {
            const schedule = response.data[0]; // Берем первое расписание
            
            // Добавление в корзину через Vuex
            this.$store.dispatch('cart/addToCart', { 
              performanceScheduleId: schedule.id,
              quantity: 1
            })
            .then(() => {
              alert(`Спектакль "${performance.name}" добавлен в корзину!`);
            })
            .catch(error => {
              console.error('Ошибка при добавлении в корзину:', error);
              alert('Не удалось добавить спектакль в корзину.');
            })
            .finally(() => {
              this.loading = false;
            });
          } else {
            alert('Нет доступных расписаний для этого спектакля.');
            this.loading = false;
          }
        })
        .catch(error => {
          console.error('Ошибка при получении расписания:', error);
          alert('Не удалось получить информацию о расписании.');
          this.loading = false;
        });
    },
    
    goToPerformance(performanceId) {
      this.$router.push({ name: 'PerformancePage', params: { id: performanceId } });
    }
  }
};
</script>

<style scoped>
.catalog-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  font-size: 2.2rem;
  color: #9E0C0C;
  margin-bottom: 1.5rem;
  text-align: center;
}

h2 {
  font-size: 1.8rem;
  color: #9E0C0C;
  margin: 1.5rem 0;
}

.filters-panel {
  background-color: #f8f8f8;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.filter-section h3 {
  font-size: 1.4rem;
  color: #333;
  margin-bottom: 15px;
}

.filter-group {
  margin-bottom: 15px;
}

.filter-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #555;
}

.filter-group select,
.filter-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
}

.filter-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #9E0C0C;
  color: #fff;
}

.btn-primary:hover {
  background-color: #7d0a0a;
}

.btn-secondary {
  background-color: #ccc;
  color: #333;
}

.btn-secondary:hover {
  background-color: #bbb;
}

.catalog-stats {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  background-color: #fff;
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stat-item {
  text-align: center;
  padding: 10px;
}

.stat-value {
  display: block;
  font-size: 1.8rem;
  font-weight: 700;
  color: #9E0C0C;
}

.stat-label {
  font-size: 1rem;
  color: #666;
}

.performances-section {
  margin-bottom: 40px;
}

.performances-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 25px;
}

.performance-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
}

.performance-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.15);
}

.performance-content {
  cursor: pointer;
  display: block;
  width: 100%;
}

.performance-image {
  height: 180px;
  overflow: hidden;
}

.performance-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.performance-card:hover .performance-image img {
  transform: scale(1.1);
}

.performance-info {
  padding: 15px;
}

.performance-info h3 {
  margin: 0 0 8px;
  font-size: 1.2rem;
  color: #333;
}

.performance-category {
  color: #9E0C0C;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.performance-details {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.9rem;
  color: #666;
}

.performance-date {
  font-size: 0.85rem;
  color: #888;
  font-style: italic;
}

.add-to-cart-btn {
  width: 100%;
  padding: 12px;
  background: #9E0C0C;
  color: white;
  border: none;
  border-radius: 0;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.add-to-cart-btn:hover {
  background: #7d0a0a;
}

.categories-nav {
  margin-top: 40px;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.category-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  padding: 15px;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.15);
  background-color: #f9f3f3;
}

.category-card h3 {
  margin: 0 0 8px;
  color: #9E0C0C;
}

.category-count {
  font-size: 0.9rem;
  color: #666;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-radius: 50%;
  border-top: 4px solid #9E0C0C;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background-color: #ffebee;
  color: #c62828;
  padding: 15px;
  border-radius: 5px;
  margin-top: 20px;
  text-align: center;
}

.no-results {
  text-align: center;
  padding: 40px 0;
  color: #666;
}

.category-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.btn-back {
  background: none;
  border: none;
  color: #9E0C0C;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
}

.btn-back:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .performances-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 15px;
  }
  
  .categories-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }
  
  .catalog-stats {
    flex-direction: column;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .performances-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}
</style> 