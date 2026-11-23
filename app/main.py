from fastapi import FastAPI
from app.salas import router as salas_router

app = FastAPI(title="API de Materias", version="1.0.0")