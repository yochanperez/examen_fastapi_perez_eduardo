from fastapi import FastAPI
from app.salas import router as salas_router

app = FastAPI(title="API de Salas", version="1.0.0")

