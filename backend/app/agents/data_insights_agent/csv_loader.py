import pandas as pd
import os

DATA_PATH = os.path.join("output", "master_dataset.csv")

class CSVLoader:
    def __init__(self, path: str = DATA_PATH):
        self.path = path
        self.df = self.load_csv()

    def load_csv(self) -> pd.DataFrame:
        try:
            if not os.path.exists(self.path):
                raise FileNotFoundError(f"El archivo CSV no existe en: {self.path}. Ejecuta primero el modelo predictivo para generar los datos.")
            
            df = pd.read_csv(self.path)
            if df.empty:
                raise ValueError("El archivo CSV está vacío.")
                
            df.columns = df.columns.str.strip().str.lower()
            return df
        except FileNotFoundError:
            # Re-lanzar FileNotFoundError para que se maneje apropiadamente
            raise
        except pd.errors.EmptyDataError:
            raise ValueError("El archivo CSV está vacío o malformado.")
        except Exception as e:
            raise RuntimeError(f"Error al cargar el CSV: {e}")

    def get_product_info(self, product_name: str) -> dict:
        try:
            product_name = product_name.strip().lower()
            match = self.df[self.df['descripcion_normalizada'].str.lower() == product_name]

            if match.empty:
                return {"error": f"No se encontraron datos para el producto: {product_name}"}

            return match.iloc[0].to_dict()
        except Exception as e:
            return {"error": f"Error al buscar información del producto: {str(e)}"}

    def summarize_dataset(self) -> str:
        try:
            total_products = len(self.df)
            avg_quantity = self.df["pred_cantidad"].mean()
            avg_days = self.df["pred_dias"].mean()

            return (
                f"El dataset incluye {total_products} productos.\n"
                f"Cantidad promedio a importar: {avg_quantity:.2f} unidades.\n"
                f"Días promedio hasta la próxima importación: {avg_days:.2f} días."
            )
        except Exception as e:
            return f"Error al resumir el dataset: {str(e)}"
