from datetime import time
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from database.models import (OEESetup, DigestData,
    PlannedDowntimeSetup, UnplannedDowntimeSetup, Paradas,
    PlannedDowntime, UnplannedDowntime, AutoOEE
)

# 📌 Função genérica para criar um registro (assíncrona)
async def create_record(db: AsyncSession, record):
    try:
        db.add(record)
        await db.commit()  # Commit assíncrono
        await db.refresh(record)  # Atualiza o objeto com dados persistidos
        return record
    except SQLAlchemyError as e:
        await db.rollback()  # Rollback assíncrono
        print(f"Erro ao criar o registro: {e}")
        raise

# 📌 Funções para criar registros em cada tabela

async def create_oee_setup(
    db: AsyncSession, user: str, stop_time: float, 
    line_speed: float, digest_time: float, camera_name_id: int, shifts: Optional[List[Dict]] = None
) -> OEESetup:
    new_oee = OEESetup(
        user=user, 
        stop_time=stop_time, 
        line_speed=line_speed, 
        digest_time=digest_time,
        camera_name_id=camera_name_id,
        shifts=shifts
    )
    return await create_record(db, new_oee)

async def create_digest_data(
    db: AsyncSession, ok: int, nok: int, lote_id: int, camera_name_id: int,
    start_digest, stop_digest
) -> DigestData:
    new_digest = DigestData(
        ok=ok, nok=nok, lote_id=lote_id, camera_name_id=camera_name_id,
        start_digest=start_digest, stop_digest=stop_digest
    )
    return await create_record(db, new_digest)

async def create_planned_downtime_setup(
    db: AsyncSession, name: str, start_time: time, stop_time: time, camera_name_id: int
) -> PlannedDowntimeSetup:
    new_setup = PlannedDowntimeSetup(
        name=name, start_time=start_time, stop_time=stop_time, camera_name_id=camera_name_id
    )
    return await create_record(db, new_setup)

async def create_unplanned_downtime_setup(db: AsyncSession, name: str) -> UnplannedDowntimeSetup:
    new_setup = UnplannedDowntimeSetup(name=name)
    return await create_record(db, new_setup)

async def create_parada(
    db: AsyncSession, start, stop, camera_name_id: int
) -> Paradas:
    new_parada = Paradas(start=start, stop=stop, camera_name_id=camera_name_id)
    return await create_record(db, new_parada)

async def create_planned_downtime(
    db: AsyncSession, user: str, planned_downtime_id: int, paradas_id: int, observacoes: str
) -> PlannedDowntime:
    new_downtime = PlannedDowntime(
        user=user, planned_downtime_id=planned_downtime_id, 
        paradas_id=paradas_id, observacoes=observacoes
    )
    return await create_record(db, new_downtime)

async def create_unplanned_downtime(
    db: AsyncSession, user: str, unplanned_downtime_id: int, paradas_id: int, observacoes: str
) -> UnplannedDowntime:
    new_downtime = UnplannedDowntime(
        user=user, unplanned_downtime_id=unplanned_downtime_id, 
        paradas_id=paradas_id, observacoes=observacoes
    )
    return await create_record(db, new_downtime)

async def create_auto_oee(
    db: AsyncSession, availability: float, performance: float, quality: float,
    oee: float, total_ok: int, total_not_ok: int, timestamp
) -> AutoOEE:
    new_oee = AutoOEE(
        Availability=availability, Performance=performance, 
        Quality=quality, OEE=oee, Total_OK=total_ok, 
        Total_NOT_OK=total_not_ok, Timestamp=timestamp
    )
    return await create_record(db, new_oee)
