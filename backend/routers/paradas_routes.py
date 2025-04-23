from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from services import paradas_digest
from database.db import get_db
import database.crud as crud
import schemas as schemas

from database.crud import create_parada

router = APIRouter()

# 📌 Criando todas as Paradas
@router.post("/criando_todas_paradas/")
async def create_parada_endpoint(db: AsyncSession = Depends(get_db)):
    resultado = paradas_digest.fetch_paradas()
    for row in resultado:
        # Extrair os dados da parada
        start_time = row[0]
        stop_time = row[1]
        camera_id = row[3]
        
        # Criar o registro de parada
        start = start_time#datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')  # Converte string para datetime
        stop = stop_time# datetime.strptime(stop_time, '%Y-%m-%d %H:%M:%S')  # Converte string para datetime
        
        # Chama a função para salvar a parada no banco de dados
        # Supondo que a função create_parada retorna a instância da parada criada
        new_parada = await create_parada(db=db, start=start, stop=stop, camera_name_id=1)
        
        # Exibe ou faz algo com a parada criada
        print(f"Parada criada: {new_parada}")
    # Chama a função de criação de parada passando a sessão do db
    return "ok"



# 📌 GET
@router.get("/paradas/", response_model=List[schemas.ParadaSchema])#, response_model=List[str])
async def get_paradas(db: AsyncSession = Depends(get_db)):
    """
    Retorna uma lista com todas as paradas
    return [
        {
            "id": 1,
            "startTime": "2025-03-19 10:00:00",
            "endTime": "2025-03-19 10:15:00",
            "paradaType": "planejada",
            "paradaID": 1,
            "paradaName": "Alongamento",
            "obs": ""
        },
        # outras paradas...
    ]
    """
    
    return await crud.get_all_paradas(db)

@router.get("/paradas_com_tipos/")
async def filtrar_paradas(
    camera_name_id: int,
    inicio: datetime,
    fim: datetime,
    db: AsyncSession = Depends(get_db)
):
    print(f"Realizando a pesquisa por camera {camera_name_id} - Inicio {inicio} - fim {fim}")
    return await crud.get_paradas_com_tipo(db, inicio, fim, camera_name_id)



# 📌 POST
@router.post("/create_parada_nao_planejada/", response_model=schemas.UnplannedDowntimeSchema)
async def post_setup_paradas_nao_planejadas(data: schemas.CreateUnplannedDowntimeSchema, db: AsyncSession = Depends(get_db)):
    try:
        print('Data create_parada_nao_planejada', data)
        # Criando o novo setup no banco de dados
        new_setup = await crud.create_unplanned_downtime(
            db=db,
            user=data.user, 
            unplanned_downtime_id=data.unplanned_downtime_id, 
            paradas_id=data.paradas_id, 
            observacoes=data.observacoes
        )
        return new_setup
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



# 📌 DELETE


# 📌 UPDATE
