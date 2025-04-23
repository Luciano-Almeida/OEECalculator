# Função que calcula o tempo total de paradas não planejadas
from datetime import datetime

columns_names ={
    'inspecao': 'inspeção',
    "timestamp": "timestamp",
}

# Function to convert timedelta to ISO-like format
def timedelta_to_iso(timedelta_obj):
    # Get hours, minutes, and seconds from the timedelta
    hours, remainder = divmod(timedelta_obj.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{timedelta_obj.days * 24 + hours:02}:{minutes:02}:{seconds:02}"

def parada_nao_planejada(results, stoped_machine) -> int:
    if len(results) < 2:
        return 0

    total_stopped_time = 0
    
    for i in range(1, len(results)):
        # Convertendo as datas para o formato datetime
        current_timestamp = datetime.strptime(results[i][columns_names['timestamp']], "%Y-%m-%d %H:%M:%S")
        previous_timestamp = datetime.strptime(results[i-1][columns_names['timestamp']], "%Y-%m-%d %H:%M:%S")

        # Calculando a diferença em segundos
        diff_seconds = (current_timestamp - previous_timestamp).total_seconds()
        print(current_timestamp, previous_timestamp, stoped_machine, diff_seconds)
        # subtrai o intervalo considerado normal entre as produções
        diff_seconds -= stoped_machine
        
        
        # Verificar se a diferença é maior que o tempo de parada permitido
        if diff_seconds > 0:
            # Se a máquina ficou parada, soma o tempo de parada
            total_stopped_time += diff_seconds
            print("total_stopped_time", total_stopped_time)
    
    # Converter a diferença para minutos
    total_stopped_time = total_stopped_time / 60

    return total_stopped_time


def start_end_times(results):
    timestamp1 = results[0][columns_names['timestamp']]
    timestamp2 = results[-1][columns_names['timestamp']]

    print('timestamp1', timestamp1)
    print('timestamp2', timestamp2)

    # Definir o formato de data
    formato = "%Y-%m-%d %H:%M:%S"

    try:
        # Converter os timestamps em objetos datetime
        data1 = datetime.strptime(timestamp1, formato)
        data2 = datetime.strptime(timestamp2, formato)
    except ValueError as e:
        raise ValueError(f"Timestamp format error: {e}")

    # Calcular a diferença entre as duas datas
    diferenca = data2 - data1

    # Converter a diferença para minutos
    diferenca_em_minutos = diferenca.total_seconds() / 60

    return timestamp1, timestamp2, diferenca_em_minutos


def producao(results):
    total = 0
    total_bons = 0
    total_ruins = 0

    for result in results:
        total += 1  # Incrementa o total de peças produzidas
        inspecao = result.get(columns_names['inspecao'])

        if inspecao == 1:
            total_bons += 1  # Incrementa as peças boas
        elif inspecao == 0:
            total_ruins += 1  # Incrementa as peças ruins
        else:
            # Caso inspecao tenha valor inválido
            print(f"Valor de inspeção inválido: {inspecao}")

    return total, total_ruins, total_bons
