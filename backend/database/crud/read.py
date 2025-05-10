from datetime import datetime, timedelta
import json
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Optional

from database.models import (
    OEESetup, DigestData,
    PlannedDowntimeSetup, UnplannedDowntimeSetup, Paradas,
    PlannedDowntime, UnplannedDowntime, AutoOEE
)

# 📌 Função genérica para executar consultas (assíncrona)
async def fetch_all(db: AsyncSession, stmt):
    try:
        result = await db.execute(stmt)  # Execução assíncrona
        return result.scalars().all()  # Obtém todos os resultados
    except SQLAlchemyError as e:
        print(f"Erro ao buscar registros: {e}")
        raise

async def fetch_one(db: AsyncSession, stmt):
    try:
        result = await db.execute(stmt)  # Execução assíncrona
        return result.scalar_one_or_none()  # Obtém um único registro ou None
    except SQLAlchemyError as e:
        print(f"Erro ao buscar registro: {e}")
        raise

async def fetch_all_rows(db: AsyncSession, stmt):
    """ Para selects com múltiplas colunas (e.g., JOIN, funções agregadas), 
        use .all() ao invés de .scalars().all().
    """
    try:
        result = await db.execute(stmt)
        return result.all()  # Retorna todas as linhas como tuplas
    except SQLAlchemyError as e:
        print(f"Erro ao buscar registros: {e}")
        raise


# 📌 Funções de leitura para cada tabela
'''async def get_all_oee_setups(db: AsyncSession) -> List[str]:
    stmt = select(OEESetup)
    #return await fetch_all(db, stmt)
    result = await fetch_all(db, stmt)

    return [json.dumps({
        "id": oee_setup.id,
        "user": oee_setup.user,
        "start_shift": oee_setup.start_shift.isoformat() if oee_setup.start_shift else None,  # Convert to string,
        "stop_shift": oee_setup.stop_shift.isoformat() if oee_setup.stop_shift else None,  # Convert to string,
        "stop_time": oee_setup.stop_time,
        "digest_time": oee_setup.digest_time,
        "line_speed": oee_setup.line_speed,
        "camera_name_id": oee_setup.camera_name_id,
        "timestamp": oee_setup.timestamp.isoformat() if oee_setup.timestamp else None,  # Convert to string,
    }) for oee_setup in result]
'''
async def get_all_oee_setups(db: AsyncSession) -> List[OEESetup]:
    stmt = select(OEESetup).order_by(OEESetup.id)  # Seleciona todos os registros da tabela OEESetup
    return await fetch_all(db, stmt)  # Usa a função genérica para buscar todos

async def get_all_digest_data(db: AsyncSession) -> List[DigestData]: #List[str]:
    stmt = select(DigestData).order_by(DigestData.id)
    result = await fetch_all(db, stmt)
    return result # retorna lista de objetos ORM diretamente
    '''return [json.dumps({
        "id": row.id,
        "ok": row.ok,
        "nok": row.nok,
        "lote_id": row.lote_id,
        "camera_id": row.camera_name_id,
        "start_digest": row.start_digest.isoformat() if row.start_digest else None,      # Convert to string,
        "stop_digest": row.stop_digest.isoformat() if row.stop_digest else None,      # Convert to string,
        #"timestamp": row.timestamp.isoformat() if row.timestamp else None,      # Convert to string        
    }) for row in result]'''

async def get_all_planned_downtime_setups(db: AsyncSession) -> List[PlannedDowntimeSetup]:
    stmt = select(PlannedDowntimeSetup).order_by(PlannedDowntimeSetup.id)
    result = await fetch_all(db, stmt)
    return result # retorna lista de objetos ORM diretamente
    '''return [json.dumps({
        "id": planned_downtime_setup.id,
        "name": planned_downtime_setup.name,
        "start_time": planned_downtime_setup.start_time.strftime("%H:%M") if planned_downtime_setup.start_time else None,
        "stop_time": planned_downtime_setup.stop_time.strftime("%H:%M") if planned_downtime_setup.stop_time else None,
        "camera_name_id": planned_downtime_setup.camera_name_id,
    }) for planned_downtime_setup in result]'''

async def get_all_unplanned_downtime_setups(db: AsyncSession) -> List[UnplannedDowntimeSetup]:
    stmt = select(UnplannedDowntimeSetup).order_by(UnplannedDowntimeSetup.id)
    result = await fetch_all(db, stmt)
    return result
    '''return [json.dumps({
        "id": unplanned_downtime_setup.id,
        "name": unplanned_downtime_setup.name,
    }) for unplanned_downtime_setup in result]'''

async def get_all_paradas(db: AsyncSession) -> List[Paradas]:
    stmt = select(Paradas).order_by(Paradas.id)
    result = await fetch_all(db, stmt)
    return result  # retorna lista de objetos ORM diretamente

