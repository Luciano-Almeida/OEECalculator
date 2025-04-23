import datetime
from .external_database_connection import ExternalDatabaseConnection

external_db = ExternalDatabaseConnection()

#START_ANALISE="'2025-03-13 08:00:00'",
#STOP_ANALISE = "'2025-04-01 13:00:00'"

def fetch_paradas():
    PARADA_TIME_STOP = 60
    query_parada = f'WITH ordered_data AS ( SELECT "TimeStamp", "LoteId", "CameraId", LAG("TimeStamp") OVER (PARTITION BY "LoteId", "CameraId" ORDER BY "TimeStamp") AS prev_timestamp FROM "DataReceived") SELECT prev_timestamp AS startTime, "TimeStamp" AS stopTime, "LoteId", "CameraId", EXTRACT(EPOCH FROM ("TimeStamp" - prev_timestamp)) AS intervalo FROM ordered_data WHERE EXTRACT(EPOCH FROM ("TimeStamp" - prev_timestamp)) > {PARADA_TIME_STOP};'
    resultado = external_db.execute_query(query_parada)
    print('resultado yy', resultado)
    return resultado

def fetch_digest_data(CAMERA_NAME_ID=1, 
                      DIGEST_TIME=60, 
                      START_ANALISE="'2025-03-13 08:00:00'",#"'2025-03-24 16:23:00'",
                      STOP_ANALISE = "'2025-03-15 13:00:00'"#"'2025-03-24 19:00:00'"
                      ):
    # Convertendo as strings de data para objetos datetime
    start_time = datetime.datetime.strptime(START_ANALISE.strip("'"), "%Y-%m-%d %H:%M:%S")
    stop_time = datetime.datetime.strptime(STOP_ANALISE.strip("'"), "%Y-%m-%d %H:%M:%S")
    
    # Convertendo o tempo de digest para um intervalo de tempo (timedelta)
    digest_delta = datetime.timedelta(seconds=DIGEST_TIME)
    
    # Inicializando o tempo atual com o tempo de início
    current_time = start_time

    resultados = []
    
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
        print("query_digest", query_digest)  # Para visualizar a query gerada (remover ou ajustar conforme necessário)

        # Executando a consulta (substitua 'external_db.execute_query' pela função real de execução)
        resultado = external_db.execute_query(query_digest)
        
        # Armazenando o resultado na lista
        if resultado:  # Se houver resultados, adicione à lista
            resultado.append(formatted_start_time)
            resultado.append(formatted_end_time)
            resultados.append(resultado)
            print('com resultado', resultado)
        else:
            print("sem resultado", resultado)
        
        # Avançar o tempo para a próxima iteração
        current_time += digest_delta

    return resultados