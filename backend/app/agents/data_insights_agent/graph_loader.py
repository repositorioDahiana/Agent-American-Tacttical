import base64
import os

GRAPH_PATH = os.path.join("output", "prediction_plot.png")

class GraphLoader:
    def __init__(self, path: str = GRAPH_PATH):
        self.path = path

    def get_base64_graph(self) -> str:
        """Convierte la gráfica PNG a string base64"""
        try:
            if not os.path.exists(self.path):
                raise FileNotFoundError(f"La imagen de predicción no existe en: {self.path}. Ejecuta primero el modelo predictivo para generar la gráfica.")
            
            with open(self.path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except FileNotFoundError:
            # Re-lanzar FileNotFoundError para que se maneje apropiadamente
            raise
        except Exception as e:
            raise RuntimeError(f"Error al cargar la imagen: {e}")

    def get_base64_data_url(self) -> str:
        """Devuelve una data URL útil para mostrar en el frontend"""
        try:
            base64_img = self.get_base64_graph()
            return f"data:image/png;base64,{base64_img}"
        except Exception as e:
            # Si no se puede cargar la imagen, devolver un mensaje de error
            return f"Error al cargar la imagen: {str(e)}"
