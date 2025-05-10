from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from database.db import get_db
import database.crud as crud
from utils import timedelta_to_iso
from services import oee_by_period

# Importando as classes do SQLAlchemy
from database.models import OEESetup, PlannedDowntime, UnplannedDowntime, Paradas, AutoOEE, PlannedDowntimeSetup

router = APIRouter()
 
@router.get("/oee/", response_model=Dict)
async def get_oee(inicio: datetime, fim: datetime, camera_name_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retorna uma lista com todas os dados do OEE e do historico de produção discretizado por um periodo
    """
    # Consultar os dados necessários para o cálculo
    # 1. Dados de setup e produção da câmera
    oee_setup = await crud.get_oee_setup_by_camera_name_id(db=db, camera_name_id=camera_name_id)
    
    if not oee_setup:
        raise HTTPException(status_code=404, detail="No valid OEE setup found for the given camera and time range.")

    oee_data = await oee_by_period(inicio, fim, camera_name_id, oee_setup.line_speed, db)

    discretized_history = await crud.get_total_ok_nok_discretized_by_period(
        db=db,
        inicio=inicio,
        fim=fim,
        camera_name_id=camera_name_id,
        period=timedelta(minutes=1)
    )

    oee_data["discretizado"] = discretized_history
    print(f"oerr_data", oee_data)
    return oee_data