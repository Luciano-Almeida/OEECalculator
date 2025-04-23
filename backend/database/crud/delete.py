from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from database.models import (
    OEESetup, DigestData,
    PlannedDowntimeSetup, UnplannedDowntimeSetup, Paradas,
    PlannedDowntime, UnplannedDowntime, AutoOEE
)

# 📌 Função genérica para deletar um registro por ID
async def delete_by_id(db: AsyncSession, model, record_id: int) -> bool:
    try:
        stmt = delete(model).where(model.id == record_id)
        await db.execute(stmt)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        print(f"Erro ao deletar {model.__tablename__} com id {record_id}: {e}")
        await db.rollback()
        return False


# 📌 Funções específicas para deletar por ID

async def delete_oee_setup(db: AsyncSession, record_id: int) -> bool:
    return await delete_by_id(db, OEESetup, record_id)

async def delete_digest_data(db: AsyncSession, record_id: int) -> bool:
    return await delete_by_id(db, DigestData, record_id)

async def delete_planned_downtime_setup(db: AsyncSession, record_id: int) -> bool:
    return await delete_by_id(db, PlannedDowntimeSetup, record_id)

async def delete_unplanned_downtime_setup(db: AsyncSession, record_id: int) -> bool:
    return await delete_by_id(db, UnplannedDowntimeSetup, record_id)

async def delete_paradas(db: AsyncSession, record_id: int) -> bool:
    return await delete_by_id(db, Paradas, record_id)

async def delete_planned_downtime(db: AsyncSession, record_id: int) -> bool:
    return await delete_by_id(db, PlannedDowntime, record_id)

async def delete_unplanned_downtime(db: AsyncSession, record_id: int) -> bool:
    return await delete_by_id(db, UnplannedDowntime, record_id)

async def delete_auto_oee(db: AsyncSession, record_id: int) -> bool:
    return await delete_by_id(db, AutoOEE, record_id)
