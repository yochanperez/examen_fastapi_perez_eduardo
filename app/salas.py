from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.datos import SALAS
from app.esquemas import Sala, SalaActualizar, SalaCrear

router = APIRouter(prefix="/salas", tags=["salas"])