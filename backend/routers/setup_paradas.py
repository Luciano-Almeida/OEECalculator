from datetime import datetime, time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.db import get_db
import database.crud as crud
import schemas as schemas

router = APIRouter()

# 📌 GET
@router.get("/get_setup_paradas_planejadas/", response_model=List[schemas.PlannedDowntimeSetupSchema])
async def get_setup_paradas_planejadas(db : AsyncSession = Depends(get_db)):
    return await crud.get_all_planned_downtime_setups(db)

@router.get("/get_setup_paradas_nao_planejadas/", response_model=List[schemas.UnplannedDowntimeSetupSchema])
async def get_paradas_nao_planejadas_setup(db : AsyncSession = Depends(get_db)):
    return await crud.get_all_unplanned_downtime_setups(db)



# 📌 POST
@router.post("/post_setup_paradas_planejadas/", response_model=schemas.PlannedDowntimeSetupSchema)
async def post_setup_paradas_planejadas(setup: schemas.CREATEPlannedDowntimeSetup, db: AsyncSession = Depends(get_db)):
    try:
        # Converte start_time e stop_time de string para time
        start_time = time.fromisoformat(setup.start_time)
        stop_time = time.fromisoformat(setup.stop_time)

        # Criar o novo setup no banco de dados
        new_setup = await crud.create_planned_downtime_setup(
            db=db,
            name=setup.name,
            start_time=start_time,
            stop_time=stop_time,
            camera_name_id=setup.camera_name_id,
        )

        # Retorna a resposta usando o schema de saída (PlannedDowntimeSetupSchema)
        return new_setup  # Supondo que new_setup seja um objeto com os dados do banco
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/post_setup_paradas_nao_planejadas/", response_model=schemas.UnplannedDowntimeSetupSchema)
async def post_setup_paradas_nao_planejadas(setup: schemas.CREATEUnplannedDowntimeSetupSchema, db: AsyncSession = Depends(get_db)):
    try:
        # Criando o novo setup no banco de dados
        new_setup = await crud.create_unplanned_downtime_setup(
            db=db,
            name=setup.name
        )
        return new_setup
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




# 📌 DELETE
# Rota para deletar o PlannedDowntimeSetup
@router.delete("/delete_planned_downtime_setup/{id}")
async def delete_planned_downtime_setup_route(id: int, db: AsyncSession = Depends(get_db)):
    return await crud.delete_planned_downtime_setup(db, id)

# Rota para deletar o UnplannedDowntimeSetup
@router.delete("/delete_unplanned_downtime_setup/{id}")
async def delete_unplanned_downtime_setup_route(id: int, db: AsyncSession = Depends(get_db)):
    return await crud.delete_unplanned_downtime_setup(db, id)



# 📌 UPDATE
# Atualiza PlannedDowntimeSetup
@router.put("/update_planned_downtime_setup/{record_id}")
async def update_planned_setup(
    record_id: int,
    data: schemas.CREATEPlannedDowntimeSetup,
    db: AsyncSession = Depends(get_db)
):
    # Converte os horários de string para datetime.time
    try:
        start_time_obj = time.fromisoformat(data.start_time)
        stop_time_obj = time.fromisoformat(data.stop_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de horário inválido. Use HH:MM:SS.")

    # Prepara o dicionário para o CRUD
    update_data = data.model_dump(exclude_unset=True)
    update_data["start_time"] = start_time_obj
    update_data["stop_time"] = stop_time_obj

    result = await crud.update_planned_downtime_setup(db, record_id, update_data)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# Atualiza UnplannedDowntimeSetup
@router.put("/update_unplanned_downtime_setup/{record_id}")
async def update_unplanned_setup(
    record_id: int,
    data: schemas.CREATEUnplannedDowntimeSetupSchema,
    db: AsyncSession = Depends(get_db)
):
    result = await crud.update_unplanned_downtime_setup(db, record_id, data.model_dump(exclude_unset=True))
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result