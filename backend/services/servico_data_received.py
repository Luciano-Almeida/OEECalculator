import datetime

from sqlalchemy import text
from .external_database_connection import ExternalDatabaseConnection
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from database.db.conexao_db_externo import get_external_db

external_db = ExternalDatabaseConnection()

#START_ANALISE="'2025-03-13 08:00:00'",
#STOP_ANALISE = "'2025-04-01 13:00:00'"

def fetch_paradas():
    PARADA_TIME_STOP = 60
    query_parada = f'WITH ordered_data AS ( SELECT "TimeStamp", "LoteId", "CameraId", LAG("TimeStamp") OVER (PARTITION BY "LoteId", "CameraId" ORDER BY "TimeStamp") AS prev_timestamp FROM "DataReceived") SELECT prev_timestamp AS startTime, "TimeStamp" AS stopTime, "LoteId", "CameraId", EXTRACT(EPOCH FROM ("TimeStamp" - prev_timestamp)) AS intervalo FROM ordered_data WHERE EXTRACT(EPOCH FROM ("TimeStamp" - prev_timestamp)) > {PARADA_TIME_STOP};'
    resultado = external_db.execute_query(query_parada)
    print('resultado yy', resultado)
    return resultado

def fetch_paradas_after_init_date(INIT = '2024-12-01 00:00:00', PARADA_TIME_STOP = 60):
    """ Identifica paradas no DataReceived filtrado por câmera e Lote, 
        considerando apenas registros após uma data inicial (INIT). 
        Retorna os intervalos de tempo entre registros consecutivos 
        que excedem um tempo limite (PARADA_TIME_STOP).
    """
    query_parada = f'''
    WITH ordered_data AS (
        SELECT 
            "TimeStamp", 
            "LoteId", 
            "CameraId", 
            LAG("TimeStamp") OVER (
                PARTITION BY "LoteId", "CameraId" 
                ORDER BY "TimeStamp"
            ) AS prev_timestamp
        FROM "DataReceived"
        WHERE "TimeStamp" > '{INIT}'
    )
    SELECT 
        prev_timestamp AS startTime,
        "TimeStamp" AS stopTime,
        "LoteId", 
        "CameraId",
        EXTRACT(EPOCH FROM ("TimeStamp" - prev_timestamp)) AS intervalo
    FROM ordered_data
    WHERE EXTRACT(EPOCH FROM ("TimeStamp" - prev_timestamp)) > {PARADA_TIME_STOP};
    '''

    resultado = external_db.execute_query(query_parada)
    return resultado


