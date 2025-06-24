from datetime import datetime, timedelta

from sqlalchemy import text
from .external_database_connection import ExternalDatabaseConnection
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from database.db.conexao_db_externo import get_external_db

external_db = ExternalDatabaseConnection()

#START_ANALISE="'2025-03-13 08:00:00'",
#STOP_ANALISE = "'2025-04-01 13:00:00'"

async def fetch_paradas(db: AsyncSession, PARADA_TIME_STOP = 60):
    """
    Identifica intervalos de parada em registros da tabela `data_received`.

    Agrupa os registros por lote e câmera, calcula o tempo entre timestamps consecutivos,
    e retorna os intervalos que excedem 60 segundos (paradas significativas).

    Returns:
        list[dict]: Lista de dicionários com os seguintes campos:
            - startTime (datetime): Timestamp anterior (início da parada).
            - stopTime (datetime): Timestamp atual (fim da parada).
            - lote_id (str): Identificador do lote.
            - camera_name_id (str): Identificador da câmera.
            - intervalo (float): Duração da parada em segundos.
    """

    # Certifique-se que PARADA_TIME_STOP está em segundos como float/int
    if isinstance(PARADA_TIME_STOP, timedelta):
        PARADA_TIME_STOP = PARADA_TIME_STOP.total_seconds()

    query_parada = text("""
        WITH ordered_data AS (
            SELECT 
                "timestamp", 
                "camera_name_id", 
                LAG("timestamp") OVER (
                    PARTITION BY "camera_name_id" 
                    ORDER BY "timestamp"
                ) AS prev_timestamp
            FROM "data_received"
        )
        SELECT 
            prev_timestamp AS startTime,
            "timestamp" AS stopTime,
            "camera_name_id",
            EXTRACT(EPOCH FROM ("timestamp" - prev_timestamp)) AS intervalo
        FROM ordered_data
        WHERE EXTRACT(EPOCH FROM ("timestamp" - prev_timestamp)) > :parada_time_stop;
    """)

    #resultado = external_db.execute_query(query_parada, {'parada_time_stop': PARADA_TIME_STOP})
    
    try:
        result = await db.execute(query_parada, {
            "parada_time_stop": PARADA_TIME_STOP
        })

        paradas = result.fetchall()
        return paradas

    except Exception as e:
        print("❌ Erro ao executar query de paradas:", str(e))
        raise e

    #return resultado


