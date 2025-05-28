import datetime
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
                                            CAMERA_NAME_ID=1, 
                                            DIGEST_TIME=60, 
                                            START_ANALISE="'2025-03-13 08:00:00'",
                                            STOP_ANALISE = "'2025-04-1 13:00:00'",
                                            db: AsyncSession = Depends(get_external_db)
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
    batch = 10    # limita a quantidade de linhas enviadas, no caso de longos periodos 

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

        try:
            # Executando a consulta (substitua 'external_db.execute_query' pela função real de execução)
            #resultado = external_db.execute_query(query_digest)
            resultado = await db.execute(query_digest)
            resultado = resultado.scalars().all()
            print("*****resultado", resultado)
        except Exception as e:
            print("❌ Erro ao executar query no fetch digest:", str(e))
            raise e
        
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


def fetch_all_digest_data_from_datareceived(CAMERA_NAME_ID=1, DIGEST_TIME=60):
    # Consulta para pegar o intervalo total de tempo no banco externo
    print(f'Fetch ALL Digest data from DataReceived from camera {CAMERA_NAME_ID} and Period {DIGEST_TIME}')
    
    query_limits = '''
    SELECT MIN("TimeStamp") AS min_time, MAX("TimeStamp") AS max_time FROM "DataReceived";
    '''
    limits_result = external_db.execute_query(query_limits)

    if not limits_result or not limits_result[0][0] or not limits_result[0][1]:
        print("Não foi possível obter o intervalo de tempo do banco externo.")
        return []

    # Convertendo os limites retornados em datetime
    start_time = limits_result[0][0]
    stop_time = limits_result[0][1]
    
    # Convertendo o tempo de digest para um intervalo de tempo (timedelta)
    digest_delta = datetime.timedelta(seconds=DIGEST_TIME)
    current_time = start_time

    resultados = []

    while current_time < stop_time:
        formatted_start_time = f"'{current_time.strftime('%Y-%m-%d %H:%M:%S')}'"
        formatted_end_time = f"'{(current_time + digest_delta).strftime('%Y-%m-%d %H:%M:%S')}'"
        
        query_digest = f'''
        SELECT "LoteId", "CameraId", 
               COUNT(CASE WHEN "OK/NOK" = true THEN 1 END) AS total_ok,
               COUNT(CASE WHEN "OK/NOK" = false THEN 1 END) AS total_nok
        FROM "DataReceived"
        WHERE "TimeStamp" BETWEEN {formatted_start_time} AND {formatted_end_time}
        GROUP BY "LoteId", "CameraId";
        '''
        #print('*****query_digest', query_digest)
        resultado = external_db.execute_query(query_digest)

        if resultado:
            resultado.append(formatted_start_time)
            resultado.append(formatted_end_time)
            resultados.append(resultado)
            print('com resultado', resultado)
            return resultados
        else:
            print("sem resultado", resultado)
        
        current_time += digest_delta

    return resultados



def get_last_timestamp_from_dataReceived_by_camera_id(CAMERA_NAME_ID) -> datetime:
    """ 
        Construindo a query para buscar o último TimeStamp da câmera fornecida
    """

    query = f'''
    SELECT "TimeStamp" 
    FROM "DataReceived"
    ORDER BY "TimeStamp" DESC
    LIMIT 1;
    '''

    try:
        # Executando a query
        resultado = external_db.execute_query(query)

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
