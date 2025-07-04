import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services import ServicoOEE
from routers import api_router  # Importa o roteador centralizado

from database.db import AsyncSessionLocal
from database.db.conexao_db_externo import AsyncSessionLocalDB1
from init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🌱 Iniciando o app...")

    # Inicia o banco de dados
    await init_db()


    # Injeta uma sessão de banco no serviço
    # Cria o serviço OEE já com os bancos
    async with AsyncSessionLocalDB1() as external_db:
        async with AsyncSessionLocal() as db:
            servico_oee = ServicoOEE(db=db, db_external=external_db)

    app.state.servico_oee = servico_oee

    # Supervisão: Tenta reiniciar o serviço se cair
    async def supervision_loop():
        while True:
            try:
                print("🔄 Iniciando serviço OEE supervisionado...")
                await servico_oee.iniciar()
            except Exception as e:
                print(f"💥 Serviço OEE caiu com erro: {e}")
                await asyncio.sleep(5)  # tempo de espera antes de tentar reiniciar
            else:
                print("🟡 Serviço OEE parou normalmente.")
                break  # sai do loop se parou por vontade própria

    task = asyncio.create_task(supervision_loop())

    yield

    print("🛑 Encerrando o app...")

    # Para o serviço de forma segura
    await servico_oee.parar()
    task.cancel()

# Criação da aplicação com lifespan
app = FastAPI(lifespan=lifespan)


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
