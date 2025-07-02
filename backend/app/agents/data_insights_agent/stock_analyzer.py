import pandas as pd
import os
from typing import Dict, List, Any

class StockAnalyzer:
    def __init__(self):
        self.stock_data = None
        self.sales_data = None
        self.load_data()
    
    def load_data(self):
        """Carga los datos de stock y ventas"""
        try:
            stock_path = os.path.join("output", "processed_stock.csv")
            sales_path = os.path.join("output", "processed_sales.csv")
            
            if os.path.exists(stock_path):
                self.stock_data = pd.read_csv(stock_path)
                self.stock_data.columns = self.stock_data.columns.str.strip().str.lower()
            
            if os.path.exists(sales_path):
                self.sales_data = pd.read_csv(sales_path)
                self.sales_data.columns = self.sales_data.columns.str.strip().str.lower()
                
        except Exception as e:
            print(f"Error cargando datos: {e}")
    
    def analyze_low_rotation_products(self) -> Dict[str, Any]:
        """Analiza productos con baja rotación de stock"""
        if self.stock_data is None:
            return {"error": "No hay datos de stock disponibles"}
        
        try:
            # Calcular días promedio de stock (si existe la columna)
            if 'coverage_days' in self.stock_data.columns:
                # Productos con más de 30 días de stock (baja rotación)
                low_rotation = self.stock_data[self.stock_data['coverage_days'] > 30].copy()
                low_rotation = low_rotation.sort_values('coverage_days', ascending=False)
                
                return {
                    "total_low_rotation": len(low_rotation),
                    "products": low_rotation.head(10)[['normalized_description', 'coverage_days', 'existencias']].to_dict('records'),
                    "avg_days": low_rotation['coverage_days'].mean() if len(low_rotation) > 0 else 0
                }
            else:
                # Si no hay columna de días, usar cantidad como proxy
                high_stock = self.stock_data.sort_values('existencias', ascending=False).head(10)
                return {
                    "total_high_stock": len(high_stock),
                    "products": high_stock[['normalized_description', 'existencias']].to_dict('records'),
                    "message": "Analizando por cantidad de stock (no hay datos de días)"
                }
                
        except Exception as e:
            return {"error": f"Error analizando rotación: {str(e)}"}
    
    def analyze_stock_levels(self) -> Dict[str, Any]:
        """Analiza niveles generales de stock"""
        if self.stock_data is None:
            return {"error": "No hay datos de stock disponibles"}
        
        try:
            total_products = len(self.stock_data)
            total_stock = self.stock_data['existencias'].sum() if 'existencias' in self.stock_data.columns else 0
            avg_stock = self.stock_data['existencias'].mean() if 'existencias' in self.stock_data.columns else 0
            
            # Productos con stock bajo (menos de 10 unidades)
            low_stock = self.stock_data[self.stock_data['existencias'] < 10] if 'existencias' in self.stock_data.columns else pd.DataFrame()
            
            return {
                "total_products": total_products,
                "total_stock": total_stock,
                "average_stock": round(avg_stock, 2),
                "low_stock_products": len(low_stock),
                "low_stock_list": low_stock[['normalized_description', 'existencias']].to_dict('records') if len(low_stock) > 0 else []
            }
            
        except Exception as e:
            return {"error": f"Error analizando niveles de stock: {str(e)}"}
    
    def get_stock_summary(self) -> str:
        """Genera un resumen general del stock"""
        levels = self.analyze_stock_levels()
        rotation = self.analyze_low_rotation_products()
        
        if "error" in levels:
            return f"Error: {levels['error']}"
        
        summary = f"📊 **Resumen de Stock:**\n"
        summary += f"• Total de productos: {levels['total_products']}\n"
        summary += f"• Stock total: {levels['total_stock']} unidades\n"
        summary += f"• Promedio por producto: {levels['average_stock']} unidades\n"
        summary += f"• Productos con stock bajo (<10): {levels['low_stock_products']}\n"
        
        if "total_low_rotation" in rotation:
            summary += f"• Productos con baja rotación (>30 días): {rotation['total_low_rotation']}\n"
        
        return summary
    
    def answer_stock_question(self, question: str) -> str:
        """Responde preguntas específicas sobre stock"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['baja rotación', 'rotación baja', 'lenta rotación']):
            rotation = self.analyze_low_rotation_products()
            if "error" in rotation:
                return f"❌ {rotation['error']}"
            
            response = "🔄 **Productos con Baja Rotación de Stock:**\n\n"
            if "total_low_rotation" in rotation:
                response += f"Se encontraron **{rotation['total_low_rotation']}** productos con baja rotación (más de 30 días de stock).\n\n"
                response += "**Top 5 productos con menor rotación:**\n"
                for i, product in enumerate(rotation['products'][:5], 1):
                    response += f"{i}. {product['normalized_description']} - {product['coverage_days']} días de stock\n"
            else:
                response += f"Se encontraron **{rotation['total_high_stock']}** productos con alto stock.\n\n"
                response += "**Top 5 productos con mayor stock:**\n"
                for i, product in enumerate(rotation['products'][:5], 1):
                    response += f"{i}. {product['normalized_description']} - {product['existencias']} unidades\n"
            
            return response
        
        elif any(word in question_lower for word in ['stock bajo', 'poco stock', 'agotándose']):
            levels = self.analyze_stock_levels()
            if "error" in levels:
                return f"❌ {levels['error']}"
            
            response = "⚠️ **Productos con Stock Bajo:**\n\n"
            response += f"Se encontraron **{levels['low_stock_products']}** productos con menos de 10 unidades.\n\n"
            
            if levels['low_stock_list']:
                response += "**Productos que requieren atención:**\n"
                for i, product in enumerate(levels['low_stock_list'][:10], 1):
                    response += f"{i}. {product['normalized_description']} - {product['existencias']} unidades\n"
            else:
                response += "✅ No hay productos con stock críticamente bajo."
            
            return response
        
        elif any(word in question_lower for word in ['resumen', 'general', 'overview']):
            return self.get_stock_summary()
        
        else:
            return "🤔 No entiendo la pregunta. Puedo ayudarte con:\n• Productos con baja rotación\n• Productos con stock bajo\n• Resumen general de stock" 