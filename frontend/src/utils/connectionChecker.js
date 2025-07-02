import { getApiBaseUrl } from '../config/index.js';
import { getApiConfig } from '../services/api.js';

/**
 * Verifica la conexión con el backend y muestra información de configuración
 */
export const checkConnection = async () => {
  const config = getApiConfig();
  
  console.log('🔧 Configuración actual:', {
    baseURL: config.baseURL,
    timeout: config.timeout,
    devMode: config.devMode,
    enableLogs: config.enableLogs,
  });

  try {
    const response = await fetch(`${config.baseURL}/`);
    if (response.ok) {
      console.log('✅ Conexión exitosa con el backend');
      return { connected: true, data: await response.json() };
    } else {
      console.log('⚠️ Backend responde pero con error:', response.status);
      return { connected: false, error: `HTTP ${response.status}` };
    }
  } catch (error) {
    console.log('❌ Error de conexión con el backend:', error.message);
    return { connected: false, error: error.message };
  }
};

/**
 * Muestra información de la URL del backend actual
 */
export const showBackendInfo = () => {
  const baseURL = getApiBaseUrl();
  console.log('🌐 URL del backend:', baseURL);
  
  if (baseURL.includes('localhost')) {
    console.log('📝 Modo: Desarrollo local');
  } else if (baseURL.includes('render.com')) {
    console.log('🚀 Modo: Producción (Render)');
  } else {
    console.log('🔧 Modo: Personalizado');
  }
};

/**
 * Verifica si estamos en desarrollo o producción
 */
export const getEnvironment = () => {
  const baseURL = getApiBaseUrl();
  
  if (baseURL.includes('localhost')) {
    return 'development';
  } else if (baseURL.includes('render.com')) {
    return 'production';
  } else {
    return 'custom';
  }
}; 