async def fetch_paradas_after_init_date(db: AsyncSession, INIT='2025-06-09 15:00:00', PARADA_TIME_STOP=60):
    """
    Identifica intervalos de parada em registros da tabela `data_received`.

    Filtra os dados por lote e câmera, considerando apenas os registros posteriores
    à data especificada (`INIT`). Em seguida, calcula o tempo entre registros consecutivos
    por grupo (lote + câmera) e retorna apenas os intervalos que excedem o tempo limite
    definido por `PARADA_TIME_STOP` (em segundos).

    Args:
        INIT (str): Data e hora inicial no formato 'YYYY-MM-DD HH:MM:SS'. 
            Apenas registros após esse timestamp serão considerados.
        PARADA_TIME_STOP (int): Tempo mínimo (em segundos) para considerar que houve uma parada.

    Returns:
        list[dict]: Lista de dicionários contendo os seguintes campos:
            - startTime (datetime): Timestamp anterior (início da parada).
            - stopTime (datetime): Timestamp atual (fim da parada).
            - camera_name_id (str): Identificador da câmera.
            - intervalo (float): Duração da parada em segundos.
    """
    
    '''query_parada_antiga_com_loteID = text("""
    WITH ordered_data AS (
        SELECT 
            "timestamp", 
            "lote_id", 
            "camera_name_id", 
            LAG("timestamp") OVER (
                PARTITION BY "lote_id", "camera_name_id" 
                ORDER BY "timestamp"
            ) AS prev_timestamp
        FROM "data_received"
        WHERE "timestamp" > :init_date
    )
    SELECT 
        prev_timestamp AS startTime,
        "timestamp" AS stopTime,
        "lote_id", 
        "camera_name_id",
        EXTRACT(EPOCH FROM ("timestamp" - prev_timestamp)) AS intervalo
    FROM ordered_data
    WHERE EXTRACT(EPOCH FROM ("timestamp" - prev_timestamp)) > :parada_time_stop;
    """)'''

    # Certifique-se que INIT está no formato datetime, se necessário
    if isinstance(INIT, str):
        INIT = datetime.strptime(INIT, '%Y-%m-%d %H:%M:%S')

    # Certifique-se que PARADA_TIME_STOP está em segundos como float/int
    if isinstance(PARADA_TIME_STOP, timedelta):
        PARADA_TIME_STOP = PARADA_TIME_STOP.total_seconds()

    query_parada = text("""
    WITH ordered_data AS (
        SELECT 
            "timestamp",  
            "camera_name_id", 
            LAG("timestamp") OVER (
                PARTITION BY "camera_name_id" 
                ORDER BY "timestamp"
            ) AS prev_timestamp
        FROM "data_received"
        WHERE "timestamp" > :init_date
    )
    SELECT 
        prev_timestamp AS startTime,
        "timestamp" AS stopTime,
        "camera_name_id",
        EXTRACT(EPOCH FROM ("timestamp" - prev_timestamp)) AS intervalo
    FROM ordered_data
    WHERE EXTRACT(EPOCH FROM ("timestamp" - prev_timestamp)) > :parada_time_stop;
    """)

    #resultado = external_db.execute_query(query_parada, {
    #    'init_date': INIT,
    #    'parada_time_stop': PARADA_TIME_STOP
    #})
    try:
        result = await db.execute(query_parada, {
            "init_date": INIT,
            "parada_time_stop": PARADA_TIME_STOP
        })

        paradas = result.fetchall()
        return paradas

    except Exception as e:
        print("❌ Erro ao executar query de paradas:", str(e))
        raise e

    #return resultado



async def fetch_digest_data_from_datareceived(
                                            db: AsyncSession,
                                            CAMERA_NAME_ID, 
                                            DIGEST_TIME, 
                                            START_ANALISE="'2025-03-13 08:00:00'",
                                            STOP_ANALISE = datetime.now()#"'2025-04-1 13:00:00'",                                            
                                            ):
    print(f'Fetch Digest data from data_received from camera {CAMERA_NAME_ID} and Period {START_ANALISE} to {STOP_ANALISE}')

    # Convertendo as strings de data para objetos datetime
    #start_time = datetime.datetime.strptime(START_ANALISE.strip("'"), "%Y-%m-%d %H:%M:%S")
    #stop_time = datetime.datetime.strptime(STOP_ANALISE.strip("'"), "%Y-%m-%d %H:%M:%S")
    if isinstance(START_ANALISE, str):
        start_time = datetime.strptime(START_ANALISE.strip("'"), "%Y-%m-%d %H:%M:%S")
    else:
        start_time = START_ANALISE

    if isinstance(STOP_ANALISE, str):
        stop_time = datetime.strptime(STOP_ANALISE.strip("'"), "%Y-%m-%d %H:%M:%S")
    else:
        stop_time = STOP_ANALISE

    
    # Convertendo o tempo de digest para um intervalo de tempo (timedelta)
    digest_delta = timedelta(seconds=DIGEST_TIME)
    
    # Inicializando o tempo atual com o tempo de início
    current_time = start_time
    #proxima_pesquisa = start_time

    resultados = []
    batch = 100    # limita a quantidade de linhas enviadas, no caso de longos periodos 

    while current_time < stop_time:
        # Formatar o intervalo de tempo como uma string no formato necessário
        #formatted_start_time = f"'{current_time.strftime('%Y-%m-%d %H:%M:%S')}'"
        #formatted_end_time = f"'{(current_time + digest_delta).strftime('%Y-%m-%d %H:%M:%S')}'"
        
        # Criando a consulta com o intervalo de tempo atualizado
        query_digest = text("""
        SELECT "lote_id", "camera_name_id", 
            COUNT(CASE WHEN "ok_nok" = 1 THEN 1 END) AS total_ok,
            COUNT(CASE WHEN "ok_nok" = 0 THEN 1 END) AS total_nok,
            MAX("timestamp") AS last_timestamp
        FROM "data_received"
        WHERE "timestamp" > :start_time AND "timestamp" <= :end_time AND "camera_name_id" = :camera_name_id
        GROUP BY "lote_id", "camera_name_id";
        """)

        
        # Aqui você pode adicionar a lógica para executar a consulta `query_digest`
        #print("query_digest", query_digest)  # Para visualizar a query gerada (remover ou ajustar conforme necessário)

        try:
            # Executando a consulta (substitua 'external_db.execute_query' pela função real de execução)
            #resultado = external_db.execute_query(query_digest)
            resultado = await db.execute(
            query_digest,
            {
                "start_time": current_time, #proxima_pesquisa, #
                "end_time": current_time + digest_delta,
                "camera_name_id": CAMERA_NAME_ID
            }
            )
            resultado = resultado.fetchall()
        except Exception as e:
            print("❌ Erro ao executar query no fetch digest:", str(e))
            raise e
        
        # Armazenando o resultado na lista
        if resultado:
            if len(resultado[0]) >= 5:
                last_timestamp = resultado[0][4]
                resultado.append(current_time)
                resultado.append(current_time + digest_delta)
                resultados.append(resultado)

                batch -= 1
                tempo_que_falta = stop_time - (current_time + digest_delta)
                if batch <= 0 or tempo_que_falta < digest_delta:
                    return resultados

                if last_timestamp > current_time:
                    current_time = last_timestamp
                else:
                    current_time += digest_delta
            else:
                print("⚠️ Resultado inesperado: menos de 5 colunas retornadas:", resultado[0])
                current_time += digest_delta
        else:
            current_time += digest_delta
        
        # Avançar o tempo para a próxima iteração
        #current_time = last_timestamp

    return resultados


