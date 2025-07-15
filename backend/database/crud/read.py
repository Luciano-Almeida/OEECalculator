from datetime import datetime, timedelta
import json
import logging
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from typing import Dict, List, Optional


from database.models import (
    OEESetup, DigestData,
    PlannedDowntimeSetup, UnplannedDowntimeSetup, Paradas,
    PlannedDowntime, UnplannedDowntime, AutoOEE
)

# Logger específico
logger = logging.getLogger(__name__)

# 📌 Função genérica para executar consultas (assíncrona)
async def fetch_all(db: AsyncSession, stmt):
    try:
        result = await db.execute(stmt)  # Execução assíncrona
        return result.scalars().all()  # Obtém todos os resultados
    except SQLAlchemyError as e:
        logger.exception(f"Erro ao buscar registros: {e}")
        raise

async def fetch_one(db: AsyncSession, stmt):
    try:
        result = await db.execute(stmt)  # Execução assíncrona
        return result.scalar_one_or_none()  # Obtém um único registro ou None
    except SQLAlchemyError as e:
        logger.exception(f"Erro ao buscar registro: {e}")
        raise

async def fetch_all_rows(db: AsyncSession, stmt):
    """ Para selects com múltiplas colunas (e.g., JOIN, funções agregadas), 
        use .all() ao invés de .scalars().all().
    """
    try:
        result = await db.execute(stmt)
        return result.all()  # Retorna todas as linhas como tuplas
    except SQLAlchemyError as e:
        logger.exception(f"Erro ao buscar registros: {e}")
        raise


# 📌 Funções de leitura para cada tabela
'''async def get_all_oee_setups(db: AsyncSession) -> List[str]:
    stmt = select(OEESetup)
    #return await fetch_all(db, stmt)
    result = await fetch_all(db, stmt)

    return [json.dumps({
        "id": oee_setup.id,
        "user": oee_setup.user,
        "start_shift": oee_setup.start_shift.isoformat() if oee_setup.start_shift else None,  # Convert to string,
        "stop_shift": oee_setup.stop_shift.isoformat() if oee_setup.stop_shift else None,  # Convert to string,
        "stop_time": oee_setup.stop_time,
        "digest_time": oee_setup.digest_time,
        "line_speed": oee_setup.line_speed,
        "camera_name_id": oee_setup.camera_name_id,
        "timestamp": oee_setup.timestamp.isoformat() if oee_setup.timestamp else None,  # Convert to string,
    }) for oee_setup in result]
'''
async def get_all_oee_setups(db: AsyncSession) -> List[OEESetup]:
    stmt = select(OEESetup).order_by(OEESetup.id)  # Seleciona todos os registros da tabela OEESetup
    return await fetch_all(db, stmt)  # Usa a função genérica para buscar todos

async def get_all_digest_data(db: AsyncSession) -> List[DigestData]: #List[str]:
    stmt = select(DigestData).order_by(DigestData.id)
    result = await fetch_all(db, stmt)
    return result # retorna lista de objetos ORM diretamente
    '''return [json.dumps({
        "id": row.id,
        "ok": row.ok,
        "nok": row.nok,
        "lote_id": row.lote_id,
        "camera_id": row.camera_name_id,
        "start_digest": row.start_digest.isoformat() if row.start_digest else None,      # Convert to string,
        "stop_digest": row.stop_digest.isoformat() if row.stop_digest else None,      # Convert to string,
        #"timestamp": row.timestamp.isoformat() if row.timestamp else None,      # Convert to string        
    }) for row in result]'''

async def get_all_planned_downtime_setups(db: AsyncSession) -> List[PlannedDowntimeSetup]:
    stmt = select(PlannedDowntimeSetup).order_by(PlannedDowntimeSetup.id)
    result = await fetch_all(db, stmt)
    return result # retorna lista de objetos ORM diretamente
    '''return [json.dumps({
        "id": planned_downtime_setup.id,
        "name": planned_downtime_setup.name,
        "start_time": planned_downtime_setup.start_time.strftime("%H:%M") if planned_downtime_setup.start_time else None,
        "stop_time": planned_downtime_setup.stop_time.strftime("%H:%M") if planned_downtime_setup.stop_time else None,
        "camera_name_id": planned_downtime_setup.camera_name_id,
    }) for planned_downtime_setup in result]'''

async def get_all_unplanned_downtime_setups(db: AsyncSession) -> List[UnplannedDowntimeSetup]:
    stmt = select(UnplannedDowntimeSetup).order_by(UnplannedDowntimeSetup.id)
    result = await fetch_all(db, stmt)
    return result
    '''return [json.dumps({
        "id": unplanned_downtime_setup.id,
        "name": unplanned_downtime_setup.name,
    }) for unplanned_downtime_setup in result]'''

async def get_all_paradas(db: AsyncSession) -> List[Paradas]:
    stmt = select(Paradas).order_by(Paradas.id)
    result = await fetch_all(db, stmt)
    return result  # retorna lista de objetos ORM diretamente

async def get_all_planned_downtime(db: AsyncSession) -> List[PlannedDowntime]:
    stmt = select(PlannedDowntime).order_by(PlannedDowntime.id)
    return await fetch_all(db, stmt)

async def get_all_unplanned_downtime(db: AsyncSession) -> List[UnplannedDowntime]:
    stmt = select(UnplannedDowntime).order_by(UnplannedDowntime.id)
    return await fetch_all(db, stmt)

