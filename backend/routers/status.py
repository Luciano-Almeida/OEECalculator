# routers/status
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional

from database.db import get_db
from database.db.conexao_db_externo import get_external_db
import services
import schemas as schemas
from utils import obter_status_do_setup

import random

router = APIRouter()

# Modelo de resposta
class CameraDisponivel(BaseModel):
    id: int
    nome: str

# Status de Inicialização dos Setups
@router.get("/get_setup_status_ok/", response_model=Dict)
async def get_setup_status_ok(
    db: AsyncSession = Depends(get_db),
    external_db: AsyncSession = Depends(get_external_db)
):
    """
    Retorna status do setup OEE, caso setup esteja preenchido com algum dado retorna verdadeiro
    """
    cameras_disponiveis = await services.fetch_enderecos_camera(
        external_db, nome_inicial="Câmera"
    )

    ids_cameras = [item["id"] for item in cameras_disponiveis]

    return await obter_status_do_setup(db, lista_de_cameras=ids_cameras)


@router.get("/get_cameras_disponiveis/", response_model=List[CameraDisponivel])
async def get_cameras_disponiveis(
    external_db: AsyncSession = Depends(get_external_db)
):
    cameras_disponiveis = await services.fetch_enderecos_camera(
        external_db, nome_inicial="Câmera"
    )

    return cameras_disponiveis