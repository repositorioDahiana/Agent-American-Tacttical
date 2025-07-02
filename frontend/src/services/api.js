import axios from 'axios';

// Configuración base de axios usando variables de entorno
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT || 30000;

// Configuración de axios con interceptores
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: parseInt(API_TIMEOUT),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para requests
api.interceptors.request.use(
  (config) => {
    // Log en desarrollo
    if (import.meta.env.VITE_DEV_MODE === 'true') {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Interceptor para responses
api.interceptors.response.use(
  (response) => {
    // Log en desarrollo
    if (import.meta.env.VITE_DEV_MODE === 'true') {
      console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    }
    return response;
  },
  (error) => {
    // Log de errores
    if (import.meta.env.VITE_ENABLE_LOGS === 'true') {
      console.error('❌ API Response Error:', {
        status: error.response?.status,
        message: error.response?.data?.detail || error.message,
        url: error.config?.url,
      });
    }
    return Promise.reject(error);
  }
);

// Servicio para el agente conversacional
export const agentService = {
  // Enviar pregunta al agente
  askQuestion: async (question) => {
    try {
      const response = await api.post('/agent/ask', { question });
      return response.data;
    } catch (error) {
      console.error('Error al enviar pregunta al agente:', error);
      throw error;
    }
  },
};

// Servicio para obtener la gráfica
export const graphService = {
  // Obtener la gráfica de predicciones
  getPredictionGraph: async () => {
    try {
      const response = await api.get('/graph');
      return response.data;
    } catch (error) {
      console.error('Error al obtener la gráfica:', error);
      throw error;
    }
  },
};

// Servicio para ejecutar el modelo
export const modelService = {
  // Ejecutar el modelo predictivo
  runModel: async () => {
    try {
      const response = await api.get('/run-model/');
      return response.data;
    } catch (error) {
      console.error('Error al ejecutar el modelo:', error);
      throw error;
    }
  },
};

// Servicio para las gráficas descriptivas
export const descriptiveService = {
  // Ejecutar el análisis descriptivo completo
  runDescriptiveAnalysis: async () => {
    try {
      const response = await api.get('/descriptive/run-analysis');
      return response.data;
    } catch (error) {
      console.error('Error al ejecutar el análisis descriptivo:', error);
      throw error;
    }
  },

  // Obtener el catálogo de gráficas descriptivas
  getDescriptiveGraphs: async () => {
    try {
      const response = await api.get('/descriptive/graphs');
      return response.data;
    } catch (error) {
      console.error('Error al obtener el catálogo de gráficas descriptivas:', error);
      throw error;
    }
  },

  // Obtener una gráfica descriptiva específica
  getDescriptiveGraph: async (graphId) => {
    try {
      const response = await api.get(`/descriptive/graph/${graphId}`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener la gráfica descriptiva:', error);
      throw error;
    }
  },
};

// Función para verificar la conectividad con el backend
export const checkBackendConnection = async () => {
  try {
    const response = await api.get('/health');
    return { connected: true, data: response.data };
  } catch (error) {
    return { connected: false, error: error.message };
  }
};

// Función para obtener la configuración actual
export const getApiConfig = () => {
  return {
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT,
    devMode: import.meta.env.VITE_DEV_MODE === 'true',
    enableLogs: import.meta.env.VITE_ENABLE_LOGS === 'true',
  };
};

export default api; 