from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict, List

from services import servico_data_received
from database.db import get_db
import database.crud as crud
import schemas as schemas

from database.crud import create_parada

router = APIRouter()

# 📌 Criando todas as Paradas
@router.post("/criando_todas_paradas/")
async def create_parada_endpoint(db: AsyncSession = Depends(get_db)):
    resultado = servico_data_received.fetch_paradas()
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



# 📌 READ
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

@router.get("/paradas_planejadas/", response_model=List[schemas.PlannedDowntimeSchema])#, response_model=List[str])
async def get_paradas_planejadas(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_planned_downtime(db)

@router.get("/get-seconds-paradas/")
async def get_seconds_paradas(
    inicio: datetime,
    fim: datetime,
    camera_name_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Chama a função para calcular o total de downtime planejado
        total_planned_downtime_seconds = await crud.get_total_planned_downtime_seconds(db, inicio, fim, camera_name_id)
        
        # Chama a função para calcular o total de downtime não planejado
        total_unplanned_downtime_seconds = await crud.get_total_unplanned_downtime_seconds(db, inicio, fim, camera_name_id)
        
        # Chama a função para calcular o total de downtime não justificado
        total_nonjustified_downtime_seconds = await crud.get_total_nonjustified_downtime_seconds(db, inicio, fim, camera_name_id)
        
        # Retorna o total de downtime não justificado
        return {"total planejados seconds": total_planned_downtime_seconds,
                "total não planejados seconds": total_unplanned_downtime_seconds,
                "total não justificados seconds": total_nonjustified_downtime_seconds,
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Função que retorna o resumo das paradas
@router.get("/get_resumo_paradas_by_period")
async def resumo_paradas_by_period(
    inicio: str,  # Início do período, no formato "YYYY-MM-DD HH:MM:SS"
    fim: str,     # Fim do período, no formato "YYYY-MM-DD HH:MM:SS"
    camera_name_id: int,  # ID da câmera ou linha de produção
    db: AsyncSession = Depends(get_db)  # Função para obter a sessão do DB
) -> Dict[str, float]:
    try:
        # Convertendo as strings de data para datetime
        inicio_dt = datetime.strptime(inicio, "%Y-%m-%d %H:%M:%S")
        fim_dt = datetime.strptime(fim, "%Y-%m-%d %H:%M:%S")
        
        # Chama a função que retorna o resumo das paradas
        resumo = await crud.get_resumo_paradas_by_period(db, inicio_dt, fim_dt, camera_name_id)
        return resumo
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 📌 CREATE
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

@router.post("/create_parada_planejada/", response_model=schemas.PlannedDowntimeSchema)
async def post_setup_paradas_planejadas(data: schemas.CreatePlannedDowntimeSchema, db: AsyncSession = Depends(get_db)):
    try:
        print('Data create_parada_planejada', data)
        # Criando o novo setup no banco de dados
        new_setup = await crud.create_planned_downtime(
            db=db,
            user=data.user, 
            planned_downtime_id=data.planned_downtime_id, 
            paradas_id=data.paradas_id, 
            observacoes=data.observacoes
        )
        return new_setup
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



# 📌 DELETE
@router.delete("/delete_planned_downtime/{record_id}", response_model=Dict[str, Any])
async def delete_planned_downtime_route(record_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.delete_planned_downtime(db, record_id)

@router.delete("/delete_unplanned_downtime/{record_id}", response_model=Dict[str, Any])
async def delete_unplanned_downtime_route(record_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.delete_unplanned_downtime(db, record_id)


# 📌 UPDATE
@router.put("/update_parada_nao_planejada/{record_id}", response_model=Dict[str, Any])
async def update_setup_paradas_nao_planejadas(
    record_id: int,
    data: schemas.CreateUnplannedDowntimeSchema, 
    db: AsyncSession = Depends(get_db)
):
    result = await crud.update_unplanned_downtime(db, record_id, data)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.put("/update_parada_planejada/{record_id}", response_model=Dict[str, Any])
async def update_setup_paradas_planejadas(
    record_id: int,
    data: schemas.CreatePlannedDowntimeSchema, 
    db: AsyncSession = Depends(get_db)
):
    result = await crud.update_planned_downtime(db, record_id, data)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