async def get_all_planned_downtime(db: AsyncSession) -> List[PlannedDowntime]:
    stmt = select(PlannedDowntime).order_by(PlannedDowntime.id)
    return await fetch_all(db, stmt)

async def get_all_unplanned_downtime(db: AsyncSession) -> List[UnplannedDowntime]:
    stmt = select(UnplannedDowntime).order_by(UnplannedDowntime.id)
    return await fetch_all(db, stmt)

async def get_all_auto_oee(db: AsyncSession) -> List[AutoOEE]:
    stmt = select(AutoOEE).order_by(AutoOEE.id)
    return await fetch_all(db, stmt)

# 📌 Funções para buscar um único registro por ID
async def get_oee_setup_by_id(db: AsyncSession, oee_id: int) -> Optional[OEESetup]:
    stmt = select(OEESetup).where(OEESetup.id == oee_id)
    return await fetch_one(db, stmt)

async def get_digest_data_by_id(db: AsyncSession, digest_id: int) -> Optional[DigestData]:
    stmt = select(DigestData).where(DigestData.id == digest_id)
    return await fetch_one(db, stmt)

async def get_planned_downtime_setup_by_id(db: AsyncSession, planned_id: int) -> Optional[PlannedDowntimeSetup]:
    stmt = select(PlannedDowntimeSetup).where(PlannedDowntimeSetup.id == planned_id)
    return await fetch_one(db, stmt)

async def get_unplanned_downtime_setup_by_id(db: AsyncSession, unplanned_id: int) -> Optional[UnplannedDowntimeSetup]:
    stmt = select(UnplannedDowntimeSetup).where(UnplannedDowntimeSetup.id == unplanned_id)
    return await fetch_one(db, stmt)

async def get_parada_by_id(db: AsyncSession, parada_id: int) -> Optional[Paradas]:
    stmt = select(Paradas).where(Paradas.id == parada_id)
    return await fetch_one(db, stmt)

async def get_planned_downtime_by_id(db: AsyncSession, planned_id: int) -> Optional[PlannedDowntime]:
    stmt = select(PlannedDowntime).where(PlannedDowntime.id == planned_id)
    return await fetch_one(db, stmt)

async def get_unplanned_downtime_by_id(db: AsyncSession, unplanned_id: int) -> Optional[UnplannedDowntime]:
    stmt = select(UnplannedDowntime).where(UnplannedDowntime.id == unplanned_id)
    return await fetch_one(db, stmt)

async def get_auto_oee_by_id(db: AsyncSession, oee_id: int) -> Optional[AutoOEE]:
    stmt = select(AutoOEE).where(AutoOEE.id == oee_id)
    return await fetch_one(db, stmt)


# 📌 Funções para buscar registros por CAMERA_NAME_ID
async def get_digest_data_by_camera_name_id(db: AsyncSession, camera_name_id: int) -> List[DigestData]:
    stmt = select(DigestData).where(DigestData.camera_name_id == camera_name_id).order_by(DigestData.id)
    return await fetch_all(db, stmt)

async def get_oee_setup_by_camera_name_id(db: AsyncSession, camera_name_id: int) -> Optional[OEESetup]:
    stmt = select(OEESetup).where(OEESetup.camera_name_id == camera_name_id)
    return await fetch_one(db, stmt)
    '''result = await fetch_all(db, stmt)

    # Caso não haja resultados, retornamos uma resposta vazia
    if result is None:
        return {"message": "Nenhum resultado encontrado"}
    
    result = result[0]  
    
    # Caso haja, retornamos os dados no formato JSON
    oee_setup_dict = {
        "id": result.id,
        "user": result.user,
        "start_shift": result.start_shift.isoformat() if result.start_shift else None,
        "stop_shift": result.stop_shift.isoformat() if result.stop_shift else None,
        "stop_time": result.stop_time,
        "line_speed": result.line_speed,  # (valor em pç/min)
        "digest_time": result.digest_time,
        "camera_name_id": result.camera_name_id,
        "timestamp": result.timestamp.isoformat() if result.timestamp else None,
    }

    return oee_setup_dict'''

async def get_planned_downtime_setup_by_camera_name_id(db: AsyncSession, camera_name_id: int) -> List[PlannedDowntimeSetup]:
    stmt = select(PlannedDowntimeSetup).where(PlannedDowntimeSetup.camera_name_id == camera_name_id)
    return await fetch_all(db, stmt)

async def get_last_digest_data_by_camera(db: AsyncSession, camera_name_id: int) -> Optional[DigestData]:
    # Último DigestData para uma câmera específica
    stmt = (
        select(DigestData)
        .where(DigestData.camera_name_id == camera_name_id)
        .order_by(desc(DigestData.stop_digest))  # Assumindo que o mais recente é pelo fim da digestão
        .limit(1)
    )
    return await fetch_one(db, stmt)

