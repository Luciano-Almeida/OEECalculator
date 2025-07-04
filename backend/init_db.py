import asyncio
from sqlalchemy.exc import OperationalError

from database.db import engine  # Certifique-se de usar o engine assíncrono
from database.db import Base  # Importa o Base para criar as tabelas


async def wait_for_db():
    """Tenta conectar-se ao banco de dados e espera até que esteja pronto."""
    while True:
        print("Tentando conectar ao banco de dados...")
        try:
            # Tenta se conectar ao banco
            async with engine.connect() as conn:
                await conn.close()  # Fecha a conexão explicitamente
                print("✅ Banco de Dados Conectado!")
                break
        except OperationalError:
            print("⏳ Banco de dados indisponível. Tentando novamente em 2 segundos...")
            await asyncio.sleep(2)


async def init_db():
    print("🚀 Iniciando o banco de dados...")
    await wait_for_db()  # Garante que o banco está pronto antes de continuar

    # Cria todas as tabelas (se não existirem)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())  