async def fetch_all_digest_data_from_datareceived(
    db: AsyncSession,
    CAMERA_NAME_ID, 
    DIGEST_TIME
    ):
    # Consulta para pegar o intervalo total de tempo no banco externo
    print(f'Fetch ALL Digest data from data_received from camera {CAMERA_NAME_ID} and Period {DIGEST_TIME}')
    
    query_limits = text("""
    SELECT MIN("timestamp") AS min_time, MAX("timestamp") AS max_time FROM "data_received";
    """)
    #limits_result = external_db.execute_query(query_limits)
    resultado = await db.execute(query_limits)
    limits_result = resultado.fetchone()
    print("limits_result", limits_result)
    start_time, stop_time = limits_result
    
    if not start_time or not stop_time:
        print("Não foi possível obter o intervalo de tempo do banco externo.")
        return []
    
    # Convertendo o tempo de digest para um intervalo de tempo (timedelta)
    digest_delta = timedelta(seconds=DIGEST_TIME)
    current_time = start_time

    resultados = []
    batch = 1    # limita a quantidade de linhas enviadas, no caso de longos periodos

    while current_time < stop_time:
        formatted_start_time = f"'{current_time.strftime('%Y-%m-%d %H:%M:%S')}'"
        formatted_end_time = f"'{(current_time + digest_delta).strftime('%Y-%m-%d %H:%M:%S')}'"
        
        query_digest = text("""
            SELECT "lote_id", "camera_name_id", 
                COUNT(CASE WHEN "ok_nok" = 1 THEN 1 END) AS total_ok,
                COUNT(CASE WHEN "ok_nok" = 0 THEN 1 END) AS total_nok,
                MAX("timestamp") AS last_timestamp
            FROM "data_received"
            WHERE "timestamp" BETWEEN :start_time AND :end_time AND "camera_name_id" = :camera_name_id
            GROUP BY "lote_id", "camera_name_id";
        """)

        resultado = await db.execute(
            query_digest,
            {
                "start_time": current_time,
                "end_time": current_time + digest_delta,
                "camera_name_id": CAMERA_NAME_ID
            }
        )
        resultado = resultado.fetchall()
        #print("query", formatted_start_time, formatted_end_time)
        #print("*****resultado", resultado)
        #print("camera id", CAMERA_NAME_ID)

        '''if resultado:
            resultado.append(formatted_start_time)
            resultado.append(formatted_end_time)
            resultados.append(resultado)
            #print('com resultado', resultado)
            batch -= 1
            if batch <= 0:
                return resultados
        else:
            pass
            print("sem resultado", resultado)
        
        current_time += digest_delta'''
        if resultado:
            if len(resultado[0]) >= 5:
                last_timestamp = resultado[0][4]
                resultado.append(current_time)
                resultado.append(current_time + digest_delta)
                resultados.append(resultado)

                batch -= 1
                tempo_que_falta = stop_time - (current_time + digest_delta)
                if batch <= 0 or tempo_que_falta < digest_delta:
                    return resultados

                if last_timestamp > current_time:
                    current_time = last_timestamp
                else:
                    current_time += digest_delta
            else:
                print("⚠️ Resultado inesperado: menos de 5 colunas retornadas:", resultado[0])
                current_time += digest_delta
        else:
            current_time += digest_delta

    return resultados




