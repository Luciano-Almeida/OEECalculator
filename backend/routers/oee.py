from datetime import datetime, time, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional, Tuple

from database.db import get_db
import database.crud as crud
from utils import timedelta_to_iso
from services import oee_by_period

# Importando as classes do SQLAlchemy
from database.db.conexao_db_externo import get_external_db
from database.models import OEESetup, PlannedDowntime, UnplannedDowntime, Paradas, AutoOEE, PlannedDowntimeSetup
import schemas as schemas
from services import get_authenticated_user_data
from utils import DIAS_SEMANA

router = APIRouter()



def parse_time(t: str) -> time:
    return datetime.strptime(t, "%H:%M").time()

def is_within_shift(start: time, end: time, current: time) -> bool:
    # Turno normal (não cruza meia-noite)
    if start <= end:
        return start <= current < end
    # Turno noturno (cruza a meia-noite)
    else:
        return current >= start or current < end

def get_current_or_previous_shift(hora_atual: datetime, shifts: List[schemas.Shift]) -> Optional[Tuple[datetime, datetime]]:

    current_weekday = hora_atual.weekday()
    current_time = hora_atual.time()

    print(f"\n[DEBUG] Hora atual: {hora_atual}")
    print(f"[DEBUG] Dia da semana atual: {current_weekday} ({hora_atual.strftime('%A')})")
    print(f"[DEBUG] Hora atual (apenas hora): {current_time}")
    print(f"[DEBUG] Total de turnos configurados: {len(shifts)}")

    # Primeiro, procurar shift ativo no momento
    for shift in shifts:
        shift_days = [DIAS_SEMANA[d] for d in shift['days'] if d in DIAS_SEMANA]
        print(f"\n[DEBUG] Verificando turno: {shift['name']}")
        print(f"[DEBUG] Dias do turno: {shift_days}")

        if current_weekday in shift_days:
            start = parse_time(shift['startTime'])
            end = parse_time(shift['endTime'])
            print(f"[DEBUG] Horário do turno: {start} até {end}")

            if is_within_shift(start, end, current_time):
                start_dt = datetime.combine(hora_atual.date(), start)
                end_dt = datetime.combine(hora_atual.date(), end)
                if end <= start:
                    end_dt += timedelta(days=1)

                print(f"[DEBUG] Turno ATUAL encontrado: {shift['name']}")
                print(f"[DEBUG] Início: {start_dt}, Fim: {end_dt}")
                return start_dt, end_dt

    # Se nenhum ativo agora, procurar o último válido (do dia atual ou anterior)
    print("\n[DEBUG] Nenhum turno atual encontrado, buscando o turno anterior válido...")
    latest_shift_times: Optional[Tuple[datetime, datetime]] = None
    latest_start_datetime = None

    for shift in shifts:
        shift_days = [DIAS_SEMANA[d] for d in shift['days'] if d in DIAS_SEMANA]
        for offset in [0, -1, -2, -3, -4, -5]:  # Hoje e ontem e dias anteriores
            check_day = (current_weekday + offset) % 7
            if check_day in shift_days:
                shift_date = (hora_atual - timedelta(days=-offset)).date()
                start_time = parse_time(shift['startTime'])
                end_time = parse_time(shift['endTime'])

                start_dt = datetime.combine(shift_date, start_time)
                end_dt = datetime.combine(shift_date, end_time)
                if end_time <= start_time:
                    end_dt += timedelta(days=1)

                print(f"\n[DEBUG] Possível turno anterior: {shift['name']}")
                print(f"[DEBUG] Dia considerado: {shift_date} (offset: {offset})")
                print(f"[DEBUG] Início: {start_dt}, Fim: {end_dt}")

                if start_dt < hora_atual:
                    if not latest_start_datetime or start_dt > latest_start_datetime:
                        latest_start_datetime = start_dt
                        latest_shift_times = (start_dt, end_dt)
                        print("[DEBUG] Este é o mais recente até agora.")

    if latest_shift_times:
        print(f"\n[DEBUG] Turno ANTERIOR selecionado: Início: {latest_shift_times[0]}, Fim: {latest_shift_times[1]}")
    else:
        print("\n[DEBUG] Nenhum turno anterior encontrado.")

    return latest_shift_times
 
from typing import List
from datetime import datetime, timedelta

