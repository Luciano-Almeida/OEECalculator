from datetime import datetime, time, timedelta
import random
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, validator
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional

from database.db import get_db
import database.crud as crud
from utils import timedelta_to_iso

from database.crud import create_parada
import schemas as schemas

# Importando as classes do SQLAlchemy
from database.models import OEESetup, PlannedDowntime, UnplannedDowntime, Paradas, AutoOEE, PlannedDowntimeSetup

from services.servico_data_received import fetch_paradas, fetch_paradas_after_init_date
from database.db.conexao_db_externo import get_external_db

router = APIRouter()


@router.get("/paradas_direto_do_data_received")
async def get_paradas(
    init_date: datetime,
    parada_time_stop: int,
    db_external: AsyncSession = Depends(get_external_db)
):
    """
    Rota para buscar paradas após uma data inicial com base em um tempo de parada mínimo.
    """
    paradas = await fetch_paradas_after_init_date(
        db=db_external,
        INIT=init_date,
        PARADA_TIME_STOP=parada_time_stop
    )
    '''
    paradas = await fetch_paradas(
        db=db_external,
        PARADA_TIME_STOP=parada_time_stop
    )'''

    # Convertendo para formato JSON-serializável
    return [
    {
        "startTime": row[0].isoformat() if row[0] else None,
        "stopTime": row[1].isoformat() if row[1] else None,
        "camera_name_id": row[2],
        "intervalo": row[3]
    }
    for row in paradas
]
