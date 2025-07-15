from datetime import date, datetime, time, timedelta
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, validator
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional

from database.db import get_db
import database.crud as crud
from utils import timedelta_to_iso

from database.crud import create_parada

# Importando as classes do SQLAlchemy
from database.models import OEESetup, PlannedDowntime, UnplannedDowntime, Paradas, AutoOEE, PlannedDowntimeSetup
import schemas as schemas

# Logger específico
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/get_autooee/", response_model=List[schemas.AutoOEESchema])
async def get_autooee(db: AsyncSession = Depends(get_db)):
    """
    Retorna uma lista com todas os dados
    """
    return await crud.get_all_auto_oee(db)

@router.delete("/delete_all_autooee_by_id/")
async def delete_all_autooee_by_id(db: AsyncSession = Depends(get_db)):
    """
    Lê todos os AutoOEE e deleta um por um, usando a função de exclusão por ID.
    """
    # Pega todos os registros
    autooees = await crud.get_all_auto_oee(db)

    # Apaga um por um usando a função existente
    for autooee in autooees:
        #autooee = json.loads(autooee)
        await crud.delete_auto_oee(db, autooee.id)

    return {"message": f"{len(autooees)} registros de AutoOEE foram deletados com sucesso."}

@router.delete("/delete_all_paradas_by_id/")
async def delete_all_paradas_by_id(db: AsyncSession = Depends(get_db)):
    """
    Lê todos os Digest Data e deleta um por um, usando a função de exclusão por ID.
    """
    # Pega todos os registros
    paradas = await crud.get_all_paradas(db)

    # Apaga um por um usando a função existente
    for parada in paradas:
        #autooee = json.loads(autooee)
        await crud.delete_paradas(db, parada.id)

    return {"message": f"{len(paradas)} registros de parada foram deletados com sucesso."}


@router.delete("/delete_all_digest_data_by_id/")
async def delete_all_digest_data_by_id(db: AsyncSession = Depends(get_db)):
    """
    Lê todos os DigestData e deleta um por um, usando a função de exclusão por ID.
    """
    # Lê todos os DigestData
    digest_data_list = await crud.get_all_digest_data(db)

    # Deleta um por um usando a função equivalente a delete_auto_oee_by_id
    for digest_data in digest_data_list:
        await crud.delete_digest_data(db, digest_data.id)

    return {"message": f"{len(digest_data_list)} registros de DigestData foram deletados com sucesso."}

@router.delete("/delete_all_parada_planejada_data_by_id/")
async def delete_all_parada_planejada_data_by_id(db: AsyncSession = Depends(get_db)):
    """
    Lê todos as paradas planejadas e deleta um por um, usando a função de exclusão por ID.
    """
    # Lê todos os DigestData
    plannedDowntime_data_list = await crud.get_all_planned_downtime(db)

    # Deleta um por um usando a função equivalente a delete_auto_oee_by_id
    for plannedDowntime_data in plannedDowntime_data_list:
        await crud.delete_planned_downtime(db, plannedDowntime_data.id)

    return {"message": f"{len(plannedDowntime_data_list)} registros de PlannedDowntime foram deletados com sucesso."}



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