async def fetch_digest_data_from_datareceived(
                                            db: AsyncSession,
                                            CAMERA_NAME_ID, 
                                            DIGEST_TIME=60, 
                                            START_ANALISE="'2025-03-13 08:00:00'",
                                            STOP_ANALISE = datetime.datetime.now()#"'2025-04-1 13:00:00'",                                            
                                            ):
    print(f'Fetch Digest data from data_received from camera {CAMERA_NAME_ID} and Period {START_ANALISE} to {STOP_ANALISE}')

    # Convertendo as strings de data para objetos datetime
    #start_time = datetime.datetime.strptime(START_ANALISE.strip("'"), "%Y-%m-%d %H:%M:%S")
    #stop_time = datetime.datetime.strptime(STOP_ANALISE.strip("'"), "%Y-%m-%d %H:%M:%S")
    if isinstance(START_ANALISE, str):
        start_time = datetime.datetime.strptime(START_ANALISE.strip("'"), "%Y-%m-%d %H:%M:%S")
    else:
        start_time = START_ANALISE

    if isinstance(STOP_ANALISE, str):
        stop_time = datetime.datetime.strptime(STOP_ANALISE.strip("'"), "%Y-%m-%d %H:%M:%S")
    else:
        stop_time = STOP_ANALISE

    
    # Convertendo o tempo de digest para um intervalo de tempo (timedelta)
    digest_delta = datetime.timedelta(seconds=DIGEST_TIME)
    
    # Inicializando o tempo atual com o tempo de início
    current_time = start_time

    resultados = []
    batch = 100    # limita a quantidade de linhas enviadas, no caso de longos periodos 

    while current_time < stop_time:
        # Formatar o intervalo de tempo como uma string no formato necessário
        formatted_start_time = f"'{current_time.strftime('%Y-%m-%d %H:%M:%S')}'"
        formatted_end_time = f"'{(current_time + digest_delta).strftime('%Y-%m-%d %H:%M:%S')}'"
        
        # Criando a consulta com o intervalo de tempo atualizado
        query_digest = text("""
        SELECT "lote_id", "camera_name_id", 
            COUNT(CASE WHEN "ok_nok" = 1 THEN 1 END) AS total_ok,
            COUNT(CASE WHEN "ok_nok" = 0 THEN 1 END) AS total_nok
        FROM "data_received"
        WHERE "timestamp" BETWEEN :start_time AND :end_time AND "camera_name_id" = :camera_name_id
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
                "start_time": current_time,
                "end_time": current_time + digest_delta,
                "camera_name_id": CAMERA_NAME_ID
            }
            )
            resultado = resultado.fetchall()
        except Exception as e:
            print("❌ Erro ao executar query no fetch digest:", str(e))
            raise e
        
        # Armazenando o resultado na lista
        if resultado:  # Se houver resultados, adicione à lista
            resultado.append(formatted_start_time)
            resultado.append(formatted_end_time)
            resultados.append(resultado)
            #print(f'com resultado {batch} {resultado}')
            batch -= 1
            if batch <= 0:
                return resultados
        else:
            pass
            #print("sem resultado", resultado)
        
        # Avançar o tempo para a próxima iteração
        current_time += digest_delta

    return resultados


async def fetch_all_digest_data_from_datareceived(
    db: AsyncSession,
    CAMERA_NAME_ID, 
    DIGEST_TIME=240
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
    digest_delta = datetime.timedelta(seconds=DIGEST_TIME)
    current_time = start_time

    resultados = []
    batch = 100    # limita a quantidade de linhas enviadas, no caso de longos periodos

    while current_time < stop_time:
        formatted_start_time = f"'{current_time.strftime('%Y-%m-%d %H:%M:%S')}'"
        formatted_end_time = f"'{(current_time + digest_delta).strftime('%Y-%m-%d %H:%M:%S')}'"
        
        query_digest = text("""
            SELECT "lote_id", "camera_name_id", 
                COUNT(CASE WHEN "ok_nok" = 1 THEN 1 END) AS total_ok,
                COUNT(CASE WHEN "ok_nok" = 0 THEN 1 END) AS total_nok
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

        if resultado:
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
        
        current_time += digest_delta

    return resultados




async def get_last_timestamp_from_dataReceived_by_camera_id(  
                                                            db: AsyncSession,                                                          
                                                            CAMERA_NAME_ID: int
                                                            ):
    """ 
        Construindo a query para buscar o último TimeStamp da câmera fornecida
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
        print("último TimeStamp da câmera fornecida", resultado)
        # Verificando e retornando o resultado
        if resultado:
            return resultado[0][0]
        else:
            print(f"Nenhum timestamp encontrado para a câmera {CAMERA_NAME_ID}")
            return None
    except Exception as e:
        print(f"Erro ao buscar último DataReceived: {e}")





def fetch_digest_data_from_datareceivedCOPY(CAMERA_NAME_ID=1, 
                      DIGEST_TIME=60, 
                      START_ANALISE="'2025-03-13 08:00:00'",#"'2025-03-24 16:23:00'",
                      STOP_ANALISE = "'2025-04-1 13:00:00'"#"'2025-03-24 19:00:00'"
                      ):
    print(f'Fetch Digest data from DataReceived from camera {CAMERA_NAME_ID} and Period {START_ANALISE} to {STOP_ANALISE}')

    # Convertendo as strings de data para objetos datetime
    #start_time = datetime.datetime.strptime(START_ANALISE.strip("'"), "%Y-%m-%d %H:%M:%S")
    #stop_time = datetime.datetime.strptime(STOP_ANALISE.strip("'"), "%Y-%m-%d %H:%M:%S")
    if isinstance(START_ANALISE, str):
        start_time = datetime.datetime.strptime(START_ANALISE.strip("'"), "%Y-%m-%d %H:%M:%S")
    else:
        start_time = START_ANALISE

    if isinstance(STOP_ANALISE, str):
        stop_time = datetime.datetime.strptime(STOP_ANALISE.strip("'"), "%Y-%m-%d %H:%M:%S")
    else:
        stop_time = STOP_ANALISE

    
    # Convertendo o tempo de digest para um intervalo de tempo (timedelta)
    digest_delta = datetime.timedelta(seconds=DIGEST_TIME)
    
    # Inicializando o tempo atual com o tempo de início
    current_time = start_time

    resultados = []
    batch = 1    # limita a quantidade de linhas enviadas, no caso de longos periodos 

    while current_time < stop_time:
        # Formatar o intervalo de tempo como uma string no formato necessário
        formatted_start_time = f"'{current_time.strftime('%Y-%m-%d %H:%M:%S')}'"
        formatted_end_time = f"'{(current_time + digest_delta).strftime('%Y-%m-%d %H:%M:%S')}'"
        
        # Criando a consulta com o intervalo de tempo atualizado
        query_digest = f'''
        SELECT "LoteId", "CameraId", COUNT(CASE WHEN "OK/NOK" = true THEN 1 END) AS total_ok,
        COUNT(CASE WHEN "OK/NOK" = false THEN 1 END) AS total_nok
        FROM "DataReceived"
        WHERE "TimeStamp" BETWEEN {formatted_start_time} AND {formatted_end_time}
        GROUP BY "LoteId", "CameraId";
        '''
        
        # Aqui você pode adicionar a lógica para executar a consulta `query_digest`
        #print("query_digest", query_digest)  # Para visualizar a query gerada (remover ou ajustar conforme necessário)

        # Executando a consulta (substitua 'external_db.execute_query' pela função real de execução)
        resultado = external_db.execute_query(query_digest)
        
        # Armazenando o resultado na lista
        if resultado:  # Se houver resultados, adicione à lista
            resultado.append(formatted_start_time)
            resultado.append(formatted_end_time)
            resultados.append(resultado)
            print(f'com resultado {batch} {resultado}')
            batch -= 1
            if batch <= 0:
                return resultados
        else:
            print("sem resultado", resultado)
        
        # Avançar o tempo para a próxima iteração
        current_time += digest_delta

    return resultados
