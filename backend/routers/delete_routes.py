from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.crud.delete import (
    delete_oee_setup, delete_digest_data,
    delete_planned_downtime_setup, delete_unplanned_downtime_setup,
    delete_parada, delete_planned_downtime, delete_unplanned_downtime,
    delete_auto_oee
)
from database.db import get_db

router = APIRouter()

# Rota para deletar o OEESetup
@router.delete("/delete_oee_setup/{id}")
async def delete_oee_setup_route(id: int, db: Session = Depends(get_db)):
    return delete_oee_setup(db, id)

# Rota para deletar o DigestData
@router.delete("/delete_digest_data/{id}")
async def delete_digest_data_route(id: int, db: Session = Depends(get_db)):
    return delete_digest_data(db, id)

# Rota para deletar a Parada
@router.delete("/delete_parada/{id}")
async def delete_parada_route(id: int, db: Session = Depends(get_db)):
    return delete_parada(db, id)

# Rota para deletar o AutoOEE
@router.delete("/delete_auto_oee/{id}")
async def delete_auto_oee_route(id: int, db: Session = Depends(get_db)):
    return delete_auto_oee(db, id)
