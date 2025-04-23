import asyncio
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
import time

from database.db import engine  # Certifique-se de usar o engine assíncrono
from database.db import Base  # Importa o Base para criar as tabelas
import database.crud as crud


async def wait_for_db():
    """Tenta conectar-se ao banco de dados e espera até que esteja pronto."""
    while True:
        print("tentando conectar o banco de dados ...")
        try:
            # Tenta se conectar ao banco
            async with engine.connect() as conn:
                await conn.close()  # Fecha a conexão explicitamente
                print("Banco de Dados Conectado")
                break
        except OperationalError:
            await asyncio.sleep(2)


async def init_db():
    print("Iniciando o banco de dados")
    await wait_for_db()  # Garante que o banco está pronto antes de continuar
    print("Conectado")
    # Cria todas as tabelas (se não existirem)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Insere usuários iniciais
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as db:  # Gerenciador de contexto para a sessão assíncrona
        try:
            # Verifica se o primeiro lote já existe
            menu_exists = await crud.get_lote_by_id(db, lote_id=1)
            if menu_exists:
                print(f"Lote {1} já criado.")
            else:
                _ = await crud.create_lote(db, name_lote="TesteLote", origem="Teste")
                print("Lote de teste criado")

        except SQLAlchemyError as e:
            await db.rollback()  # Reverte alterações no caso de erro
            print(f"Erro ao inicializar o banco de dados: {e}")


if __name__ == "__main__":
    asyncio.run(init_db())
