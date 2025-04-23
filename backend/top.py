from fastapi import FastAPI
import psycopg2
from psycopg2 import sql
import os

app = FastAPI()

# Configurações de conexão
DB_HOST = os.getenv('DB_HOST', '172.30.224.1')  # com o docker na mesma máquina utilize o IP do Adaptador Ethernet ou adaptador Wi-fi
DB_PORT = os.getenv('DB_PORT', '5432')  # Porta padrão do PostgreSQL
DB_NAME = os.getenv('DB_NAME', 'query')  # Nome do seu banco de dados
DB_USER = os.getenv('DB_USER', 'postgres')  # Nome de usuário do PostgreSQL
DB_PASSWORD = os.getenv('DB_PASSWORD', 'padrao')  # Senha do usuário

# Função para conectar ao banco de dados PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

#@app.get("/")
def read_root(query):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)  # Exemplo de query
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"result": rows}

if __name__ == '__main__':
    print('Teste de leitura do banco de produção')
    print(read_root())
