/**
 * Скрипт для проверки инициализации и настройки Hawk в приложении.
 * Запускается автоматически в режиме разработки.
 */

(function checkHawk() {
  console.group('🦅 Hawk Integration Check');
  
  try {
    // Проверка наличия Hawk в window (только если загружается из CDN)
    const hasGlobalHawk = typeof window !== 'undefined' && window.HawkCatcher;
    console.log('Global Hawk found:', hasGlobalHawk ? 'YES ✅' : 'NO ❌ (expected if using NPM package)');
    
    // Импортируем локально
    import('./plugins/hawk.js').then((hawkModule) => {
      const hawk = hawkModule.default;
      
      // Проверка инициализации экземпляра Hawk
      if (!hawk) {
        console.error('❌ Hawk instance not found in /plugins/hawk.js');
        return;
      }
      
      console.log('Local Hawk instance:', hawk ? 'Found ✅' : 'Not found ❌');
      console.log('Send method available:', typeof hawk.send === 'function' ? 'YES ✅' : 'NO ❌');
      console.log('SendMessage method available:', typeof hawk.sendMessage === 'function' ? 'YES ✅' : 'NO ❌');
      
      // Отправка тестового сообщения
      console.log('Sending test message to Hawk...');
      hawk.sendMessage('[TEST] Hawk initialization check', {
        level: 'info',
        context: {
          source: 'check-hawk.js',
          environment: process.env.NODE_ENV,
          timestamp: new Date().toISOString()
        }
      }).then(() => {
        console.log('Test message sent successfully ✅');
      }).catch((err) => {
        console.error('Failed to send test message ❌', err);
      });
      
      // Отправка тестовой ошибки
      console.log('Sending test error to Hawk...');
      try {
        throw new Error('[TEST] Hawk error tracking test');
      } catch (error) {
        hawk.send(error, {
          context: {
            source: 'check-hawk.js',
            test: true
          }
        }).then(() => {
          console.log('Test error sent successfully ✅');
        }).catch((err) => {
          console.error('Failed to send test error ❌', err);
        });
      }
      
    }).catch((err) => {
      console.error('❌ Error importing Hawk module:', err);
    });
    
  } catch (err) {
    console.error('❌ Error checking Hawk configuration:', err);
  }
  
  console.groupEnd();
})(); 