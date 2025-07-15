from datetime import datetime, timedelta
import json
import logging
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from typing import Dict, List, Optional


from database.models import (
    OEESetup, DigestData,
    PlannedDowntimeSetup, UnplannedDowntimeSetup, Paradas,
    PlannedDowntime, UnplannedDowntime, AutoOEE
)

# Logger específico
logger = logging.getLogger(__name__)

# 📌 Função genérica para executar consultas (assíncrona)
async def fetch_all(db: AsyncSession, stmt):
    try:
        result = await db.execute(stmt)  # Execução assíncrona
        return result.scalars().all()  # Obtém todos os resultados
    except SQLAlchemyError as e:
        logger.exception(f"Erro ao buscar registros: {e}")
        raise

async def fetch_one(db: AsyncSession, stmt):
    try:
        result = await db.execute(stmt)  # Execução assíncrona
        return result.scalar_one_or_none()  # Obtém um único registro ou None
    except SQLAlchemyError as e:
        logger.exception(f"Erro ao buscar registro: {e}")
        raise

async def fetch_all_rows(db: AsyncSession, stmt):
    """ Para selects com múltiplas colunas (e.g., JOIN, funções agregadas), 
        use .all() ao invés de .scalars().all().
    """
    try:
        result = await db.execute(stmt)
        return result.all()  # Retorna todas as linhas como tuplas
    except SQLAlchemyError as e:
        logger.exception(f"Erro ao buscar registros: {e}")
        raise


# 📌 Funções especiais
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
        logger.exception(f"Erro ao buscar AutoOEE no período: {e}")
        raise


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

