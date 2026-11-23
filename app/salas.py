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

@router.post("", response_model=Sala, status_code=status.HTTP_201_CREATED)
def crear_sala(nueva: SalaCrear) -> dict:
    if any(s["codigo"] == nueva.codigo for s in SALAS):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La Sala '{nueva.codigo}' ya existe",
        )
    SALAS.append(nueva.model_dump())
    return SALAS[-1]


@router.get("/{codigo}", response_model=Sala)
def ver_sala(sala: MateriaEncontrada) -> dict:
    return sala


@router.put("/{codigo}", response_model=Materia)
def actualizar_materia(cambios: MateriaActualizar, materia: MateriaEncontrada) -> dict:
    materia.update(cambios.model_dump(exclude_unset=True))
    return materia


@router.delete("/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_materia(materia: MateriaEncontrada) -> None:
    MATERIAS.remove(materia)