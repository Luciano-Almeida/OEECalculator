import psycopg2
from psycopg2 import sql
import os

class ExternalDatabaseConnection:
    def __init__(self):
        # Configurações de conexão
        self.db_host = os.getenv('DB_HOST', '172.30.224.1')
        self.db_port = os.getenv('DB_PORT', '5432')
        self.db_name = os.getenv('DB_NAME', 'query')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', 'padrao')
    
    def get_connection(self):
        """Cria e retorna uma conexão com o banco de dados."""
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password
        )
    
    def execute_query(self, query):
        """Executa uma query no banco de dados e retorna os resultados."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows#{"result": rows}
        finally:
            cursor.close()
            conn.close()

# Exemplo de uso:
# db = ExternalDatabaseConnection()
# resultado = db.execute_query("SELECT * FROM sua_tabela;")
# print(resultado)