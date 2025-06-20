<template>
  <div class="hawk-test-container">
    <h2>Тестирование Hawk Error Tracking</h2>
    
    <div class="test-buttons">
      <button 
        class="test-button" 
        @click="testUnhandledException"
        :disabled="loading.unhandled"
      >
        {{ loading.unhandled ? 'Отправка...' : 'Тест необработанного исключения' }}
      </button>
      
      <button 
        class="test-button" 
        @click="testHandledException"
        :disabled="loading.handled"
      >
        {{ loading.handled ? 'Отправка...' : 'Тест обработанного исключения' }}
      </button>
      
      <button 
        class="test-button" 
        @click="testCustomMessage"
        :disabled="loading.message"
      >
        {{ loading.message ? 'Отправка...' : 'Тест произвольного сообщения' }}
      </button>
      
      <button 
        class="test-button" 
        @click="testApiError"
        :disabled="loading.api"
      >
        {{ loading.api ? 'Отправка...' : 'Тест ошибки API' }}
      </button>
    </div>

    <div v-if="lastTest" class="test-result">
      <h3>Результат последнего теста:</h3>
      <pre>{{ lastTest }}</pre>
    </div>

    <div v-if="error" class="error-message">
      <h3>Ошибка:</h3>
      <pre>{{ error }}</pre>
    </div>
  </div>
</template>

<script>
import hawk from '@/plugins/hawk';
import api from '@/api';

export default {
  name: 'HawkTest',
  data() {
    return {
      loading: {
        unhandled: false,
        handled: false,
        message: false,
        api: false
      },
      lastTest: null,
      error: null
    };
  },
  mounted() {
    // Check Hawk initialization on component mount
    console.log('🦅 Hawk test component mounted');
    console.log('Hawk methods available:', {
      send: typeof hawk.send === 'function',
      sendMessage: typeof hawk.sendMessage === 'function',
      setUser: typeof hawk.setUser === 'function',
      resetUser: typeof hawk.resetUser === 'function'
    });
  },
  methods: {
    async testUnhandledException() {
      try {
        this.loading.unhandled = true;
        this.error = null;
        
        // Создаем исключение
        setTimeout(() => {
          console.log('Симуляция необработанного исключения...');
          // Эта ошибка будет перехвачена глобальным обработчиком Vue
          const nonExistentObject = null;
          nonExistentObject.someMethod(); // Вызовет ошибку
        }, 100);
        
        // Мы не должны достичь этой точки, но на всякий случай
        this.lastTest = {
          type: 'Необработанное исключение',
          time: new Date().toISOString(),
          message: 'Тест запущен'
        };
      } catch (err) {
        this.error = `Ошибка при тестировании: ${err.message}`;
      } finally {
        setTimeout(() => {
          this.loading.unhandled = false;
        }, 1000);
      }
    },
    
    async testHandledException() {
      this.loading.handled = true;
      this.error = null;
      
      try {
        console.log('Симуляция обработанного исключения...');
        const obj = {};
        obj.nonExistent.property = true; // Вызовет ошибку
      } catch (err) {
        // Вручную отправляем ошибку в Hawk
        hawk.send(err, {
          context: {
            source: 'HawkTest.vue',
            method: 'testHandledException',
            custom: 'Это пример обработанного исключения'
          }
        });
        
        this.lastTest = {
          type: 'Обработанное исключение',
          time: new Date().toISOString(),
          message: err.message,
          status: 'Отправлено в Hawk'
        };
      } finally {
        this.loading.handled = false;
      }
    },
    
    async testCustomMessage() {
      this.loading.message = true;
      this.error = null;
      
      try {
        console.log('Отправка произвольного сообщения в Hawk...');
        
        // Отправляем произвольное сообщение без исключения
        await hawk.sendMessage('Тестовое сообщение из приложения Афиша', {
          level: 'info',
          context: {
            source: 'HawkTest.vue',
            method: 'testCustomMessage',
            details: 'Это тестовое информационное сообщение'
          }
        });
        
        this.lastTest = {
          type: 'Произвольное сообщение',
          time: new Date().toISOString(),
          message: 'Тестовое сообщение из приложения Афиша',
          status: 'Отправлено в Hawk'
        };
      } catch (err) {
        console.error('Error sending message to Hawk:', err);
        this.error = `Ошибка при отправке сообщения: ${err.message}`;
      } finally {
        this.loading.message = false;
      }
    },
    
    async testApiError() {
      this.loading.api = true;
      this.error = null;
      
      try {
        console.log('Симуляция ошибки API...');
        
        // Выполняем запрос к несуществующему эндпоинту
        await api.get('/non-existent-endpoint/');
        
        // Этот код не должен выполниться
        this.error = 'Ошибка теста: запрос должен был вернуть ошибку';
      } catch (err) {
        // Ошибка будет автоматически отправлена в Hawk через перехватчик axios
        this.lastTest = {
          type: 'Ошибка API',
          time: new Date().toISOString(),
          url: '/non-existent-endpoint/',
          status: err.response?.status || 'unknown',
          message: err.message,
          note: 'Ошибка должна быть автоматически отправлена в Hawk через axios interceptor'
        };
      } finally {
        this.loading.api = false;
      }
    }
  }
};
</script>

<style scoped>
.hawk-test-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  border: 1px solid #eaeaea;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.9);
}

h2 {
  text-align: center;
  margin-bottom: 20px;
}

.test-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.test-button {
  flex: 1;
  min-width: 200px;
  padding: 10px;
  background-color: #4b70e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.test-button:hover {
  background-color: #3a5bbf;
}

.test-button:disabled {
  background-color: #b8c2e5;
  cursor: not-allowed;
}

.test-result, .error-message {
  margin-top: 20px;
  padding: 15px;
  border-radius: 4px;
}

.test-result {
  background-color: #e8f4fb;
  border: 1px solid #b8e2f2;
}

.error-message {
  background-color: #fdeded;
  border: 1px solid #f2b8b8;
}

pre {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 10px;
  border-radius: 4px;
  overflow: auto;
  white-space: pre-wrap;
}
</style> 