async def get_all_auto_oee(db: AsyncSession) -> List[AutoOEE]:
    stmt = select(AutoOEE).order_by(AutoOEE.id)
    return await fetch_all(db, stmt)

# 📌 Funções para buscar um único registro por ID
async def get_oee_setup_by_id(db: AsyncSession, oee_id: int) -> Optional[OEESetup]:
    stmt = select(OEESetup).where(OEESetup.id == oee_id)
    return await fetch_one(db, stmt)

async def get_digest_data_by_id(db: AsyncSession, digest_id: int) -> Optional[DigestData]:
    stmt = select(DigestData).where(DigestData.id == digest_id)
    return await fetch_one(db, stmt)

async def get_planned_downtime_setup_by_id(db: AsyncSession, planned_id: int) -> Optional[PlannedDowntimeSetup]:
    stmt = select(PlannedDowntimeSetup).where(PlannedDowntimeSetup.id == planned_id)
    return await fetch_one(db, stmt)

async def get_unplanned_downtime_setup_by_id(db: AsyncSession, unplanned_id: int) -> Optional[UnplannedDowntimeSetup]:
    stmt = select(UnplannedDowntimeSetup).where(UnplannedDowntimeSetup.id == unplanned_id)
    return await fetch_one(db, stmt)

async def get_parada_by_id(db: AsyncSession, parada_id: int) -> Optional[Paradas]:
    stmt = select(Paradas).where(Paradas.id == parada_id)
    return await fetch_one(db, stmt)

async def get_planned_downtime_by_id(db: AsyncSession, planned_id: int) -> Optional[PlannedDowntime]:
    stmt = select(PlannedDowntime).where(PlannedDowntime.id == planned_id)
    return await fetch_one(db, stmt)

async def get_unplanned_downtime_by_id(db: AsyncSession, unplanned_id: int) -> Optional[UnplannedDowntime]:
    stmt = select(UnplannedDowntime).where(UnplannedDowntime.id == unplanned_id)
    return await fetch_one(db, stmt)

async def get_auto_oee_by_id(db: AsyncSession, oee_id: int) -> Optional[AutoOEE]:
    stmt = select(AutoOEE).where(AutoOEE.id == oee_id)
    return await fetch_one(db, stmt)


# 📌 Funções para buscar registros por CAMERA_NAME_ID
async def get_digest_data_by_camera_name_id(db: AsyncSession, camera_name_id: int) -> List[DigestData]:
    stmt = select(DigestData).where(DigestData.camera_name_id == camera_name_id).order_by(DigestData.id)
    return await fetch_all(db, stmt)

async def get_oee_setup_by_camera_name_id(db: AsyncSession, camera_name_id: int) -> Optional[OEESetup]:
    stmt = select(OEESetup).where(OEESetup.camera_name_id == camera_name_id)
    return await fetch_one(db, stmt)
    '''result = await fetch_all(db, stmt)

    # Caso não haja resultados, retornamos uma resposta vazia
    if result is None:
        return {"message": "Nenhum resultado encontrado"}
    
    result = result[0]  
    
    # Caso haja, retornamos os dados no formato JSON
    oee_setup_dict = {
        "id": result.id,
        "user": result.user,
        "start_shift": result.start_shift.isoformat() if result.start_shift else None,
        "stop_shift": result.stop_shift.isoformat() if result.stop_shift else None,
        "stop_time": result.stop_time,
        "line_speed": result.line_speed,  # (valor em pç/min)
        "digest_time": result.digest_time,
        "camera_name_id": result.camera_name_id,
        "timestamp": result.timestamp.isoformat() if result.timestamp else None,
    }

    return oee_setup_dict'''

async def get_planned_downtime_setup_by_camera_name_id(db: AsyncSession, camera_name_id: int) -> List[PlannedDowntimeSetup]:
    stmt = select(PlannedDowntimeSetup).where(PlannedDowntimeSetup.camera_name_id == camera_name_id)
    return await fetch_all(db, stmt)

async def get_last_digest_data_by_camera(db: AsyncSession, camera_name_id: int) -> Optional[DigestData]:
    # Último DigestData para uma câmera específica
    stmt = (
        select(DigestData)
        .where(DigestData.camera_name_id == camera_name_id)
        .order_by(desc(DigestData.stop_digest))  # Assumindo que o mais recente é pelo fim da digestão
        .limit(1)
    )
    return await fetch_one(db, stmt)

async def get_last_parada_by_camera(db: AsyncSession, camera_name_id: int) -> Optional[Paradas]:
    # Última Parada para uma câmera específica
    stmt = (
        select(Paradas)
        .where(Paradas.camera_name_id == camera_name_id)
        .order_by(desc(Paradas.stop))  # Parada mais recente pelo tempo de parada final
        .limit(1)
    )
    return await fetch_one(db, stmt)

async def get_last_auto_oee_by_camera(db: AsyncSession, camera_name_id: int) -> Optional[AutoOEE]:
    # Último AutoOEE para uma câmera específica
    stmt = (
        select(AutoOEE)
        .where(AutoOEE.camera_name_id == camera_name_id)
        .order_by(desc(AutoOEE.end))  # Registro mais recente pelo end (final do periodo de análise)
        .limit(1)
    )
    return await fetch_one(db, stmt)



