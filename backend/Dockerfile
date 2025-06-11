# Usar a imagem base do Python
#FROM python:3.9-slim
FROM python:3.11-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Instalar SQLite
#RUN apt-get update && apt-get install -y sqlite3

# Copiar os arquivos do backend para o container
COPY . .


# Expor a porta 8000 para o servidor
EXPOSE 8000

# Comando para rodar o servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
