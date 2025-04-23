import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from routers import api_router  # Importa o roteador centralizado
from typing import Dict, List

from utils import parada_nao_planejada, producao, start_end_times

app = FastAPI()

# Configuração do CORSMiddleware para permitir requisições de http://localhost:3000
origins = [
    "http://localhost:3000",  # Permitir localhost:3000
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Lista de origens permitidas
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)


# Função para acessar o banco de dados SQLite
"""def get_db():
    conn = sqlite3.connect('/data/db_oeecalculator.db')
    conn.row_factory = sqlite3.Row  # Para obter os resultados como dicionários
    return conn"""

from init_db import init_db
""" Inicialização do Banco de Dados (com evento de startup -> lifespan) """
@app.on_event("startup")
async def startup_event():
    await init_db()



# Modelo Pydantic para definir a estrutura dos dados que serão retornados
class DataItem(BaseModel):
    id: int
    timestamp: str
    inspeção: int
    lote: str
    validade: str
    nome_camera: str

class OEESearch(BaseModel):
    startDate: str
    endDate: str
    cycleTime: str
    stopedMachine: str
    totalPlannedStops: str
    cameraType: str

    class Config:
        arbitrary_types_allowed = True  # Permite tipos arbitrários como datetime


def search_1(data):
    stoped_machine = int(data.stopedMachine)

    query = """
    SELECT id, timestamp, inspeção, lote, validade
    FROM oeecalculator
    WHERE timestamp BETWEEN ? AND ? AND nome_camera = ?
    ORDER BY timestamp
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Passando os parâmetros de forma segura
        cursor.execute(query, (data.startDate, data.endDate, data.cameraType))
        
        # Obtendo os nomes das colunas
        columns = [description[0] for description in cursor.description]
        
        # Convertendo as linhas para dicionários
        rows = cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}
    finally:
        conn.close()

    if not results:
        return {"error": "No data found for the specified parameters"}

    A_inicio, A_fim, B_tempo_total_disponivel = start_end_times(results)
    C_paradas_planejadas = float(data.totalPlannedStops)
    D_tempo_disponivel_liquido = B_tempo_total_disponivel - C_paradas_planejadas
    E_paradas_nao_planejadas = parada_nao_planejada(results, stoped_machine) - C_paradas_planejadas  # subtrair paradas planejadas para não colocar duas vezes as paradas planejadas
    F_tempo_operando = D_tempo_disponivel_liquido - E_paradas_nao_planejadas
    G_relacao_disponibilidade = F_tempo_operando / D_tempo_disponivel_liquido if D_tempo_disponivel_liquido != 0 else 0

    #print("G_relacao_disponibilidade", G_relacao_disponibilidade)
    H_total_pecas, L_total_ruins, total_bons = producao(results)
    I_Tempo_ideal_ciclo = float(data.cycleTime)
    J_maximo_pecas = I_Tempo_ideal_ciclo * F_tempo_operando
    K_relacao_desempenho = H_total_pecas / J_maximo_pecas

    M_relacao_qualidade = total_bons / H_total_pecas if H_total_pecas != 0 else 0

    oee = G_relacao_disponibilidade * K_relacao_desempenho * M_relacao_qualidade 

    response = {
        "A_inicio": str(A_inicio),
        "A_fim": str(A_fim),
        "B_Tempo_total_disponivel": str(round(B_tempo_total_disponivel, 2)),
        "C_Paradas_planejadas": str(C_paradas_planejadas),
        "D_Tempo_disponivel_liquido(B-C)": str(round(D_tempo_disponivel_liquido, 2)),
        "E_Paradas_nao_planejadas": str(round(E_paradas_nao_planejadas, 2)),
        "F_Tempo_operando(D-E)": str(round(F_tempo_operando, 2)),
        "G_Relacao_disponibilidade(F/D)": str(round(G_relacao_disponibilidade * 100, 2)),

        "H_Total_pecas_produzidas": str(H_total_pecas),
        "I_Tempo_ideal_ciclo": str(round(I_Tempo_ideal_ciclo, 2)),
        "J_Numero_maximo_pecas_que_podem_ser_produzidas(IxF)": str(round(J_maximo_pecas, 2)),
        "K_Relacao_desempenho(H/J)": str(round(K_relacao_desempenho * 100, 2)),

        "L_Total_pecas_ruins": str(L_total_ruins),
        "M_Relacao_qualidade(H-L/H)": str(round(M_relacao_qualidade * 100, 2)),

        "OEE": str(round(oee * 100, 2))
        
    }
    
    return response


@app.post("/oee_search")
async def receive_oee_data(data: OEESearch) -> Dict[str, str]:
    # processar os dados e retornar um dicionário com os resultados
    return search_1(data)

# Rota para obter todos os dados da tabela
@app.get("/api/data")#, response_model=List[DataItem])
def get_data():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM oeecalculator")
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results

# Nova rota para listar arquivos na pasta 'app' do Docker
@app.get("/api/files", response_model=List[str])
def list_files():
    # Caminho relativo ou absoluto da pasta 'app' dentro do container
    app_folder_path = "/data"  # Caso o código esteja na pasta '/app' no Docker
    
    try:
        files = os.listdir(app_folder_path)
        return files
    except FileNotFoundError:
        return {"error": f"Diretório {app_folder_path} não encontrado."}
    except Exception as e:
        return {"error": str(e)}



# Inclui todas as rotas do api_router
app.include_router(api_router)
