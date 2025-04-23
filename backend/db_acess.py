import sqlite3

# Conectar ao banco de dados SQLite
conn = sqlite3.connect(r'C:\sqlite3\db_oeecalculator.db')

cursor = conn.cursor()

# Executar uma consulta para verificar os dados na tabela
cursor.execute("SELECT * FROM oeecalculator")

# Exibir os resultados
rows = cursor.fetchall()
for row in rows:
    print(row)

# Fechar a conexão
conn.close()
