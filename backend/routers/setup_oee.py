from datetime import date, datetime, time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.db import get_db
import database.crud as crud


# Importando as classes do SQLAlchemy
from database.models import OEESetup, PlannedDowntime, UnplannedDowntime, Paradas, AutoOEE, PlannedDowntimeSetup
import schemas as schemas

router = APIRouter()



# 📌 GET
@router.get("/all-oee-setup", response_model=List[schemas.OEESetupSchema])
async def get_oee_setups(db: AsyncSession = Depends(get_db)):
    try:
        setups = await crud.get_all_oee_setups(db)
        return setups
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/oee-setup-by-id/{oee_id}", response_model=schemas.OEESetupSchema)
async def get_oee_setup(oee_id: int, db: AsyncSession = Depends(get_db)):
    try:
        setup = await crud.get_oee_setup_by_id(db, oee_id)
        if not setup:
            raise HTTPException(status_code=404, detail="OEESetup not found")
        return setup
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/oee-setup-by-camera-id/{camera_name_id}", response_model=schemas.OEESetupSchema)
async def get_oee_setup_by_camera_name_id(camera_name_id: int, db: AsyncSession = Depends(get_db)):
    try:
        setup = await crud.get_oee_setup_by_camera_name_id(db=db, camera_name_id=camera_name_id)
        if not setup:
            raise HTTPException(status_code=404, detail="OEESetup not found")
        return setup
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# 📌 POST
@router.post("/post_oee-setup", response_model=schemas.CREATEOEESetupSchema)
async def create_oee_setup_route(
    request: schemas.CREATEOEESetupSchema,
    db: AsyncSession = Depends(get_db)
):
    """ Exemplo de dados 
        {
        "user": "operador1",
        "stop_time": 1.5,
        "digest_time": 2.0,
        "line_speed": 120.0,
        "camera_name_id": 1,
        "shifts": [
            {
            "id": "1",
            "name": "Manhã",
            "days": ["segunda", "quarta"],
            "startTime": "07:00",
            "endTime": "08:00"
            },
            {
            "id": "2",
            "name": "Noite",
            "days": ["terça", "quinta"],
            "startTime": "18:00",
            "endTime": "19:00"
            }
        ]
        }

    """
    try:
        oee = await crud.create_oee_setup(
            db=db,
            user=request.user,
            stop_time=request.stop_time,
            line_speed=request.line_speed,
            digest_time=request.digest_time,
            camera_name_id=request.camera_name_id,
            shifts=[shift.dict() for shift in request.shifts] if request.shifts else None
        )
        return request  # ou algum response customizado com o que foi criado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# 📌 DELETE
@router.delete("/delete_oee_setup/{id}")
async def delete_oee_setup_route(id: int, db: AsyncSession = Depends(get_db)):
    return await crud.delete_oee_setup(db, record_id=id)



# 📌 UPDATE
@router.put("/update-oee-setup/{setup_id}", response_model=dict)
async def update_oee_setup_route(setup_id: int, data: schemas.CREATEOEESetupSchema, db: AsyncSession = Depends(get_db)):
    print('setup_id', setup_id)
    print('data', data)
    try:
        updated_data = {
            "user": data.user,
            "stop_time": data.stop_time,
            "digest_time": data.digest_time,
            "line_speed": data.line_speed,
            "camera_name_id": data.camera_name_id,
            "shifts": [shift.dict() for shift in data.shifts] if data.shifts else None
        }
        print('updated_data', updated_data)
        updated = await crud.update_oee_setup(db, record_id=setup_id, data=updated_data)
        if not updated:
            raise HTTPException(status_code=404, detail="OEESetup not found")
        print('updated', updated)
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))