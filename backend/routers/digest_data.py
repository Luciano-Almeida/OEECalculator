from datetime import datetime
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from services import servico_data_received
from database.db import get_db
import database.crud as crud
import schemas as schemas

from database.crud import create_parada

from services.servico_data_received import fetch_digest_data_from_datareceived, fetch_all_digest_data_from_datareceived, get_last_timestamp_from_dataReceived_by_camera_id
from database.db.conexao_db_externo import get_external_db

# Logger específico
logger = logging.getLogger(__name__)

router = APIRouter()

# 📌 GET
@router.get("/digest/", response_model=List[schemas.DigestDataSchema])
async def get_digest(db: AsyncSession = Depends(get_db)):
    """
    Retorna uma lista com todas os dados
    """
    return await crud.get_all_digest_data(db)

@router.get("/digest_filtered_by_period/", response_model=List[schemas.DigestDataSchema])
async def get_digest_filtered_by_period(
    inicio: datetime, 
    fim: datetime, 
    camera_name_id: int, 
    db: AsyncSession = Depends(get_db)
    ):
    """
    Retorna uma lista com todas os dados
    """
    return await crud.get_digest_data_filtered_by_period_and_cameraId(db, inicio, fim, camera_name_id)

@router.get("/teste_fetch_digest/")
async def teste_fetch_digest(
    inicio: datetime, 
    fim: datetime, 
    camera_name_id: int, 
    digest_time: int=120,
    db_external: AsyncSession = Depends(get_external_db)
    ):
    resultados = await fetch_digest_data_from_datareceived(
                db=db_external, 
                CAMERA_NAME_ID=camera_name_id,
                DIGEST_TIME=digest_time, 
                START_ANALISE=inicio, # datetime "'2025-06-09 10:00:43'",
                STOP_ANALISE=fim
                )
    return {'resultados': resultados}

# 📌 POST
@router.post("/create_digest/")
async def create_digest_endpoint(db: AsyncSession = Depends(get_db)):
    # SetupOEE
    camera_name_id = 1 # setup_oee["camera_name_id"]
    digest_time = 60 # setup_oee["digest_time"]
    resultados = servico_data_received.fetch_digest_data_from_datareceived(camera_name_id, digest_time)

    for row in resultados:
        # Extrair valores de cada linha de resultado
        lote_id = row[0][0]  # row["LoteId"]  # Ajuste conforme o formato do seu resultado
        camera_name_id = row[0][1]  # row["CameraId"]  # Ajuste conforme o formato do seu resultado
        ok = row[0][2]  # row["total_ok"]
        nok = row[0][3]  # row["total_nok"]
        # Convertendo start_digest e stop_digest para datetime
        start_digest = datetime.strptime(row[1], "'%Y-%m-%d %H:%M:%S'")  # Format according to the string format
        stop_digest = datetime.strptime(row[2], "'%Y-%m-%d %H:%M:%S'")  # Same as above
        
        # Chamar a função para criar o registro na tabela DigestData
        await crud.create_digest_data(db=db, ok=ok, nok=nok, lote_id=lote_id, camera_name_id=camera_name_id,
                                      start_digest=start_digest, stop_digest=stop_digest)

    return "Data processed and stored successfully."


# 📌 DELETE


# 📌 UPDATE