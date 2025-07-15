import logging
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any

from database.models import (
    OEESetup, DigestData,
    PlannedDowntimeSetup, UnplannedDowntimeSetup, Paradas,
    PlannedDowntime, UnplannedDowntime, AutoOEE
)
import schemas as schemas

# Logger específico
logger = logging.getLogger(__name__)

# 📌 Função genérica para atualizar qualquer modelo
async def update_record(
    db: AsyncSession,
    model,
    record_id: int,
    update_data: Dict[str, Any]
) -> Dict[str, Any]:
    try:
        stmt = (
            update(model)
            .where(model.id == record_id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(stmt)
        await db.commit()
        return {"status": "success", "message": f"{model.__tablename__} with ID {record_id} updated."}
    except SQLAlchemyError as e:
        await db.rollback()
        logger.exception(f"Erro ao atualizar {model.__tablename__}: {e}")
        return {"status": "error", "message": str(e)}


# 📌 Atualizações específicas por tabela

async def update_oee_setup(db: AsyncSession, record_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    return await update_record(db, OEESetup, record_id, data)

async def update_digest_data(db: AsyncSession, record_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    return await update_record(db, DigestData, record_id, data)

async def update_planned_downtime_setup(db: AsyncSession, record_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    return await update_record(db, PlannedDowntimeSetup, record_id, data)

async def update_unplanned_downtime_setup(db: AsyncSession, record_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    return await update_record(db, UnplannedDowntimeSetup, record_id, data)

async def update_paradas(db: AsyncSession, record_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    return await update_record(db, Paradas, record_id, data)

async def update_planned_downtime(db: AsyncSession, record_id: int, data: schemas.CreatePlannedDowntimeSchema) -> Dict[str, Any]:
    #return await update_record(db, PlannedDowntime, record_id, data)
    update_dict = data.model_dump(exclude_unset=True) # exclude_unset=True garante que só os campos realmente enviados na requisição sejam atualizados (evitando sobrescrever com None).
    return await update_record(db, PlannedDowntime, record_id, update_dict)

async def update_unplanned_downtime(db: AsyncSession, record_id: int, data: schemas.CreateUnplannedDowntimeSchema) -> Dict[str, Any]:
    #return await update_record(db, UnplannedDowntime, record_id, data)
    update_dict = data.model_dump(exclude_unset=True) # exclude_unset=True garante que só os campos realmente enviados na requisição sejam atualizados (evitando sobrescrever com None).
    return await update_record(db, UnplannedDowntime, record_id, update_dict)

async def update_auto_oee(db: AsyncSession, record_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    return await update_record(db, AutoOEE, record_id, data)
