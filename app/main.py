from fastapi import FastAPI
from app.salas import router as salas_router

app = FastAPI(title="API de Salas", version="1.0.0")
app.include_router(salas_router)

@app.get("/")
def raiz() -> dict:
    return {"api": "materias", "docs": "/docs"}
