import asyncio
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from services import ServicoOEE
from routers import api_router  # Importa o roteador centralizado
from typing import Dict, List

from database.db import get_db
from utils import parada_nao_planejada, producao, start_end_times

from init_db import init_db

#servico_oee = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🌱 Iniciando o app...")

    # Inicia o banco de dados
    await init_db()

    # Cria o serviço OEE
    #servico_oee = ServicoOEE()

    # Injeta uma sessão de banco no serviço
    
    # Cria o serviço OEE já com o db
    async for db in get_db():
        #servico_oee.set_db(db)
        servico_oee = ServicoOEE(db=db)
        break  # Pega uma sessão apenas

    # Inicia o serviço em segundo plano
    task = asyncio.create_task(servico_oee.iniciar())

    # Armazena o serviço no estado do app
    app.state.servico_oee = servico_oee

    yield  # Aqui o app está rodando

    print("🛑 Encerrando o app...")

    # Para o serviço de forma segura
    await servico_oee.parar()
    task.cancel()

# Criação da aplicação com lifespan
app = FastAPI(lifespan=lifespan)
#app = FastAPI()


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


# Inclui todas as rotas do api_router
app.include_router(api_router)
