# routers/status
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional

from database.db import get_db
import schemas as schemas
from utils import obter_status_do_setup

import random

router = APIRouter()

# Status de Inicialização dos Setups
@router.get("/get_setup_status_ok/", response_model=Dict)
async def get_setup_status_ok(
    db: AsyncSession = Depends(get_db),
):
    """
    Retorna status do setup OEE, caso setup esteja preenchido com algum dado retorna verdadeiro
    """
    # Sorteando entre True e False para testes
    '''resultado = random.choices([False, True], weights=[85, 15])[0]
    cameras_faltando_setup = [1,2,3,4]#[random.choice([1,2,3,4])]
    return {
                "oee_ready": resultado,
                "cameras_faltando_setup": cameras_faltando_setup
            }'''
    return await obter_status_do_setup(db)

