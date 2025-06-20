<template>
  <div class="error-test">
    <h3>Тестирование Hawk Error Tracking</h3>
    <button @click="testError" class="btn btn-danger">
      Симулировать ошибку
    </button>
    <button @click="testCaughtError" class="btn btn-warning">
      Отправить отловленную ошибку
    </button>
  </div>
</template>

<script>
import hawk from '../plugins/hawk';

export default {
  name: 'ErrorTestComponent',
  methods: {
    testError() {
      // This will be caught by the global Vue error handler and reported to Hawk
      const nonExistentObject = null;
      nonExistentObject.someMethod();
    },
    
    testCaughtError() {
      try {
        // Create a deliberate error
        const a = {};
        a.nonExistent.property = 1;
      } catch (error) {
        // Manually send to Hawk with custom context
        hawk.send(error, {
          context: {
            message: 'Manually caught and reported error',
            location: 'ErrorTestComponent.testCaughtError'
          }
        });
      }
    }
  }
}
</script>

<style scoped>
.error-test {
  padding: 20px;
  margin: 20px 0;
  border: 1px solid #eaeaea;
  border-radius: 4px;
}

.btn {
  padding: 8px 16px;
  margin-right: 10px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
  border: none;
}

.btn-warning {
  background-color: #ffc107;
  color: #212529;
  border: none;
}
</style> 