def formatar_paradas_planejadas(paradas_raw: List, data_base: datetime) -> List[dict]:
    paradas_formatadas = []

    for parada in paradas_raw:
        start_parts = list(map(int, str(parada.start_time).split(":")))
        stop_parts = list(map(int, str(parada.stop_time).split(":")))

        start_dt = data_base.replace(hour=start_parts[0], minute=start_parts[1], second=start_parts[2], microsecond=0)
        stop_dt = data_base.replace(hour=stop_parts[0], minute=stop_parts[1], second=stop_parts[2], microsecond=0)

        if stop_dt <= start_dt:
            stop_dt += timedelta(days=1)  # Caso a parada cruze a meia-noite

        paradas_formatadas.append({
            "start": start_dt.isoformat(),
            "end": stop_dt.isoformat(),
            "name": parada.name  # opcional, caso queira exibir tooltip/legenda
        })

    return paradas_formatadas


@router.get("/oee/", response_model=Dict)
async def get_oee(
    hora_atual: datetime, 
    camera_name_id: int, 
    db: AsyncSession = Depends(get_db),
    external_db: AsyncSession = Depends(get_external_db)
):
    """
    Retorna uma lista com todas os dados do OEE e do historico de produção discretizado por um periodo
    """
    # Consultar os dados necessários para o cálculo
    # 1. Dados de setup e produção da câmera
    oee_setup = await crud.get_oee_setup_by_camera_name_id(db=db, camera_name_id=camera_name_id)
    
    if not oee_setup:
        raise HTTPException(status_code=404, detail="No valid OEE setup found for the given camera and time range.")

    # extrair horarios do turno
    shift_atual = get_current_or_previous_shift(hora_atual, oee_setup.shifts)
    if not shift_atual:
        raise HTTPException(status_code=404, detail="No valid shift_atual found for the given camera and time.")

    inicio, fim = shift_atual
    # se preferir o fim como a hora atual
    if fim > hora_atual:
        fim = hora_atual
    print('pesquisa', inicio, fim)
    oee_data = await oee_by_period(inicio, fim, camera_name_id, oee_setup.line_speed, db)

    # 3. Histórico de produção
    discretized_history = await crud.get_total_ok_nok_grouped_by_rows(
        db=db,
        inicio=inicio,
        fim=fim,
        camera_name_id=camera_name_id,
        group_size=1
    )
    
    # 4. Usuário
    user = await get_authenticated_user_data(external_db)
    
    # 5. Setup Paradas Planejadas da câmera específica
    setup_paradas_planejadas_raw = await crud.get_all_planned_downtime_setups(db)
    setup_paradas_planejadas = formatar_paradas_planejadas(setup_paradas_planejadas_raw, inicio)

    # 6. Monta resposta
    oee_data["autentication"] = user
    oee_data["shift_atual"] = shift_atual
    oee_data["setup_paradas_planejadas"] = setup_paradas_planejadas
    oee_data["discretizado"] = discretized_history
    return oee_data





@router.get("/oee_back/", response_model=Dict)
async def get_oee_back(
    inicio: datetime, 
    fim: datetime, 
    camera_name_id: int, 
    db: AsyncSession = Depends(get_db),
    external_db: AsyncSession = Depends(get_external_db)
):
    """
    Retorna uma lista com todas os dados do OEE e do historico de produção discretizado por um periodo
    """
    # Consultar os dados necessários para o cálculo
    # 1. Dados de setup e produção da câmera
    oee_setup = await crud.get_oee_setup_by_camera_name_id(db=db, camera_name_id=camera_name_id)
    print(f"\n[DEBUG] Hora inicio: {inicio}")
    print(f"\n[DEBUG] Hora fim: {fim}")
    if not oee_setup:
        raise HTTPException(status_code=404, detail="No valid OEE setup found for the given camera and time range.")

    oee_data = await oee_by_period(inicio, fim, camera_name_id, oee_setup.line_speed, db)

    discretized_history = await crud.get_total_ok_nok_discretized_by_period(
        db=db,
        inicio=inicio,
        fim=fim,
        camera_name_id=camera_name_id,
        period=timedelta(minutes=2)
    )
    
    user = await get_authenticated_user_data(external_db)

    oee_data["autentication"] = user
    oee_data["discretizado"] = discretized_history
    return oee_data