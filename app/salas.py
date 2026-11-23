from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.datos import SALAS
from app.esquemas import Sala, SalaActualizar, SalaCrear

router = APIRouter(prefix="/salas", tags=["salas"])

def obtener_sala(codigo: str) -> dict:
    for s in SALAS:
        if s["codigo"] == codigo.upper():
            return s
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe la Sala '{codigo}'",
    )

@router.get("", response_model=list[Sala])
def listar_Salas(
    piso: Annotated[int | None, Query(ge=1, le=5)] = None,
    es_3d: bool = False,
) -> list[dict]:
    resultado = SALAS
    if piso is not None:
        resultado = [p for p in resultado if p["piso"] == piso]
    if es_3d:
        resultado = [s for s in resultado if s["es_3d"]]
    return resultado
