# app.py
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from fastapi.encoders import jsonable_encoder

from services.servico_data_received import fetch_all_digest_data_from_datareceived
from database.db.conexao_db_externo import get_external_db
import database.crud as crud


router = APIRouter()


@router.get("/dados-external-db")
async def dados_external_db(db: AsyncSession = Depends(get_external_db)):
    query = text("""
            SELECT * FROM "data_received" LIMIT 10;
        """)
    try:
        result = await db.execute(query)
        #tabelas = result.fetchall()        
        #return {"tabelas": [dict(row) for row in tabelas]}  # Convertendo para dicionário
        tabelas = result.mappings().all()
        print("✅ Tabelas encontradas:", tabelas)
        #return tabelas
        return {"tabelas": jsonable_encoder(tabelas)}
    except Exception as e:
        print("❌ Erro ao buscar dados:", e)
        return {"erro": str(e)}

@router.get("/tabelas-external-db")
async def listar_tabelas_external_db(db: AsyncSession = Depends(get_external_db)):
    try:
        print("🧪 Executando query...")
        query = text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        result = await db.execute(query)
        tabelas = result.scalars().all()
        #tabelas = result.fetchall()
        #print("✅ Tabelas encontradas:", tabelas)
        #return {"tabelas": tabelas}
        return {"db": "external_db", "tabelas": tabelas}
    except Exception as e:
        print("❌ Erro ao executar query:", str(e))
        raise e
    

@router.get("/teste")
async def teste(db: AsyncSession = Depends(get_external_db)):
    try:
        print("🧪 Executando query...")
        
        resultados = await fetch_all_digest_data_from_datareceived(
                db=db,
                CAMERA_NAME_ID=2, 
                DIGEST_TIME=60
                )
        
        print("✅ Tabelas encontradas:", resultados)
        #return {"tabelas": tabelas}
        return {"db": "external_db", "tabelas": 'resultados'}
    except Exception as e:
        print("❌ Erro ao executar query:", str(e))
        raise e