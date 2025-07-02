from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import shutil
import os
from typing import List
from app.pipelines.merge_files import merge_excel_files
import tempfile
from app.pipelines.process_imports import process_imports
from app.pipelines.process_stock import process_stock
from app.models.predictor import run_model
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.data_insights_agent.agent import PredictiveAgent
from app.agents.data_insights_agent.graph_loader import GraphLoader
from app.models import descriptive_analysis



router = APIRouter()

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_agent():
    """Crea una instancia del agente bajo demanda"""
    try:
        return PredictiveAgent()
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al cargar el agente: {str(e)}. Asegúrate de que los archivos de datos existan."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error inesperado al cargar el agente: {str(e)}"
        )

@router.get("/")
def read_root():
    return {"message": "¡Bienvenido a la API de American Tactical!"}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return JSONResponse(content={"message": f"{file.filename} cargado exitosamente."})

@router.post("/merge-excel/")
async def merge_excel(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        return {"error": "At least 2 Excel files are required to merge."}

    temp_paths = []
    original_names = []

    try:
        for file in files:
            suffix = os.path.splitext(file.filename)[1]
            name_no_ext = os.path.splitext(file.filename)[0]
            original_names.append(name_no_ext)

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_file.write(await file.read())
            temp_file.close()
            temp_paths.append(temp_file.name)

        short_name = "_and_".join(original_names[:2])[:50]
        output_filename = f"merged_{short_name}.csv"
        output_path = os.path.join("output", output_filename)
        os.makedirs("output", exist_ok=True)

        # Aquí sí se llama correctamente la función de procesamiento
        merged_file = merge_excel_files(temp_paths, output_path)

        return JSONResponse(content={
            "message": "Files merged successfully.",
            "merged_file_name": output_filename,
            "path": merged_file
        })

    except Exception as e:
        return {"error": str(e)}
    finally:
        for path in temp_paths:
            os.unlink(path)

@router.get("/process-imports/")
def run_process_imports():
    try:
        output_file = process_imports()
        return {
            "message": "Imports processed successfully.",
            "output_file": output_file
        }
    except Exception as e:
        return {"error": str(e)}
    
from app.pipelines.process_sales import process_sales

@router.get("/process-sales/")
def run_process_sales():
    try:
        output_file = process_sales()
        return {
            "message": "Sales processed successfully.",
            "output_file": output_file
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/process-stock/")
def run_process_stock():
    try:
        output_file = process_stock()
        return {
            "message": "Stock processed successfully.",
            "output_file": output_file
        }
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/run-model/")
def run_forecasting_model():
    try:
        result = run_model()
        return {
            "message": "Model executed successfully.",
            "mae": result["mae"],
            "rmse": result["rmse"],
            "csv_file": result["csv"],
            "plot_image": result["image"]
        }
    except Exception as e:
        return {"error": str(e)}
    
# Clase para recibir la pregunta en el body del request
class QuestionRequest(BaseModel):
    question: str

@router.post("/agent/ask")
def ask_agent(request: QuestionRequest):
    try:
        # Crear el agente bajo demanda
        agent = get_agent()
        response = agent.answer_question(request.question)
        return {"answer": response}
    except HTTPException:
        # Re-lanzar HTTPExceptions para mantener el status code correcto
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la pregunta: {str(e)}")

@router.get("/graph")
def get_prediction_graph():
    """Obtiene la gráfica de predicciones en formato base64"""
    try:
        graph_loader = GraphLoader()
        base64_data_url = graph_loader.get_base64_data_url()
        
        if base64_data_url.startswith("Error"):
            raise HTTPException(status_code=404, detail="Gráfica no encontrada. Ejecuta primero el modelo predictivo.")
        
        return {"graph_data_url": base64_data_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la gráfica: {str(e)}")

@router.get("/descriptive/graphs")
def get_descriptive_graphs():
    """Devuelve el catálogo de gráficas descriptivas disponibles."""
    return descriptive_analysis.get_descriptive_graphs_catalog()

@router.get("/descriptive/graph/{graph_id}")
def get_descriptive_graph(graph_id: str):
    """Devuelve la imagen base64 de la gráfica descriptiva solicitada."""
    try:
        graph_base64 = descriptive_analysis.get_graph_by_id(graph_id)
        return {"graph_id": graph_id, "image_base64": graph_base64}
    except Exception as e:
        return {"error": str(e)}

@router.get("/descriptive/run-analysis")
def run_descriptive_analysis():
    """Ejecuta el análisis descriptivo completo y genera todas las gráficas."""
    try:
        # Generar todas las gráficas del catálogo
        graphs_generated = []
        for graph in descriptive_analysis.get_descriptive_graphs_catalog():
            try:
                graph_base64 = descriptive_analysis.get_graph_by_id(graph['id'])
                graphs_generated.append({
                    "id": graph['id'],
                    "name": graph['name'],
                    "status": "success"
                })
            except Exception as e:
                graphs_generated.append({
                    "id": graph['id'],
                    "name": graph['name'],
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "message": "Análisis descriptivo ejecutado",
            "graphs_generated": graphs_generated
        }
    except Exception as e:
        return {"error": str(e)}