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
import schemas as schemas


router = APIRouter()


@router.get("/autentication")
def get_authenticated_user():
    user = {
        "nome": "usuarioAutomático",
        "permissoes": [
            "acessar_oee_dinamico", 
            "acessar_paradas",
            "acessar_oee_search",
            "acessar_oee_setup",
            "acessar_paradas_setup",
            "acessar_voltar"
        ]
    }
    return user

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