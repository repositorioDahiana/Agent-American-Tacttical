// Configuración centralizada de la aplicación
export const config = {
  // Configuración de la API
  api: {
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: parseInt(import.meta.env.VITE_API_TIMEOUT) || 30000,
  },

  // Configuración de la aplicación
  app: {
    name: import.meta.env.VITE_APP_NAME || 'American Tactical Dashboard',
    version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  },

  // Configuración de desarrollo
  development: {
    devMode: import.meta.env.VITE_DEV_MODE === 'true',
    enableLogs: import.meta.env.VITE_ENABLE_LOGS === 'true',
  },

  // Configuración de CORS
  cors: {
    origin: import.meta.env.VITE_CORS_ORIGIN || 'http://localhost:3000',
  },

  // Configuración de features
  features: {
    fileUpload: false, // Funcionalidad de subida de archivos
    realTimeUpdates: true, // Actualizaciones en tiempo real
    analytics: true, // Análisis y métricas
  },

  // Configuración de UI
  ui: {
    theme: 'light', // light | dark
    language: 'es', // es | en
    timezone: 'America/Mexico_City',
  },
};

// Función para obtener configuración específica
export const getConfig = (key) => {
  const keys = key.split('.');
  let value = config;
  
  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = value[k];
    } else {
      return undefined;
    }
  }
  
  return value;
};

// Función para verificar si estamos en desarrollo
export const isDevelopment = () => {
  return config.development.devMode;
};

// Función para verificar si los logs están habilitados
export const isLoggingEnabled = () => {
  return config.development.enableLogs;
};

// Función para obtener la URL base de la API
export const getApiBaseUrl = () => {
  return config.api.baseURL;
};

// Función para obtener el timeout de la API
export const getApiTimeout = () => {
  return config.api.timeout;
};

export default config; 