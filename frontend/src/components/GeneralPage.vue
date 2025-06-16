<template>
    <main class="GeneralPage_container" aria-label="Главная страница">
        <span class="GeneralPage_Text" tabindex="0">Teatral</span>
    </main>
    <div class="search-block">
        <form @submit.prevent="handleSearch" class="search-form" role="search" aria-label="Поиск спектаклей">
            <input v-model="searchQuery" type="text" placeholder="Поиск спектаклей..." class="search-input" aria-label="Поиск спектаклей" />
            <button type="submit" class="search-btn">Найти</button>
            <button v-if="searchQuery" type="button" class="reset-btn" @click="resetSearch" aria-label="Сбросить поиск">×</button>
        </form>
        <div class="catalog-link-container">
            <router-link to="/catalog" class="catalog-link">
                <i class="fas fa-filter"></i> Перейти в каталог с фильтрами
            </router-link>
        </div>
    </div>
    <div class="Wrapper">
        <div class="Action">
            <h3>Акции</h3>
            <ul v-if="promotions.length">
                <li v-for="promo in promotions" :key="promo.id">
                    <strong>{{ promo.title }}</strong><br />
                    <span>{{ promo.description }}</span>
                </li>
            </ul>
            <span v-else>Нет акций</span>
        </div>
        <div class="Novinki">
            <h3 v-if="!searchQuery">Последние новинки</h3>
            <h3 v-else>Результаты поиска</h3>
            <ul v-if="performances.length">
                <li v-for="perf in performances" :key="perf.id">
                    <div class="novinki-link-card">
                        <router-link :to="`/performances/${perf.id}`" class="novinki-link" tabindex="0" :aria-label="`Подробнее о спектакле ${perf.name}`">
                            <strong>{{ perf.name }}</strong><br />
                            <span>{{ perf.description }}</span>
                        </router-link>
                        <button class="add-to-cart-btn" @click="addToCart(perf)" aria-label="Добавить в корзину">В корзину</button>
                    </div>
                </li>
            </ul>
            <span v-else>{{ searchQuery ? 'Ничего не найдено' : 'Нет новинок' }}</span>
        </div>
        <div class="Question">
            <h3>Вопросы</h3>
            <ul v-if="questions.length">
                <li v-for="q in questions" :key="q.id">
                    <span>{{ q.text }}</span>
                </li>
            </ul>
            <span v-else>Нет вопросов</span>
        </div>
        <div v-if="isAdmin" class="admin-panel">
            <h3>Админ-панель</h3>
            <router-link to="/admin/products" class="admin-link">Товары</router-link>
            <router-link to="/admin/categories" class="admin-link">Категории</router-link>
            <router-link to="/admin/users" class="admin-link">Пользователи</router-link>
            <router-link to="/admin/reviews" class="admin-link">Отзывы</router-link>
        </div>
    </div>
</template>

<script>
import api from '@/api';

export default {
  data() {
    return {
      promotions: [],
      performances: [],
      questions: [],
      loading: true,
      error: null,
      searchQuery: '',
      lastPerformances: [],
      isAdmin: false,
    };
  },
  async mounted() {
    // Загружаем иконки FontAwesome
    const fontAwesome = document.createElement('link');
    fontAwesome.rel = 'stylesheet';
    fontAwesome.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
    document.head.appendChild(fontAwesome);
    
    try {
      const [promRes, perfRes, questRes] = await Promise.all([
        api.get('promotions/last/'),
        api.get('performances/last/'),
        api.get('questions/last/'),
      ]);
      this.promotions = promRes.data;
      this.performances = perfRes.data;
      this.lastPerformances = perfRes.data;
      this.questions = questRes.data;
      // Проверка роли администратора (пример: /user/ возвращает {is_admin: true})
      const userRes = await api.get('user/');
      this.isAdmin = userRes.data && (userRes.data.is_admin || userRes.data.is_superuser || userRes.data.is_staff);
    } catch (err) {
      this.error = 'Ошибка загрузки данных';
    } finally {
      this.loading = false;
    }
  },
  methods: {
    async handleSearch() {
      if (!this.searchQuery) {
        this.performances = this.lastPerformances;
        return;
      }
      this.loading = true;
      try {
        const res = await api.get('performances/search/', { params: { q: this.searchQuery } });
        this.performances = res.data;
      } catch (err) {
        this.error = 'Ошибка поиска спектаклей';
      } finally {
        this.loading = false;
      }
    },
    resetSearch() {
      this.searchQuery = '';
      this.performances = this.lastPerformances;
    },
    addToCart(performance) {
      let cart = JSON.parse(localStorage.getItem('cart') || '[]');
      const idx = cart.findIndex(i => i.id === performance.id);
      if (idx !== -1) {
        cart[idx].qty += 1;
      } else {
        cart.push({
          id: performance.id,
          name: performance.name,
          image: performance.image,
          qty: 1,
        });
      }
      localStorage.setItem('cart', JSON.stringify(cart));
    },
  },
};
</script>