async def get_total_nonjustified_downtime_seconds(
    db: AsyncSession,
    inicio: datetime,
    fim: datetime,
    camera_name_id: int
) -> float:
    # Subquery para obter os IDs das paradas que têm vínculo com PlannedDowntime ou UnplannedDowntime
    subquery = (
        select(Paradas.id)
        .join(PlannedDowntime, PlannedDowntime.paradas_id == Paradas.id, isouter=True)
        .join(UnplannedDowntime, UnplannedDowntime.paradas_id == Paradas.id, isouter=True)
        .where(
            Paradas.start >= inicio,
            Paradas.stop <= fim,
            Paradas.camera_name_id == camera_name_id,
            (PlannedDowntime.paradas_id.isnot(None) | UnplannedDowntime.paradas_id.isnot(None))  # Exclui paradas sem downtime
        )
    )

    # Consulta principal que seleciona as paradas que não estão na subconsulta (não justificadas)
    stmt = (
        select(
            func.sum(func.extract('epoch', Paradas.stop) - func.extract('epoch', Paradas.start))
        )
        .where(
            Paradas.id.notin_(subquery),   # Exclui as paradas justificadas (com downtime)
            Paradas.start >= inicio,       # Filtra paradas dentro do intervalo de tempo
            Paradas.stop <= fim,           # Filtra paradas dentro do intervalo de tempo
            Paradas.camera_name_id == camera_name_id  # Filtra pelo tipo de câmera
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

async def get_total_ok_nok_grouped_by_rows(
    db: AsyncSession,
    inicio: datetime,
    fim: datetime,
    camera_name_id: int,
    group_size: int 
) -> List[Dict[str, int]]:
    """
    Agrupa registros consecutivos de DigestData por N linhas (ex: 2 ou 3) e calcula total de OK/NOK por grupo.
    """

    # Buscar todos os registros ordenados por tempo dentro do intervalo
    stmt = (
        select(DigestData)
        .where(
            DigestData.start_digest >= inicio,
            DigestData.stop_digest <= fim,
            DigestData.camera_name_id == camera_name_id
        )
        .order_by(DigestData.start_digest)
    )

    result = await db.execute(stmt)
    rows = result.scalars().all()

    results = []

    # Agrupar os registros em blocos de N (ex: 2 ou 3 linhas consecutivas)
    for i in range(0, len(rows), group_size):
        group = rows[i:i+group_size]

        if not group:
            continue

        total_ok = sum(r.ok for r in group)
        total_nok = sum(r.nok for r in group)
        start = group[0].start_digest
        end = group[-1].stop_digest

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

async def get_digest_data_filtered_by_period_and_cameraId(db: AsyncSession, inicio: datetime, fim: datetime, camera_name_id: int) -> List[DigestData]:
    stmt = select(DigestData).where(
        DigestData.start_digest >= inicio,
        DigestData.stop_digest <= fim,
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
                "plannedOrUnplannedID": planned_obj.id,
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
                "plannedOrUnplannedID": unplanned_obj.id,
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
            "plannedOrUnplannedID": -1,
            "obs": label_sem_obs
        })

        

    return response

async def get_resumo_paradas_by_period(
    db: AsyncSession,
    inicio: datetime,
    fim: datetime,
    camera_name_id: int
) -> Dict[str, float]:
    """
    Retorna a duração total (em minutos) das paradas planejadas, não planejadas e não justificadas
    para uma determinada linha de produção em um intervalo de tempo.

    A função consulta o banco de dados para obter os registros de paradas que ocorreram entre as datas
    fornecidas e classifica a duração de cada parada de acordo com seu tipo: planejada, não planejada ou
    não justificada (quando não pertence a nenhuma das categorias anteriores).

    Args:
        db (AsyncSession): Sessão assíncrona com o banco de dados.
        inicio (datetime): Data e hora de início do período de análise.
        fim (datetime): Data e hora de fim do período de análise.
        camera_name_id (int): ID da câmera ou linha de produção a ser analisada.

    Returns:
        Dict[str, float]: Um dicionário com a duração total (em minutos) de cada tipo de parada:
            - "planejadas": Paradas previamente agendadas.
            - "nao_planejadas": Paradas não previstas.
            - "nao_justificadas": Paradas sem categoria atribuída.
    """
    stmt = (
        select(Paradas)
        .where(
            and_(
                Paradas.start >= inicio,
                Paradas.stop <= fim,
                Paradas.camera_name_id == camera_name_id
            )
        )
    )

    result = await db.execute(stmt)
    paradas = result.scalars().all()

    planejadas = 0.0
    nao_planejadas = 0.0
    nao_justificadas = 0.0

    for parada in paradas:
        duracao_min = (parada.stop - parada.start).total_seconds() / 60

        # Verifique se a parada está relacionada a uma parada planejada
        planned = await db.execute(
            select(PlannedDowntime)
            .where(PlannedDowntime.paradas_id == parada.id)
        )
        planned_result = planned.scalars().first()

        # Verifique se a parada está relacionada a uma parada não planejada
        unplanned = await db.execute(
            select(UnplannedDowntime)
            .where(UnplannedDowntime.paradas_id == parada.id)
        )
        unplanned_result = unplanned.scalars().first()

        if planned_result:
            # Se houver uma parada planejada, classifique como planejada
            planejadas += duracao_min
        elif unplanned_result:
            # Se houver uma parada não planejada, classifique como não planejada
            nao_planejadas += duracao_min
        else:
            # Caso contrário, classifique como não justificada
            nao_justificadas += duracao_min

    return {
        "planejadas": round(planejadas, 2),
        "nao_planejadas": round(nao_planejadas, 2),
        "nao_justificadas": round(nao_justificadas, 2)
    }


    '''stmt = (
        select(Paradas)
        .options(
            joinedload(Paradas.planned),
            joinedload(Paradas.unplanned)
        )
        .where(
            and_(
                Paradas.start >= inicio,
                Paradas.stop <= fim,
                Paradas.camera_name_id == camera_name_id
            )
        )
    )

    result = await db.execute(stmt)
    paradas = result.scalars().all()

    planejadas = 0.0
    nao_planejadas = 0.0
    nao_justificadas = 0.0

    for parada in paradas:
        duracao_min = (parada.stop - parada.start).total_seconds() / 60

        if parada.planned:
            planejadas += duracao_min
        elif parada.unplanned:
            nao_planejadas += duracao_min
        else:
            nao_justificadas += duracao_min

    return {
        "planejadas": round(planejadas, 2),
        "nao_planejadas": round(nao_planejadas, 2),
        "nao_justificadas": round(nao_justificadas, 2)
    }'''

