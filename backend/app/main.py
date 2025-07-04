from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router

app = FastAPI(title="American Tactical API")

# Habilitar CORS (para permitir peticiones desde el frontend o Postman)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción limita esto a tu dominio frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los endpoints definidos en routes.py
app.include_router(api_router)
