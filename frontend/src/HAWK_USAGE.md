# Hawk Error Tracking - Руководство по использованию

## Обзор

В проекте "Афиша" интегрирована система мониторинга ошибок Hawk, которая автоматически отслеживает и отправляет информацию об ошибках на сервер Hawk. Это помогает нам быстро обнаруживать и исправлять проблемы в приложении.

## Что отслеживается автоматически

- Ошибки JavaScript в браузере
- Ошибки внутри Vue-компонентов
- Ошибки API-запросов (через интеграцию с Axios)

## Как вручную отправить ошибку в Hawk

### Импорт модуля Hawk

```javascript
import hawk from '@/plugins/hawk';
```

### Отправка ошибки

```javascript
try {
  // Код, который может вызвать ошибку
  throw new Error('Пример ошибки');
} catch (error) {
  // Отправляем ошибку в Hawk с дополнительным контекстом
  hawk.send(error, {
    context: {
      // Любая дополнительная информация
      component: 'MyComponent',
      action: 'userAction',
      additionalData: { /* данные */ }
    }
  }).then(() => {
    console.log('Ошибка отправлена в Hawk');
  }).catch(err => {
    console.error('Не удалось отправить ошибку в Hawk', err);
  });
}
```

### Отправка сообщения без исключения

```javascript
hawk.sendMessage('Что-то пошло не так', {
  level: 'warning', // или 'error', 'info'
  context: {
    details: 'Подробности о проблеме'
  }
}).then(() => {
  console.log('Сообщение отправлено в Hawk');
}).catch(err => {
  console.error('Не удалось отправить сообщение в Hawk', err);
});
```

## Добавление информации о пользователе

Чтобы добавить информацию о текущем пользователе ко всем отправляемым ошибкам:

```javascript
// После аутентификации пользователя
hawk.setUser({
  id: user.id,
  name: user.username
});

// При выходе пользователя
hawk.resetUser();
```

## Тестирование отправки ошибок

Для тестирования интеграции с Hawk доступны:

1. **Страница тестирования** - доступна по адресу `/hawk-test` для администраторов
   - Позволяет тестировать разные типы ошибок и сообщений

2. **Скрипты проверки**:
   - `src/check-hawk.js` - автоматически запускается в режиме разработки
   - `src/test-hawk-directly.js` - можно импортировать вручную в консоли браузера

3. **Проверка в консоли браузера**:
   ```javascript
   import(/* webpackChunkName: "test-hawk" */ './test-hawk-directly.js')
     .then(module => console.log('Test completed'))
   ```

## Доступ к Hawk из компонентов Vue

В компонентах Vue можно использовать Hawk через глобальный объект `$hawk`:

```javascript
export default {
  methods: {
    someMethod() {
      try {
        // код с потенциальной ошибкой
      } catch (error) {
        this.$hawk.send(error, {
          context: { /* данные */ }
        });
      }
    },
    logMessage() {
      this.$hawk.sendMessage('Информационное сообщение', {
        level: 'info',
        context: { /* данные */ }
      });
    }
  }
}
```

## Доступ к панели управления Hawk

Панель управления Hawk доступна по адресу [https://hawk.so](https://hawk.so) с учетными данными администратора проекта.

## Структура реализации

- `plugins/hawk.js` - основной модуль интеграции с Hawk
- `components/HawkTest.vue` - компонент для тестирования
- `store/modules/auth.js` - интеграция с аутентификацией пользователей
- `plugins/axios.js` - интеграция с API-запросами

## Устранение неполадок

Если интеграция с Hawk не работает:

1. Проверьте консоль браузера на наличие ошибок
2. Убедитесь, что токен интеграции в `plugins/hawk.js` актуален
3. Проверьте сетевые запросы к Hawk в панели Network инструментов разработчика
4. Запустите `import('./test-hawk-directly.js')` в консоли для диагностики 