import os
from .csv_loader import CSVLoader
from .graph_loader import GraphLoader
from .stock_analyzer import StockAnalyzer
from dotenv import load_dotenv
from openai import OpenAI
from app.models import descriptive_analysis

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


class PredictiveAgent:
    def __init__(self):
        try:
            self.csv_loader = CSVLoader()
            self.df = self.csv_loader.df
            self.graph_base64 = GraphLoader().get_base64_data_url()
            self.stock_analyzer = StockAnalyzer()
        except Exception as e:
            # Re-lanzar la excepción para que se maneje en el nivel superior
            raise Exception(f"Error al inicializar el agente: {str(e)}")

    def answer_question(self, question: str) -> str:
        """Interpreta preguntas en lenguaje natural sobre el CSV, la gráfica o stock"""
        try:
            # Primero intentar responder con análisis local
            local_response = self._try_local_answer(question)
            if local_response:
                return local_response
            
            # Si no se puede responder localmente, usar OpenAI
            return self._answer_with_openai(question)
            
        except Exception as e:
            return f"Error al procesar la pregunta: {str(e)}"

    def _try_local_answer(self, question: str) -> str:
        """Intenta responder la pregunta usando análisis local"""
        question_lower = question.lower()
        
        # Saludos y preguntas de bienvenida
        if any(word in question_lower for word in ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'saludos', 'hey']):
            return self._get_greeting_response()
        
        # Preguntas sobre qué puede hacer el agente
        if any(word in question_lower for word in ['qué puedes hacer', 'qué sabes hacer', 'ayúdame', 'ayuda', 'funciones', 'capacidades']):
            return self._get_help_response()
        
        # Preguntas sobre gráficas descriptivas
        if any(word in question_lower for word in ['gráfica', 'gráfico', 'tendencia', 'análisis descriptivo', 'descriptivo']):
            return self._handle_descriptive_questions(question)
        
        # Preguntas sobre stock
        if any(word in question_lower for word in ['stock', 'rotación', 'inventario', 'cantidad', 'existencias']):
            return self.stock_analyzer.answer_stock_question(question)
        
        # Preguntas sobre predicciones/importaciones
        if any(word in question_lower for word in ['predicción', 'predicciones', 'importar', 'próximamente', 'recomendación', 'recomendaciones', 'futuro', 'pronóstico']):
            return self._answer_prediction_question(question)
        
        # Preguntas generales sobre datos
        if any(word in question_lower for word in ['resumen', 'general', 'datos', 'estadísticas', 'overview', 'panorama']):
            return self._get_data_summary()
        
        return None  # No se puede responder localmente

    def _get_greeting_response(self) -> str:
        """Genera una respuesta de saludo personalizada"""
        import datetime
        hour = datetime.datetime.now().hour
        
        if 5 <= hour < 12:
            greeting = "¡Buenos días! 🌅"
        elif 12 <= hour < 18:
            greeting = "¡Buenas tardes! ☀️"
        else:
            greeting = "¡Buenas noches! 🌙"
        
        response = f"{greeting}\n\n"
        response += "Soy tu asistente analítico especializado en datos de importación y stock de American Tactical. "
        response += "Puedo ayudarte con:\n\n"
        response += "📊 **Análisis Descriptivo:**\n"
        response += "• Tendencias de importación\n"
        response += "• Productos más importados\n"
        response += "• Costos logísticos\n"
        response += "• Análisis de rotación\n\n"
        response += "🔮 **Predicciones:**\n"
        response += "• Productos recomendados para importar\n"
        response += "• Cantidades sugeridas\n"
        response += "• Tiempos estimados\n\n"
        response += "📦 **Gestión de Stock:**\n"
        response += "• Productos con baja rotación\n"
        response += "• Stock bajo\n"
        response += "• Resumen de inventario\n\n"
        response += "¿En qué puedo ayudarte hoy?"
        
        return response

    def _get_help_response(self) -> str:
        """Proporciona información sobre las capacidades del agente"""
        response = "🤖 **Mis Capacidades:**\n\n"
        response += "**📊 Análisis Descriptivo:**\n"
        response += "• Pregunta por 'tendencias de importación'\n"
        response += "• Pregunta por 'productos más importados'\n"
        response += "• Pregunta por 'costos logísticos'\n"
        response += "• Pregunta por 'análisis de rotación'\n\n"
        response += "**🔮 Predicciones:**\n"
        response += "• Pregunta por 'predicciones de importación'\n"
        response += "• Pregunta por 'productos recomendados'\n"
        response += "• Pregunta por 'cantidades sugeridas'\n\n"
        response += "**📦 Stock:**\n"
        response += "• Pregunta por 'productos con baja rotación'\n"
        response += "• Pregunta por 'stock bajo'\n"
        response += "• Pregunta por 'resumen de inventario'\n\n"
        response += "**📈 General:**\n"
        response += "• Pregunta por 'resumen general'\n"
        response += "• Pregunta por 'estadísticas'\n\n"
        response += "¡Solo dime qué te interesa saber!"
        
        return response

    def _handle_descriptive_questions(self, question: str) -> str:
        """Maneja preguntas específicas sobre análisis descriptivo"""
        question_lower = question.lower()
        
        # Mapeo de palabras clave a gráficas específicas
        graph_mapping = {
            'tendencia': 'trend_imports',
            'tendencias': 'trend_imports',
            'histórico': 'trend_imports',
            'histórica': 'trend_imports',
            'productos más': 'top_imported_products',
            'top': 'top_imported_products',
            'más importados': 'top_imported_products',
            'costo logístico': 'logistics_cost_trend',
            'costos logísticos': 'logistics_cost_trend',
            'logística': 'logistics_cost_trend',
            'rotación': 'low_rotation_high_margin',
            'margen': 'low_rotation_high_margin',
            'baja rotación': 'low_rotation_high_margin'
        }
        
        # Buscar coincidencias
        for keyword, graph_id in graph_mapping.items():
            if keyword in question_lower:
                return self._summarize_descriptive_graph(graph_id)
        
        # Si no encuentra coincidencia específica, dar un resumen general
        return self._get_descriptive_overview()

    def _get_descriptive_overview(self) -> str:
        """Proporciona un resumen general de los análisis descriptivos disponibles"""
        response = "📊 **Análisis Descriptivo Disponible:**\n\n"
        response += "Tenemos varios análisis que pueden interesarte:\n\n"
        response += "**📈 Tendencias de Importación:**\n"
        response += "Muestra cómo han variado las importaciones a lo largo del tiempo, identificando patrones estacionales y cambios en la demanda.\n\n"
        response += "**🏆 Productos Más Importados:**\n"
        response += "Revela cuáles son los productos con mayor movimiento en el último trimestre, ayudando a enfocar esfuerzos comerciales.\n\n"
        response += "**🚚 Costos Logísticos:**\n"
        response += "Analiza la evolución de los gastos de transporte y logística, clave para la rentabilidad del negocio.\n\n"
        response += "**⚖️ Análisis de Rotación:**\n"
        response += "Identifica productos con baja rotación pero alto margen, oportunidades para estrategias de venta específicas.\n\n"
        response += "¿Cuál de estos análisis te gustaría explorar?"
        
        return response

    def _summarize_descriptive_graph(self, graph_id: str) -> str:
        """Genera un resumen textual detallado de la gráfica descriptiva solicitada."""
        try:
            if graph_id == 'trend_imports':
                response = "📈 **Tendencias Históricas de Importación:**\n\n"
                response += "Este análisis muestra la evolución temporal de las importaciones, permitiendo identificar:\n\n"
                response += "• **Patrones estacionales** - Picos y valles en ciertos periodos del año\n"
                response += "• **Tendencias de crecimiento** - Si las importaciones aumentan o disminuyen\n"
                response += "• **Anomalías** - Periodos con comportamiento inusual\n"
                response += "• **Ciclos de demanda** - Fluctuaciones regulares en el tiempo\n\n"
                response += "💡 **Insight:** Esta información es crucial para planificar futuras importaciones y optimizar la cadena de suministro."
                
            elif graph_id == 'top_imported_products':
                response = "🏆 **Productos Más Importados:**\n\n"
                response += "Este ranking revela los productos con mayor demanda en el último trimestre:\n\n"
                response += "• **Productos estrella** - Los de mayor movimiento\n"
                response += "• **Preferencias del mercado** - Qué productos son más populares\n"
                response += "• **Oportunidades de negocio** - Productos con alta demanda\n"
                response += "• **Estrategias de inventario** - En qué enfocar los esfuerzos\n\n"
                response += "💡 **Insight:** Enfoca tus recursos en estos productos de alto rendimiento para maximizar ventas."
                
            elif graph_id == 'logistics_cost_trend':
                response = "🚚 **Tendencia de Costos Logísticos:**\n\n"
                response += "Este análisis muestra la evolución de los gastos asociados al transporte:\n\n"
                response += "• **Eficiencia logística** - Si los costos están optimizados\n"
                response += "• **Impacto en rentabilidad** - Cómo afectan los costos al margen\n"
                response += "• **Oportunidades de ahorro** - Dónde reducir gastos\n"
                response += "• **Tendencias del mercado** - Cambios en costos de transporte\n\n"
                response += "💡 **Insight:** Optimizar estos costos puede mejorar significativamente la rentabilidad del negocio."
                
            elif graph_id == 'low_rotation_high_margin':
                response = "⚖️ **Análisis de Rotación vs Margen:**\n\n"
                response += "Este análisis identifica productos especiales:\n\n"
                response += "• **Productos premium** - Baja rotación pero alto margen\n"
                response += "• **Oportunidades de promoción** - Productos que pueden venderse más\n"
                response += "• **Estrategias de precios** - Productos con potencial de mayor precio\n"
                response += "• **Diversificación** - Productos nicho con buena rentabilidad\n\n"
                response += "💡 **Insight:** Estos productos son ideales para campañas específicas o estrategias de precios premium."
                
            else:
                response = "❓ No se encontró una gráfica descriptiva específica para tu pregunta.\n\n"
                response += "Puedes preguntar por:\n"
                response += "• Tendencias de importación\n"
                response += "• Productos más importados\n"
                response += "• Costos logísticos\n"
                response += "• Análisis de rotación"
            
            return response
            
        except Exception as e:
            return f"Error al analizar la gráfica descriptiva: {str(e)}"

    def _answer_prediction_question(self, question: str) -> str:
        """Responde preguntas sobre predicciones usando datos locales"""
        try:
            # Usar las columnas correctas del archivo
            top_products = self.df.sort_values(by="cantidad_a_importar", ascending=False).head(5)
            
            response = "🔮 **Predicciones de Importación:**\n\n"
            response += "Basándome en el análisis histórico de ventas y patrones de demanda, aquí están mis recomendaciones:\n\n"
            response += "**🏆 Top 5 productos recomendados para importar:**\n\n"
            
            for i, (_, row) in enumerate(top_products.iterrows(), 1):
                response += f"{i}. **{row['normalized_description']}**\n"
                response += f"   📦 Cantidad sugerida: **{round(row['cantidad_a_importar'], 2)}** unidades\n"
                response += f"   ⏰ Tiempo estimado: **{round(row['dias_hasta_proxima_importacion'], 1)}** días\n"
                response += f"   📊 Prioridad: **Alta**\n\n"
            
            response += "**💡 Insights adicionales:**\n"
            response += "• Estas predicciones se basan en algoritmos de machine learning\n"
            response += "• Consideran patrones históricos de venta y estacionalidad\n"
            response += "• Se actualizan automáticamente con nuevos datos\n"
            response += "• Recomiendo revisar estas predicciones semanalmente\n\n"
            response += "¿Te gustaría que profundice en algún producto específico?"
            
            return response
            
        except Exception as e:
            return f"Error al analizar predicciones: {str(e)}"

    def _get_data_summary(self) -> str:
        """Genera un resumen general de los datos disponibles"""
        try:
            total_products = len(self.df)
            avg_quantity = self.df["cantidad_a_importar"].mean()
            avg_days = self.df["dias_hasta_proxima_importacion"].mean()
            
            response = "📊 **Resumen General de Datos:**\n\n"
            response += "**📈 Estadísticas Principales:**\n"
            response += f"• **Total de productos analizados:** {total_products:,}\n"
            response += f"• **Cantidad promedio a importar:** {avg_quantity:.2f} unidades\n"
            response += f"• **Tiempo promedio estimado:** {avg_days:.1f} días\n\n"
            
            # Agregar estadísticas adicionales
            max_quantity = self.df["cantidad_a_importar"].max()
            min_quantity = self.df["cantidad_a_importar"].min()
            response += "**📊 Rango de Cantidades:**\n"
            response += f"• **Máxima cantidad:** {max_quantity:.2f} unidades\n"
            response += f"• **Mínima cantidad:** {min_quantity:.2f} unidades\n\n"
            
            # Agregar resumen de stock si está disponible
            stock_summary = self.stock_analyzer.get_stock_summary()
            if not stock_summary.startswith("Error"):
                response += "---\n" + stock_summary
            
            response += "\n**🎯 Próximos pasos recomendados:**\n"
            response += "• Revisar las predicciones de importación\n"
            response += "• Analizar las tendencias descriptivas\n"
            response += "• Evaluar el estado del inventario\n"
            response += "• Planificar las próximas importaciones"
            
            return response
            
        except Exception as e:
            return f"Error al generar resumen: {str(e)}"

    def _answer_with_openai(self, question: str) -> str:
        """Responde usando OpenAI como fallback"""
        if not openai_api_key:
            return "Error: No se encontró la clave de API de OpenAI. Verifica la variable de entorno OPENAI_API_KEY."

        try:
            context = self._build_context()

            client = OpenAI(api_key=openai_api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente analítico especializado en datos de importación y stock de American Tactical. Responde en español de manera clara y profesional. Usa emojis para hacer las respuestas más amigables. Proporciona insights útiles y recomendaciones prácticas."},
                    {"role": "user", "content": f"{context}\n\nPregunta: {question}"}
                ],
                temperature=0.3,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error al procesar con OpenAI: {str(e)}"

    def _build_context(self) -> str:
        """Crea contexto para el agente a partir de los datos actuales"""
        try:
            top_products = self.df.sort_values(by="cantidad_a_importar", ascending=False).head(5)
            context_lines = ["📊 **Contexto de Datos Actuales:**\n"]
            context_lines.append("Top 5 productos a importar próximamente:\n")
            for i, (_, row) in enumerate(top_products.iterrows(), 1):
                context_lines.append(
                    f"{i}. {row['normalized_description']} → {round(row['cantidad_a_importar'], 2)} unidades en {round(row['dias_hasta_proxima_importacion'], 1)} días"
                )
            
            # Agregar estadísticas generales
            total_products = len(self.df)
            avg_quantity = self.df["cantidad_a_importar"].mean()
            context_lines.append(f"\n📈 **Estadísticas:** {total_products} productos analizados, promedio de {avg_quantity:.2f} unidades por producto")
            
            return "\n".join(context_lines)
        except Exception as e:
            return f"Error al construir el contexto: {str(e)}"