async def get_last_parada_by_camera(db: AsyncSession, camera_name_id: int) -> Optional[Paradas]:
    # Última Parada para uma câmera específica
    stmt = (
        select(Paradas)
        .where(Paradas.camera_name_id == camera_name_id)
        .order_by(desc(Paradas.stop))  # Parada mais recente pelo tempo de parada final
        .limit(1)
    )
    return await fetch_one(db, stmt)

async def get_last_auto_oee_by_camera(db: AsyncSession, camera_name_id: int) -> Optional[AutoOEE]:
    # Último AutoOEE para uma câmera específica
    stmt = (
        select(AutoOEE)
        .where(AutoOEE.camera_name_id == camera_name_id)
        .order_by(desc(AutoOEE.end))  # Registro mais recente pelo end (final do periodo de análise)
        .limit(1)
    )
    return await fetch_one(db, stmt)

async def get_auto_oee_by_period_and_camera(db: AsyncSession, inicio_pesquisa: datetime, fim_pesquisa: datetime, camera_name_id: int) -> List[AutoOEE]:
    try:
        stmt = select(AutoOEE).filter(
            AutoOEE.init >= inicio_pesquisa,
            AutoOEE.end <= fim_pesquisa,
            AutoOEE.camera_name_id == camera_name_id
        ).order_by(AutoOEE.init)  # Ordena por data de início (opcional)

        # Chama a função genérica para buscar os registros
        return await fetch_all(db, stmt)

    except Exception as e:
        print(f"Erro ao buscar AutoOEE no período: {e}")
        raise

# 📌 Funções especiais
async def get_total_planned_downtime_seconds(
    db: AsyncSession,
    inicio: datetime,
    fim: datetime,
    camera_name_id: int
) -> float:
    stmt = (
        select(
            func.sum(func.extract('epoch', Paradas.stop) - func.extract('epoch', Paradas.start))
        )
        .join(PlannedDowntime, PlannedDowntime.paradas_id == Paradas.id)
        .where(
            Paradas.start >= inicio,
            Paradas.stop <= fim,
            Paradas.camera_name_id == camera_name_id
        )
    )

    total_seconds = await fetch_one(db, stmt)
    return total_seconds or 0.0

async def get_total_unplanned_downtime_seconds(
    db: AsyncSession,
    inicio: datetime,
    fim: datetime,
    camera_name_id: int
) -> float:
    stmt = (
        select(
            func.sum(func.extract('epoch', Paradas.stop) - func.extract('epoch', Paradas.start))
        )
        .join(UnplannedDowntime, UnplannedDowntime.paradas_id == Paradas.id)
        .where(
            Paradas.start >= inicio,
            Paradas.stop <= fim,
            Paradas.camera_name_id == camera_name_id
        )
    )

    total_seconds = await fetch_one(db, stmt)
    return total_seconds or 0.0


async def get_total_ok_nok_from_digest(
    db: AsyncSession,
    inicio: datetime,
    fim: datetime,
    camera_name_id: int
) -> dict:
    stmt = (
        select(
            func.sum(DigestData.ok).label("total_ok"),
            func.sum(DigestData.nok).label("total_nok")
        )
        .where(
            DigestData.start_digest >= inicio,
            DigestData.stop_digest <= fim,
            DigestData.camera_name_id == camera_name_id
        )
    )

    result = await db.execute(stmt)
    total_ok, total_nok = result.one_or_none() or (0, 0)

    return {
        "total_ok": total_ok or 0,
        "total_nok": total_nok or 0
    }

