from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from services import paradas_digest
from database.db import get_db
import database.crud as crud
from utils import timedelta_to_iso

from database.crud import create_parada

# Importando as classes do SQLAlchemy
from database.models import OEESetup, PlannedDowntime, UnplannedDowntime, Paradas, AutoOEE, PlannedDowntimeSetup

router = APIRouter()
 
@router.get("/oee/", response_model=Dict)
async def get_oee(inicio: datetime, fim: datetime, camera_name_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retorna uma lista com todas os dados do OEE
    """
    # Consultar os dados necessários para o cálculo
    # 1. Dados de setup e produção da câmera
    #oee_setup = db.query(OEESetup).filter(OEESetup.camera_name_id == camera_name_id, 
    #                                      OEESetup.start_shift >= inicio,
    #                                      OEESetup.stop_shift <= fim).all()
    oee_setup = await crud.get_oee_setup_by_camera_name_id(db=db, camera_name_id=camera_name_id)
    #formatted_start_shift = f"'{OEESetup['start_shift'].strftime('%Y-%m-%d %H:%M:%S')}'"
    #formatted_stop_shift = f"'{OEESetup['stop_shift'].strftime('%Y-%m-%d %H:%M:%S')}'"

    #if not oee_setup or oee_setup.start_shift > fim or oee_setup.stop_shift < inicio:
    #    raise HTTPException(status_code=404, detail="No OEE setup found for the given camera and time range.")

    # B. Tempo de produção (Total de Tempo Disponível)
    total_available_time = fim - inicio

    # C. Paradas planejadas
    #total_planned_downtime = timedelta(hours=0, minutes=0, seconds=0)
    total_planned_downtime_seconds = await crud.get_total_planned_downtime_seconds(db=db, inicio=inicio, fim=fim, camera_name_id=camera_name_id)
    total_planned_downtime = timedelta(seconds=int(total_planned_downtime_seconds))
    
    # D. Tempo disponícel líquido (B - C)
    tempo_disponivel_liquido = total_available_time - total_planned_downtime

    # E. Paradas não planejadas
    #total_unplanned_downtime = timedelta(hours=0, minutes=0, seconds=0)
    total_unplanned_downtime_seconds = await crud.get_total_unplanned_downtime_seconds(db=db, inicio=inicio, fim=fim, camera_name_id=camera_name_id)
    total_unplanned_downtime = timedelta(seconds=int(total_unplanned_downtime_seconds))
    

    # F. Tempo operando (Tempo disponível - Paradas não planejadas) (D - E)
    operating_time = tempo_disponivel_liquido - total_unplanned_downtime

    # G. Relação de disponibilidade (F / D)
    availability_ratio = operating_time.total_seconds() / tempo_disponivel_liquido.total_seconds() if tempo_disponivel_liquido.total_seconds() > 0 else 0
    #print('availability_ratio', availability_ratio)

    # H. Número total de peças produzidas (boas e ruins)
    #total_produced_pieces = db.query(DataReceived).filter(
    #    DataReceived.camera_name_id == camera_name_id,
    #    DataReceived.timestamp >= inicio,
    #    DataReceived.timestamp <= fim
    #).count()
    #total_produced_pieces = 1000
    production = await crud.get_total_ok_nok_from_digest(db=db, inicio=inicio, fim=fim, camera_name_id=camera_name_id)
    total_produced_pieces = production["total_ok"] + production["total_nok"]

    # I. Tempo ideal de ciclo (valor em pç/min)
    #ideal_cycle_time = oee_setup["line_speed"]
    ideal_cycle_time = oee_setup.line_speed

    # J. Número máximo de peças que podem ser produzidas (Tempo operando * Tempo ideal de ciclo) (I x F)
    max_pieces = (operating_time.total_seconds() / 60) * ideal_cycle_time

    # K. Relação de desempenho (Desempenho = Peças Produzidas / Máximo de Peças) (H / J)
    performance_ratio = total_produced_pieces / max_pieces if max_pieces > 0 else 0

    # L. Total de peças defeituosas
    #total_defective_pieces = 0
    total_defective_pieces = production["total_nok"]

    # M. Relação de qualidade (Qualidade = (Peças boas - Defeituosas) / Peças boas) (H - L / H)
    quality_ratio = (total_produced_pieces - total_defective_pieces) / total_produced_pieces if total_produced_pieces > 0 else 0
    print('quality_ratio', quality_ratio)

    # OEE
    oee = availability_ratio * performance_ratio * quality_ratio

    discretizado = await crud.get_total_ok_nok_discretized_by_period(db=db, 
                                                                     inicio=inicio, 
                                                                     fim=fim, 
                                                                     camera_name_id=camera_name_id,
                                                                     period=timedelta(minutes=1)
                                                                     )


    # Retornando os resultados no formato JSON
    return {
        "A_Inicio": inicio,
        "A_Fim": fim,
        "B_Tempo_total_disponivel": timedelta_to_iso(total_available_time),
        "C_Paradas_planejadas": timedelta_to_iso(total_planned_downtime),
        "D_Tempo_disponivel_liquido(B-C)": timedelta_to_iso(tempo_disponivel_liquido),
        "E_Paradas_nao_planejadas": timedelta_to_iso(total_unplanned_downtime),
        "F_Tempo_operando(D-E)": timedelta_to_iso(operating_time),
        "G_Relacao_disponibilidade(F/D)": round(availability_ratio * 100, 2),
        
        "H_Total_pecas_produzidas": total_produced_pieces,
        "I_Tempo_ideal_ciclo": ideal_cycle_time,
        "J_Max_pecas_possiveis(IxF)": max_pieces,
        "K_Relacao_desempenho(H/J)": round(performance_ratio * 100, 2),
        
        "L_Total_pecas_defeituosas": total_defective_pieces,
        "M_Relacao_qualidade(H-(L/H))": round(quality_ratio * 100, 2),

        "oee(GxKxM)": round(oee * 100, 2),

        "discretizado": discretizado
    }