import React, { useState, useEffect } from "react";
import { agentService, graphService, modelService, descriptiveService } from "../../services/api";

const Dashboard = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: "agent",
      content: "¡Hola! Soy tu agente analítico. Puedo ayudarte a analizar tus datos de importación y stock. ¿En qué puedo ayudarte?",
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [graphData, setGraphData] = useState(null);
  const [graphLoading, setGraphLoading] = useState(true);
  const [graphError, setGraphError] = useState(null);
  
  // Estados para gráficas descriptivas
  const [descriptiveGraphs, setDescriptiveGraphs] = useState([]);
  const [selectedGraph, setSelectedGraph] = useState(null);
  const [selectedGraphData, setSelectedGraphData] = useState(null);
  const [descriptiveLoading, setDescriptiveLoading] = useState(false);

  // Cargar la gráfica al montar el componente
  useEffect(() => {
    loadGraph();
    loadDescriptiveGraphs();
  }, []);

  const loadGraph = async () => {
    try {
      setGraphLoading(true);
      setGraphError(null);
      const response = await graphService.getPredictionGraph();
      setGraphData(response.graph_data_url);
    } catch (error) {
      console.error("Error al cargar la gráfica:", error);
      setGraphError(
        error.response?.data?.detail || 
        "Error al cargar la gráfica. Asegúrate de que el modelo predictivo se haya ejecutado."
      );
    } finally {
      setGraphLoading(false);
    }
  };

  const loadDescriptiveGraphs = async () => {
    try {
      const response = await descriptiveService.getDescriptiveGraphs();
      setDescriptiveGraphs(response);
    } catch (error) {
      console.error("Error al cargar gráficas descriptivas:", error);
    }
  };

  const loadSelectedGraph = async (graphId) => {
    try {
      setDescriptiveLoading(true);
      const response = await descriptiveService.getDescriptiveGraph(graphId);
      setSelectedGraphData(response.image_base64);
    } catch (error) {
      console.error("Error al cargar la gráfica descriptiva:", error);
    } finally {
      setDescriptiveLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: "user",
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await agentService.askQuestion(inputMessage);
      
      const agentMessage = {
        id: Date.now() + 1,
        type: "agent",
        content: response.answer,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      console.error("Error al enviar mensaje:", error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: "agent",
        content: "Lo siento, hubo un error al procesar tu pregunta. Por favor, intenta de nuevo.",
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const runModel = async () => {
    try {
      setGraphLoading(true);
      setGraphError(null);
      
      await modelService.runModel();
      
      // Recargar la gráfica después de ejecutar el modelo
      await loadGraph();
      
      // Agregar mensaje de confirmación
      const successMessage = {
        id: Date.now(),
        type: "agent",
        content: "✅ Modelo ejecutado exitosamente. La gráfica ha sido actualizada.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, successMessage]);
    } catch (error) {
      console.error("Error al ejecutar el modelo:", error);
      
      const errorMessage = {
        id: Date.now(),
        type: "agent",
        content: "❌ Error al ejecutar el modelo predictivo. Verifica que los datos estén disponibles.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      setGraphError("Error al ejecutar el modelo");
    } finally {
      setGraphLoading(false);
    }
  };

  const runDescriptiveAnalysis = async () => {
    try {
      setDescriptiveLoading(true);
      
      // Ejecutar el análisis descriptivo
      await descriptiveService.runDescriptiveAnalysis();
      
      // Recargar el catálogo de gráficas
      await loadDescriptiveGraphs();
      
      // Agregar mensaje de confirmación
      const successMessage = {
        id: Date.now(),
        type: "agent",
        content: "✅ Análisis descriptivo ejecutado exitosamente. Las gráficas están listas para visualizar.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, successMessage]);
    } catch (error) {
      console.error("Error al ejecutar el análisis descriptivo:", error);
      
      const errorMessage = {
        id: Date.now(),
        type: "agent",
        content: "❌ Error al ejecutar el análisis descriptivo. Verifica que los datos estén disponibles.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setDescriptiveLoading(false);
    }
  };

  const handleFileUpload = () => {
    // Mostrar mensaje de funcionalidad no disponible
    const uploadMessage = {
      id: Date.now(),
      type: "agent",
      content: "📁 **Funcionalidad de Subida de Archivos**\n\n⚠️ Esta funcionalidad aún no está disponible en esta versión.\n\n🔧 **Próximamente:**\n• Subida de archivos Excel (.xlsx)\n• Subida de archivos CSV (.csv)\n• Procesamiento automático de datos\n• Actualización de análisis en tiempo real\n\n💡 Por ahora, puedes usar los datos existentes para consultar predicciones y análisis descriptivos.",
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, uploadMessage]);
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString('es-ES', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="min-h-screen bg-white flex">
      {/* Sidebar izquierdo con agente AI */}
      <aside className="w-80 h-[630px] mt-4 ml-4 bg-gray-100 border-r border-gray-300 p-4 flex flex-col rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-4">AI Chat Assistant</h2>
        
        {/* Área de mensajes */}
        <div className="flex-1 overflow-y-auto mb-4 space-y-3">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
                  message.type === "user"
                    ? "bg-black text-white"
                    : "bg-white text-gray-800 border border-gray-300"
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
                <div className={`text-xs mt-1 ${
                  message.type === "user" ? "text-blue-100" : "text-gray-500"
                }`}>
                  {formatTime(message.timestamp)}
                </div>
              </div>
            </div>
          ))}
          
          {/* Indicador de carga */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-800 border border-gray-300 px-3 py-2 rounded-lg text-sm">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                  <span>Pensando...</span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Formulario de entrada */}
        <form onSubmit={handleSendMessage} className="flex">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Escribe tu pregunta..."
            className="flex-1 px-3 py-2 border rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputMessage.trim()}
            className="bg-black text-white px-4 py-2 rounded-r-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            ▶
          </button>
        </form>
      </aside>
        
      {/* Contenido Principal */}
      <main className="flex-1 p-6">
        {/* Header */}
        <header className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">American Tactical Dashboard</h1>
          <div className="space-x-2">
            <button
              onClick={runModel}
              disabled={graphLoading}
              className="px-4 py-2 bg-black text-white rounded hover:bg-green-600 disabled:bg-gray-400"
            >
              {graphLoading ? "Ejecutando..." : "Ejecutar Modelo"}
            </button>
            <button
              onClick={runDescriptiveAnalysis}
              disabled={descriptiveLoading}
              className="px-4 py-2 bg-black text-white rounded hover:bg-purple-600 disabled:bg-gray-400"
            >
              {descriptiveLoading ? "Analizando..." : "Análisis Descriptivo"}
            </button>
          </div>
        </header>
  
        {/* Gráficas Principales */}
        <section className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Gráfica de predicciones */}
          <div className="bg-gray-100 p-4 rounded-lg shadow-inner">
            <h2 className="font-semibold mb-2">model prediction</h2>
            <div className="h-80 bg-white rounded border border-dashed flex justify-center items-center">
              {graphLoading ? (
                <span className="text-gray-500">Cargando...</span>
              ) : graphError ? (
                <span className="text-red-500">{graphError}</span>
              ) : graphData ? (
                <img src={graphData} alt="Graph" className="h-full object-contain" />
              ) : (
                <span className="text-gray-400">No disponible</span>
              )}
            </div>
          </div>
  
          {/* Gráfica descriptiva */}
          <div className="bg-gray-100 p-4 rounded-lg shadow-inner">
            <h2 className="font-semibold mb-2">Import Trends</h2>
            <select
              value={selectedGraph || ""}
              onChange={(e) => {
                setSelectedGraph(e.target.value);
                if (e.target.value) loadSelectedGraph(e.target.value);
              }}
              className="mb-2 w-full px-2 py-1 border rounded"
            >
              <option value="">Selecciona gráfica...</option>
              {descriptiveGraphs.map((graph) => (
                <option key={graph.id} value={graph.id}>
                  {graph.name}
                </option>
              ))}
            </select>
            <div className="h-80 bg-white rounded border border-dashed flex justify-center items-center">
              {descriptiveLoading ? (
                <span className="text-gray-500">Cargando...</span>
              ) : selectedGraphData ? (
                <img src={selectedGraphData} alt="Graph" className="h-full object-contain" />
              ) : (
                <span className="text-gray-400">No disponible</span>
              )}
            </div>
          </div>
        </section>
  
        {/* Upload de Archivos */}
        <section className="bg-gray-100 p-3 rounded-lg text-center border border-dashed border-gray-400">
          <p className="mb-2">Drop files here or click to upload</p>
          <input 
            type="file" 
            className="hidden" 
            onChange={handleFileUpload}
            accept=".xlsx,.csv"
          />
          <button 
            onClick={handleFileUpload}
            className="mt-2 px-4 py-2 bg-black text-white rounded hover:bg-gray-700 transition-colors"
          >
            Select Files
          </button>
          <ul className="mt-4 space-y-1 text-sm">
            <li>Q4_Sales_Report.xlsx <span className="text-gray-500 text-xs">2.1 MB</span></li>
            <li>Product_Catalog_2023.csv <span className="text-gray-500 text-xs">1.5 MB</span></li>
          </ul>
        </section>
      </main>
    </div>
  ); 
};

export default Dashboard;
