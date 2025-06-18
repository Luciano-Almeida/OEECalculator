# app.py
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from database.db.conexao_db_externo import get_external_db
import database_external.crud as crud_external
import schemas as schemas


router = APIRouter()


@router.get("/autentication")
async def get_authenticated_user(db: AsyncSession = Depends(get_external_db)):
    try:
        user_id = await crud_external.get_last_active_user_id(db)
        user_data = await crud_external.get_user_info_by_id(db, user_id)
        permissoes = await crud_external.get_permissoes_ativas_por_nivel_acesso(db, user_data["nivel_acesso"])
        
        user = {
            "nome": user_data["nome"],
            "nivel_acesso": user_data["nivel_acesso"],
            "permissoes": permissoes["permissoes"]
        }

        print(f"--------{user_id}Usuário e Permissões {user}")

        return user

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/criar_auditoria")
async def criar_auditoria(
    auditoria: schemas.AuditoriaCreate,
    db: AsyncSession = Depends(get_external_db)
):
    try:
        query = text("""
            INSERT INTO "Auditoria" ("Data", "Usuario", "Tela", "Acao", "Detalhe")
            VALUES (:data, :usuario, :tela, :acao, :detalhe)
        """)
        
        horario_atual = datetime.now(ZoneInfo("America/Sao_Paulo")).replace(tzinfo=None)
        
        await db.execute(query, {
            "data": horario_atual,
            "usuario": auditoria.usuario,
            "tela": auditoria.tela,
            "acao": auditoria.acao,
            "detalhe": auditoria.detalhe
        })
        
        await db.commit()
        return {"mensagem": f"Registro de auditoria criado com sucesso data:{horario_atual}"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))