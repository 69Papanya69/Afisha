import HawkCatcher from '@hawk.so/javascript';

/**
 * Initialize Hawk with the integration token
 */
const hawk = new HawkCatcher({
  token: 'eyJpbnRlZ3JhdGlvbklkIjoiZDZmZmMyMjMtNjVkMS00OTdiLWI2MWItZmE1YzUyOGM1ZTJjIiwic2VjcmV0IjoiNjMzMGE0NGUtMzM0Ni00MzFmLWFlMWMtMmM2NGQ5N2RhMDVkIn0=',
  context: {
    environment: process.env.NODE_ENV
  }
});

/**
 * Add helper methods that might not be available in the Hawk API
 */
const enhancedHawk = {
  // Forward the original Hawk methods
  send: (error, options) => hawk.send(error, options),
  setUser: (user) => hawk.setUser?.(user) || console.warn("setUser method not available"),
  resetUser: () => hawk.resetUser?.() || console.warn("resetUser method not available"),
  
  // Custom method for sending messages without errors
  sendMessage: (message, options = {}) => {
    try {
      // Create a custom error to send with the message
      const customError = new Error(message);
      
      // Strip the stack trace as it's not relevant for a message
      customError.stack = null;
      
      // Set type to identify this as a message, not an error
      const context = options.context || {};
      context._messageType = 'custom_message';
      
      // Send through the Hawk API
      return hawk.send(customError, {
        ...options,
        context: context,
      });
    } catch (err) {
      console.error('Failed to send message to Hawk:', err);
      return Promise.reject(err);
    }
  }
};

export const hawkPlugin = {
  install: (app) => {
    // Set up global error handler for Vue 3
    app.config.errorHandler = (error, instance, info) => {
      // Report the error to Hawk
      enhancedHawk.send(error, {
        context: {
          vueInfo: info,
          componentName: instance?.$options?.name || 'Unknown Component'
        }
      });
      
      // Log the error to console
      console.error('Vue Error:', error);
    };
    
    // Make hawk available globally
    app.config.globalProperties.$hawk = enhancedHawk;
  }
};

// Log initialization for debugging
console.log('🦅 Hawk initialized with token:', enhancedHawk.send ? 'VALID' : 'INVALID');

export default enhancedHawk; 