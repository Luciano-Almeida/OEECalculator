from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from database.db import get_db
import database.crud as crud
from utils import timedelta_to_iso
from services import oee_by_period
import schemas as schemas

# Importando as classes do SQLAlchemy
from database.models import OEESetup, PlannedDowntime, UnplannedDowntime, Paradas, AutoOEE, PlannedDowntimeSetup

router = APIRouter()
 
@router.get("/auto_oee/", response_model=List[schemas.AutoOEESchema])
async def get_auto_oee(
    inicio: datetime, 
    fim: datetime, 
    camera_name_id: int, 
    db: AsyncSession = Depends(get_db)
) -> List[schemas.AutoOEESchema]:
    """
    Retorna uma lista com os registros de AutoOEE para o período de tempo e para uma câmera específica.

    - **inicio**: Data e hora de início para o filtro de OEE.
    - **fim**: Data e hora de fim para o filtro de OEE.
    - **camera_name_id**: ID da câmera.
    """
    print(f"Auto OEE init {inicio}, fim {fim}, camera {camera_name_id}")
    
    oees = await crud.get_auto_oee_by_period_and_camera(
        db=db, inicio_pesquisa=inicio, 
        fim_pesquisa=fim,
        camera_name_id=camera_name_id
    )
    return oees
