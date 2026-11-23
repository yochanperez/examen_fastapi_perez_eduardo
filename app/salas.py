from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.datos import SALAS
from app.esquemas import SalaActualizar, SalaCrear, SalaSalida

router = APIRouter(prefix="/salas", tags=["Salas de Cine"])


def buscar_sala_por_codigo(codigo: str) -> dict:
    codigo = codigo.upper()
    for s in SALAS:
        if s["codigo"] == codigo:
            return s
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe la Sala '{codigo}'",
    )


SalaDep = Annotated[dict, Depends(buscar_sala_por_codigo)]


@router.get("/aforo-jornada", status_code=status.HTTP_200_OK)
def calcular_aforo_jornada(
    funciones: Annotated[int, Query(ge=1, le=12)],
    piso: Annotated[int | None, Query(ge=1, le=5)] = None,
):
    seleccion = [s for s in SALAS if piso is None or s["piso"] == piso]

    if not seleccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay salas registradas para los criterios seleccionados",
        )

    cantidad_salas = len(seleccion)
    suma_butacas = 0
    suma_vendible_por_funcion = 0
    cantidad_3d = 0

    for sala in seleccion:
        butacas = sala["butacas"]
        suma_butacas += butacas
        suma_vendible_por_funcion += int(butacas * 0.90)
        if sala["es_3d"]:
            cantidad_3d += 1

    return {
        "salas": cantidad_salas,
        "funciones": funciones,
        "butacas_promedio": round(suma_butacas / cantidad_salas, 2),
        "aforo_total": suma_butacas * funciones,
        "aforo_vendible": suma_vendible_por_funcion * funciones,
        "porcentaje_3d": round((cantidad_3d / cantidad_salas) * 100, 1),
    }


@router.get("/estado-mantenimiento", status_code=status.HTTP_200_OK)
def reporte_mantenimiento(
    en_mantenimiento: Annotated[
        list[str] | None,
        Query(description="Códigos de salas fuera de servicio (repetible)"),
    ] = None,
):
    if not SALAS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existen salas registradas en el sistema",
        )

    codigos_mantenimiento = {cod.upper() for cod in en_mantenimiento} if en_mantenimiento else set()

    total = 0
    conteo_mantenimiento = 0
    operativas = 0
    aforo_operativo = 0
    max_butacas = -1
    sala_operativa_mayor: str | None = None

    for sala in SALAS:
        total += 1
        if sala["codigo"] in codigos_mantenimiento:
            conteo_mantenimiento += 1
        else:
            operativas += 1
            aforo_operativo += sala["butacas"]
            if sala["butacas"] > max_butacas:
                max_butacas = sala["butacas"]
                sala_operativa_mayor = sala["codigo"]

    return {
        "total": total,
        "en_mantenimiento": conteo_mantenimiento,
        "operativas": operativas,
        "porcentaje_fuera_de_servicio": round((conteo_mantenimiento / total) * 100, 1),
        "aforo_operativo": aforo_operativo,
        "sala_operativa_mayor": sala_operativa_mayor,
    }


@router.get("", response_model=list[SalaSalida], status_code=status.HTTP_200_OK)
def listar_salas(
    piso: Annotated[int | None, Query(ge=1, le=5)] = None,
    es_3d: bool = False,
) -> list[dict]:
    resultado = SALAS
    if piso is not None:
        resultado = [p for p in resultado if p["piso"] == piso]
    if es_3d:
        resultado = [s for s in resultado if s["es_3d"]]
    return resultado


@router.post("", response_model=SalaSalida, status_code=status.HTTP_201_CREATED)
def crear_sala(nueva: SalaCrear):
    for s in SALAS:
        if s["codigo"] == nueva.codigo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La Sala '{nueva.codigo}' ya existe",
            )
    registro = nueva.model_dump()
    SALAS.append(registro)
    return registro


@router.get("/{codigo}", response_model=SalaSalida, status_code=status.HTTP_200_OK)
def obtener_sala(sala: SalaDep):
    return sala


@router.patch("/{codigo}", response_model=SalaSalida, status_code=status.HTTP_200_OK)
def actualizar_sala(sala: SalaDep, datos: SalaActualizar):
    cambios = datos.model_dump(exclude_unset=True)
    sala.update(cambios)
    return sala


@router.delete("/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_sala(sala: SalaDep):
    SALAS.remove(sala)