async def get_total_ok_nok_discretized_by_period(
    db: AsyncSession,
    inicio: datetime,
    fim: datetime,
    camera_name_id: int,
    period: timedelta
) -> List[Dict[str, int]]:
    """
    Calcula a produção de peças OK e NOK discretizada por um período (P) dentro de um intervalo de tempo.
    
    :param db: Sessão de banco de dados assíncrona.
    :param inicio: Data e hora de início do intervalo.
    :param fim: Data e hora de fim do intervalo.
    :param camera_name_id: ID da câmera para filtrar.
    :param period: O período de discretização (ex: timedelta(hours=1) para 1 hora).
    :return: Lista de dicionários com os totais de OK e NOK por intervalo de tempo.

    Exemplo de retorno
    [
        {"start": datetime(2023, 4, 12, 8, 0, 0), "end": datetime(2023, 4, 12, 9, 0, 0), "total_ok": 120, "total_nok": 5},
        {"start": datetime(2023, 4, 12, 9, 0, 0), "end": datetime(2023, 4, 12, 10, 0, 0), "total_ok": 130, "total_nok": 3},
        {"start": datetime(2023, 4, 12, 10, 0, 0), "end": datetime(2023, 4, 12, 11, 0, 0), "total_ok": 125, "total_nok": 7},
        ...
    ]

    """
    
    # Criar uma lista de intervalos de tempo com base no período (P)
    intervals = []
    current_start = inicio
    while current_start < fim:
        current_end = current_start + period
        if current_end > fim:
            current_end = fim  # Ajustar para o final do intervalo, se necessário
        intervals.append((current_start, current_end))
        current_start = current_end
    
    # Lista para armazenar os resultados
    results = []

    # Iterar sobre os intervalos e calcular a produção de OK e NOK
    for start, end in intervals:
        stmt = (
            select(
                func.sum(DigestData.ok).label("total_ok"),
                func.sum(DigestData.nok).label("total_nok")
            )
            .where(
                DigestData.start_digest >= start,
                DigestData.stop_digest <= end,
                DigestData.camera_name_id == camera_name_id
            )
        )
        
        result = await db.execute(stmt)
        total_ok, total_nok = result.one_or_none() or (0, 0)

        
        
        results.append({
            "start": start,
            "end": end,
            "total_ok": total_ok,
            "total_nok": total_nok
        })
    
    return results


async def get_digest_data_filtered_by_stop_and_cameraId(db: AsyncSession, fim: datetime, camera_name_id: int) -> List[DigestData]:
    stmt = select(DigestData).where(
        DigestData.stop_digest >= fim,
        DigestData.camera_name_id == camera_name_id
        ).order_by(DigestData.id)
    return await fetch_all(db, stmt)


async def get_planned_downtime_filtered_by_init_end_cameraId(
    db: AsyncSession,
    inicio: datetime,
    fim: datetime,
    camera_name_id: int
) -> List[PlannedDowntime]:
    stmt = (
        select(PlannedDowntime)
        .join(Paradas, PlannedDowntime.paradas_id == Paradas.id)
        .where(
            Paradas.start <= fim,
            Paradas.stop >= inicio,
            Paradas.camera_name_id == camera_name_id
        )
    )

    result = await fetch_all(db, stmt)

    return result

async def get_paradas_com_tipo(
    db: AsyncSession,
    inicio: datetime,
    fim: datetime,
    camera_name_id: int
) -> List[dict]:
    # Buscar todas as paradas no intervalo e com a câmera
    result = await db.execute(
        select(Paradas)
        .where(
            and_(
                Paradas.start >= inicio,
                Paradas.stop <= fim,
                Paradas.camera_name_id == camera_name_id
            )
        )
    )
    paradas = result.scalars().all()

    response = []
    cont_paradas = 0
    label_sem_obs = "Sem Observação"

    for parada in paradas:
        cont_paradas += 1
        
        # Tenta buscar como planejada
        planned = await db.execute(
            select(PlannedDowntime, PlannedDowntimeSetup)
            .join(PlannedDowntimeSetup, PlannedDowntime.planned_downtime_id == PlannedDowntimeSetup.id)
            .where(PlannedDowntime.paradas_id == parada.id)
        )
        planned_row = planned.first()

        if planned_row:
            planned_obj, setup = planned_row
            response.append({
                "id": {cont_paradas},
                "startTime": parada.start,
                "endTime": parada.stop,
                "paradaType": "planejada",
                "paradaID": parada.id,
                "paradaSetupID": setup.id,
                "paradaName": setup.name,
                "obs": planned_obj.observacoes or label_sem_obs
            })
            continue

        # Tenta buscar como não planejada
        unplanned = await db.execute(
            select(UnplannedDowntime, UnplannedDowntimeSetup)
            .join(UnplannedDowntimeSetup, UnplannedDowntime.unplanned_downtime_id == UnplannedDowntimeSetup.id)
            .where(UnplannedDowntime.paradas_id == parada.id)
        )
        unplanned_row = unplanned.first()

        if unplanned_row:
            unplanned_obj, setup = unplanned_row
            response.append({
                "id": {cont_paradas},
                "startTime": parada.start,
                "endTime": parada.stop,
                "paradaType": "naoPlanejada",
                "paradaID": parada.id,
                "paradaSetupID": setup.id,
                "paradaName": setup.name,
                "obs": unplanned_obj.observacoes or label_sem_obs
            })
            continue

        # Caso não tenha justificativa
        response.append({
            "id": {cont_paradas},
            "startTime": parada.start,
            "endTime": parada.stop,
            "paradaType": "naoJustificada",
            "paradaID": parada.id,
            "paradaSetupID": -1,
            "paradaName": "Não justificada",
            "obs": label_sem_obs
        })

        

    return response