async def get_last_timestamp_from_dataReceived_by_camera_id(  
                                                            db: AsyncSession,                                                          
                                                            CAMERA_NAME_ID: int
                                                            ):
    """ 
        Construindo a query para buscar o último timestamp da câmera fornecida
    """

    query = text("""
    SELECT "timestamp" 
    FROM "data_received"
    WHERE "camera_name_id" = :camera_name_id
    ORDER BY "timestamp" DESC
    LIMIT 1;
    """)

    try:
        # Executando a query
        #resultado = external_db.execute_query(query)
        resultado = await db.execute(
            query,
            {
                "camera_name_id": CAMERA_NAME_ID
            }
        )
        resultado = resultado.fetchall()
        print("último timestamp da câmera fornecida", resultado)
        # Verificando e retornando o resultado
        if resultado:
            return resultado[0][0]
        else:
            print(f"Nenhum timestamp encontrado para a câmera {CAMERA_NAME_ID}")
            return None
    except Exception as e:
        print(f"Erro ao buscar último data_received: {e}")






def fetch_paradas_copy():
    PARADA_TIME_STOP = 60
    query_parada = text("""WITH ordered_data AS ( 
                        SELECT 
                            "timestamp", 
                            "lote_id", 
                            "camera_name_id", 
                            LAG("timestamp") OVER (
                                PARTITION BY "lote_id", "camera_name_id" 
                                ORDER BY "timestamp") AS prev_timestamp 
                            FROM "data_received") 
                        SELECT 
                            prev_timestamp AS startTime, 
                            "timestamp" AS stopTime, 
                            "lote_id", 
                            "camera_name_id", 
                            EXTRACT(EPOCH FROM ("timestamp" - prev_timestamp)) AS intervalo 
                        FROM ordered_data 
                        WHERE EXTRACT(EPOCH FROM ("timestamp" - prev_timestamp)) > {PARADA_TIME_STOP};
                        """)
    resultado = external_db.execute_query(query_parada)
    print('resultado yy', resultado)
    return resultado

def fetch_paradas_after_init_date_copy(INIT = '2024-12-01 00:00:00', PARADA_TIME_STOP = 60):
    """ Identifica paradas no data_received filtrado por câmera e Lote, 
        considerando apenas registros após uma data inicial (INIT). 
        Retorna os intervalos de tempo entre registros consecutivos 
        que excedem um tempo limite (PARADA_TIME_STOP).
    """
    query_parada = text("""
    WITH ordered_data AS (
        SELECT 
            "timestamp", 
            "lote_id", 
            "camera_name_id", 
            LAG("timestamp") OVER (
                PARTITION BY "lote_id", "camera_name_id" 
                ORDER BY "timestamp"
            ) AS prev_timestamp
        FROM "data_received"
        WHERE "timestamp" > '{INIT}'
    )
    SELECT 
        prev_timestamp AS startTime,
        "timestamp" AS stopTime,
        "lote_id", 
        "camera_name_id",
        EXTRACT(EPOCH FROM ("timestamp" - prev_timestamp)) AS intervalo
    FROM ordered_data
    WHERE EXTRACT(EPOCH FROM ("timestamp" - prev_timestamp)) > {PARADA_TIME_STOP};
    """)

    resultado = external_db.execute_query(query_parada)
    return resultado