from datetime import datetime, timedelta
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from database.db import get_db
import database.crud as crud
from utils import timedelta_to_iso


async def oee_by_period(
                        inicio: datetime, 
                        fim: datetime, 
                        camera_name_id: int, 
                        velocidade_da_linha: float, 
                        db: AsyncSession = Depends(get_db)
                        ) -> Dict:
    """
    Calcula os indicadores de OEE (Overall Equipment Effectiveness) em um período definido.

    A função realiza o cálculo dos três principais pilares do OEE: disponibilidade, desempenho e qualidade.
    Esses dados são obtidos a partir de informações no banco de dados relacionadas ao tempo de operação da linha,
    paradas planejadas e não planejadas, produção total e defeitos.

    Args:
        inicio (datetime): Data e hora de início do período de análise.
        fim (datetime): Data e hora de fim do período de análise.
        camera_name_id (int): ID da câmera ou linha de produção a ser analisada.
        velocidade_da_linha (float): Velocidade teórica da linha de produção em peças por minuto.
        db (AsyncSession, optional): Sessão assíncrona com o banco de dados, injetada via dependência FastAPI.

    Returns:
        Dict: Um dicionário contendo os seguintes dados:
            - A_Inicio: Início do período.
            - A_Fim: Fim do período.
            - B_Tempo_total_disponivel: Tempo total disponível (fim - início).
            - C_Paradas_planejadas: Tempo total de paradas planejadas.
            - D_Tempo_disponivel_liquido: Tempo disponível líquido (B - C).
            - E_Paradas_nao_planejadas: Tempo de paradas não planejadas.
            - F_Tempo_operando: Tempo efetivamente operando (D - E).
            - G_Relacao_disponibilidade: Percentual de disponibilidade (F / D).
            - H_Total_pecas_produzidas: Quantidade total de peças produzidas (boas e ruins).
            - I_Tempo_ideal_ciclo: Taxa ideal de produção (peças/minuto).
            - J_Max_pecas_possiveis: Quantidade máxima de peças possíveis (F * I).
            - K_Relacao_desempenho: Percentual de desempenho (H / J).
            - L_Total_pecas_defeituosas: Quantidade total de peças defeituosas.
            - M_Relacao_qualidade: Percentual de qualidade ((H - L) / H).
            - oee: Valor percentual do OEE calculado (G * K * M).
    """
    # B. Tempo de produção (Total de Tempo Disponível)
    total_available_time = fim - inicio

    # C. Paradas planejadas
    #total_planned_downtime = timedelta(hours=0, minutes=0, seconds=0)
    total_planned_downtime_seconds = await crud.get_total_planned_downtime_seconds(db=db, inicio=inicio, fim=fim, camera_name_id=camera_name_id)
    total_planned_downtime = timedelta(seconds=int(total_planned_downtime_seconds))
    
    # D. Tempo disponícel líquido (B - C)
    tempo_disponivel_liquido = total_available_time - total_planned_downtime

    # E. Paradas não planejadas + não justificadas
    #total_unplanned_downtime = timedelta(hours=0, minutes=0, seconds=0)
    total_unplanned_downtime_seconds = await crud.get_total_unplanned_downtime_seconds(db=db, inicio=inicio, fim=fim, camera_name_id=camera_name_id)
    total_unplanned_downtime = timedelta(seconds=int(total_unplanned_downtime_seconds))
    
    total_nonjustified_downtime_seconds = await crud.get_total_nonjustified_downtime_seconds(db=db, inicio=inicio, fim=fim, camera_name_id=camera_name_id)
    total_nonjustified_downtime = timedelta(seconds=int(total_nonjustified_downtime_seconds))
    
    total_paradas_nao_planejadas_ou_nao_justificadas = total_unplanned_downtime + total_nonjustified_downtime

    # F. Tempo operando (Tempo disponível - Paradas não planejadas) (D - E)
    operating_time = tempo_disponivel_liquido - total_paradas_nao_planejadas_ou_nao_justificadas

    # G. Relação de disponibilidade (F / D)
    availability_ratio = operating_time.total_seconds() / tempo_disponivel_liquido.total_seconds() if tempo_disponivel_liquido.total_seconds() > 0 else 0
    #print('availability_ratio', availability_ratio)

    # H. Número total de peças produzidas (boas e ruins)
    production = await crud.get_total_ok_nok_from_digest(db=db, inicio=inicio, fim=fim, camera_name_id=camera_name_id)
    total_produced_pieces = production["total_ok"] + production["total_nok"]

    # I. Tempo ideal de ciclo (valor em pç/min)
    ideal_cycle_time = velocidade_da_linha

    # J. Número máximo de peças que podem ser produzidas (Tempo operando * Tempo ideal de ciclo) (I x F)
    max_pieces = (operating_time.total_seconds() / 60) * ideal_cycle_time

    # K. Relação de desempenho (Desempenho = Peças Produzidas / Máximo de Peças) (H / J)
    performance_ratio = total_produced_pieces / max_pieces if max_pieces > 0 else 0

    # L. Total de peças defeituosas
    total_defective_pieces = production["total_nok"]

    # M. Relação de qualidade (Qualidade = (Peças boas - Defeituosas) / Peças boas) (H - L / H)
    quality_ratio = (total_produced_pieces - total_defective_pieces) / total_produced_pieces if total_produced_pieces > 0 else 0
    #print('quality_ratio', quality_ratio)

    # OEE
    oee = availability_ratio * performance_ratio * quality_ratio


    # Retornando os resultados no formato JSON
    return {
        "A_Inicio": inicio,
        "A_Fim": fim,
        "B_Tempo_total_disponivel": timedelta_to_iso(total_available_time),
        "C_Paradas_planejadas": timedelta_to_iso(total_planned_downtime),
        "D_Tempo_disponivel_liquido(B-C)": timedelta_to_iso(tempo_disponivel_liquido),
        "E_Paradas_nao_planejadas": timedelta_to_iso(total_paradas_nao_planejadas_ou_nao_justificadas),
        "F_Tempo_operando(D-E)": timedelta_to_iso(operating_time),
        "G_Relacao_disponibilidade(F/D)": round(availability_ratio * 100, 2),
        
        "H_Total_pecas_produzidas": total_produced_pieces,
        "I_Tempo_ideal_ciclo": ideal_cycle_time,
        "J_Max_pecas_possiveis(IxF)": max_pieces,
        "K_Relacao_desempenho(H/J)": round(performance_ratio * 100, 2),
        
        "L_Total_pecas_defeituosas": total_defective_pieces,
        "M_Relacao_qualidade(H-(L/H))": round(quality_ratio * 100, 2),

        "oee(GxKxM)": round(oee * 100, 2)
    }