<style>
.Wrapper {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    align-items: flex-start;
    justify-content: center;
    gap: 40px;
    margin: 40px 0;
}

.Action, .Novinki, .Question {
    background: #fff;
    border-radius: 18px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.10);
    padding: 32px 28px 24px 28px;
    min-width: 320px;
    max-width: 370px;
    width: 100%;
    min-height: 260px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    font-family: 'Philosopher', Arial, sans-serif;
}

.Action h3, .Novinki h3, .Question h3 {
    font-size: 2rem;
    color: #9E0C0C;
    margin-bottom: 18px;
    font-family: 'Vogue', Arial, sans-serif;
    font-weight: 600;
}

.Action ul, .Novinki ul, .Question ul {
    list-style: none;
    padding: 0;
    margin: 0;
    width: 100%;
}

.Action li, .Novinki li, .Question li {
    background: #f7f7f7;
    border-radius: 10px;
    margin-bottom: 14px;
    padding: 14px 16px;
    font-size: 1.1rem;
    color: #222;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    transition: background 0.2s;
}
.Action li:hover, .Novinki li:hover, .Question li:hover {
    background: #f0e6e6;
}

.Action span, .Novinki span, .Question span {
    color: #666;
    font-size: 1rem;
}

.catalog-link-container {
    display: flex;
    justify-content: center;
    margin-top: 15px;
}

.catalog-link {
    display: inline-flex;
    align-items: center;
    background-color: #9E0C0C;
    color: white;
    text-decoration: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: 500;
    transition: background-color 0.2s;
}

.catalog-link:hover {
    background-color: #8a0b0b;
}

.catalog-link i {
    margin-right: 8px;
}

.Action strong, .Novinki strong {
    color: #9E0C0C;
    font-size: 1.15rem;
    font-weight: 700;
}

.GeneralPage_container {
    display: flex;
    justify-content: center;
    height: 50vh;
    align-items: flex-end;
}

.GeneralPage_Text {
    color: #9E0C0C;
    font-size: 250px;
    font-family: 'Vogue';
    font-weight: 500;
    letter-spacing: 5px;
}

.novinki-link {
    color: inherit;
    text-decoration: none;
    display: block;
    width: 100%;
    height: 100%;
    outline: none;
}
.novinki-link:focus, .novinki-link:hover {
    background: #f0e6e6;
    border-radius: 10px;
    text-decoration: underline;
}

.search-block {
    display: flex;
    justify-content: center;
    margin: 30px 0 0 0;
}
.search-form {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    padding: 8px 16px;
}
.search-input {
    font-size: 1.1rem;
    padding: 8px 14px;
    border: 1.5px solid #9E0C0C;
    border-radius: 8px;
    outline: none;
    min-width: 220px;
}
.search-btn {
    background: #9E0C0C;
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
}
.search-btn:hover {
    background: #b91c1c;
}
.reset-btn {
    background: transparent;
    border: none;
    font-size: 1.5rem;
    color: #9E0C0C;
    cursor: pointer;
    margin-left: 4px;
    padding: 0 6px;
    border-radius: 50%;
    line-height: 1;
}
.reset-btn:hover {
    background: #f0e6e6;
}

.novinki-link-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.add-to-cart-btn {
  margin-top: 4px;
  background: #9E0C0C;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 6px 16px;
  font-size: 1em;
  cursor: pointer;
  transition: background 0.2s;
  width: 100%;
}
.add-to-cart-btn:hover {
  background: #b91c1c;
}

.admin-panel {
  background: #f7f7f7;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(158,12,12,0.08);
  padding: 18px 20px;
  margin: 24px auto 0 auto;
  max-width: 370px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-start;
}
.admin-panel h3 {
  color: #9E0C0C;
  font-size: 1.3em;
  margin-bottom: 8px;
}
.admin-link {
  color: #9E0C0C;
  text-decoration: underline;
  font-size: 1.1em;
  cursor: pointer;
}
.admin-link:hover {
  color: #b91c1c;
}

@media (max-width: 1200px) {
    .Wrapper {
        flex-direction: column;
        align-items: center;
        gap: 30px;
    }
    .Action, .Novinki, .Question {
        max-width: 95vw;
        min-width: 0;
    }
}
@media (max-width: 800px) {
    .GeneralPage_Text {
        font-size: 60px;
        text-align: center;
    }
    .Action, .Novinki, .Question {
        padding: 18px 8px 14px 8px;
    }
}
</style>