import { isDevelopment, isLoggingEnabled } from '../config';

// Niveles de log
export const LOG_LEVELS = {
  ERROR: 'error',
  WARN: 'warn',
  INFO: 'info',
  DEBUG: 'debug',
};

// Clase Logger
class Logger {
  constructor() {
    this.isDev = isDevelopment();
    this.isLoggingEnabled = isLoggingEnabled();
  }

  // Método para formatear el mensaje
  formatMessage(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const prefix = `[${timestamp}] [${level.toUpperCase()}]`;
    
    if (data) {
      return `${prefix} ${message}`, data;
    }
    
    return `${prefix} ${message}`;
  }

  // Log de error
  error(message, data = null) {
    if (this.isLoggingEnabled) {
      const formattedMessage = this.formatMessage(LOG_LEVELS.ERROR, message, data);
      console.error(formattedMessage);
    }
  }

  // Log de advertencia
  warn(message, data = null) {
    if (this.isLoggingEnabled) {
      const formattedMessage = this.formatMessage(LOG_LEVELS.WARN, message, data);
      console.warn(formattedMessage);
    }
  }

  // Log de información
  info(message, data = null) {
    if (this.isLoggingEnabled) {
      const formattedMessage = this.formatMessage(LOG_LEVELS.INFO, message, data);
      console.info(formattedMessage);
    }
  }

  // Log de debug (solo en desarrollo)
  debug(message, data = null) {
    if (this.isDev && this.isLoggingEnabled) {
      const formattedMessage = this.formatMessage(LOG_LEVELS.DEBUG, message, data);
      console.debug(formattedMessage);
    }
  }

  // Log de API requests
  apiRequest(method, url, data = null) {
    if (this.isDev) {
      console.log(`🚀 API Request: ${method?.toUpperCase()} ${url}`, data || '');
    }
  }

  // Log de API responses
  apiResponse(status, url, data = null) {
    if (this.isDev) {
      const emoji = status >= 200 && status < 300 ? '✅' : '❌';
      console.log(`${emoji} API Response: ${status} ${url}`, data || '');
    }
  }

  // Log de errores de API
  apiError(error) {
    if (this.isLoggingEnabled) {
      console.error('❌ API Error:', {
        status: error.response?.status,
        message: error.response?.data?.detail || error.message,
        url: error.config?.url,
        method: error.config?.method,
      });
    }
  }

  // Log de errores de componentes
  componentError(componentName, error, props = null) {
    if (this.isLoggingEnabled) {
      console.error(`❌ Component Error [${componentName}]:`, {
        error: error.message,
        stack: error.stack,
        props,
      });
    }
  }

  // Log de eventos de usuario
  userEvent(event, data = null) {
    if (this.isDev) {
      console.log(`👤 User Event: ${event}`, data || '');
    }
  }

  // Log de rendimiento
  performance(operation, duration) {
    if (this.isDev) {
      console.log(`⚡ Performance: ${operation} took ${duration}ms`);
    }
  }
}

// Instancia global del logger
export const logger = new Logger();

// Función helper para logging rápido
export const log = {
  error: (message, data) => logger.error(message, data),
  warn: (message, data) => logger.warn(message, data),
  info: (message, data) => logger.info(message, data),
  debug: (message, data) => logger.debug(message, data),
  api: {
    request: (method, url, data) => logger.apiRequest(method, url, data),
    response: (status, url, data) => logger.apiResponse(status, url, data),
    error: (error) => logger.apiError(error),
  },
  component: (componentName, error, props) => logger.componentError(componentName, error, props),
  user: (event, data) => logger.userEvent(event, data),
  performance: (operation, duration) => logger.performance(operation, duration),
};

export default logger; 