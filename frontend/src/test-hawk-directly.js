/**
 * Скрипт для ручного тестирования Hawk 
 * Чтобы запустить, можно импортировать в консоли браузера:
 * import('./test-hawk-directly.js')
 */

import hawk from './plugins/hawk';

// Вывести информацию о Hawk
console.group('🔍 Hawk Manual Test');
console.log('Hawk object:', hawk);
console.log('Methods available:', {
  send: typeof hawk.send === 'function',
  sendMessage: typeof hawk.sendMessage === 'function'
});

// Тестовое сообщение
hawk.sendMessage('Manual test message', {
  level: 'info',
  context: { source: 'manual-test' }
})
  .then(response => console.log('✅ Message sent:', response))
  .catch(error => console.error('❌ Message failed:', error));

// Тестовая ошибка
try {
  throw new Error('Manual test error');
} catch (error) {
  hawk.send(error, {
    context: { source: 'manual-test' }
  })
    .then(response => console.log('✅ Error sent:', response))
    .catch(err => console.error('❌ Error failed:', err));
}

console.groupEnd();

// Экспортируем hawk для возможности дальнейшего использования
export default hawk; 