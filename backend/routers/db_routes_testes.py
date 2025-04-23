from datetime import date, datetime, time, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, validator
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional

from services import paradas_digest
from database.db import get_db
import database.crud as crud
from utils import timedelta_to_iso

from database.crud import create_parada

# Importando as classes do SQLAlchemy
from database.models import OEESetup, PlannedDowntime, UnplannedDowntime, Paradas, AutoOEE, PlannedDowntimeSetup
import schemas as schemas

router = APIRouter()



@router.put("/alterar-oee-setup-id/{id_atual}/alterar-id/{novo_id}")
async def alterar_id_oee_setup(id_atual: int, novo_id: int, db: AsyncSession = Depends(get_db)):
    # Verifica se o ID atual existe
    result = await db.execute(select(OEESetup).where(OEESetup.id == id_atual))
    oee_setup = result.scalar_one_or_none()
    if not oee_setup:
        raise HTTPException(status_code=404, detail="OEESetup não encontrado com o ID atual")

    # Verifica se o novo ID já está em uso
    result_novo = await db.execute(select(OEESetup).where(OEESetup.id == novo_id))
    if result_novo.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Já existe um OEESetup com o novo ID")

    try:
        # ⚠️ Executa a alteração do ID com SQL bruto (cuidado com integridade referencial!)
        await db.execute(
            text("UPDATE oee_setup SET id = :novo_id WHERE id = :id_atual"),
            {"novo_id": novo_id, "id_atual": id_atual}
        )
        await db.commit()
        return {"mensagem": "ID alterado com sucesso", "id_novo": novo_id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao alterar ID: {str(e)}")