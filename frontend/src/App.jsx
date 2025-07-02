import { Routes, Route } from "react-router-dom";
import { useEffect } from "react";
import Home from "./components/pages/Home";
import Dashboard from "./components/pages/Dashboard";
import Header from "./components/layouts/Header";
import { showBackendInfo, checkConnection } from "./utils/connectionChecker.js";

function App() {
  useEffect(() => {
    // Mostrar información de configuración al cargar la app
    showBackendInfo();
    
    // Verificar conexión con el backend
    checkConnection().then((result) => {
      if (result.connected) {
        console.log('🎉 Aplicación conectada correctamente');
      } else {
        console.warn('⚠️ Problema de conexión con el backend:', result.error);
      }
    });
  }, []);

  return (
    <div>
      <Header />
      <div className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
