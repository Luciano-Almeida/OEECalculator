import asyncio
from datetime import datetime
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.db import engine  # Certifique-se de usar o engine assíncrono
from database.db import Base  # Importa o Base para criar as tabelas
import database.crud as crud  # Importa as funções de criação do CRUD


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

    # Insere os dados iniciais
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as db:  # Gerenciador de contexto para a sessão assíncrona
        try:
            # Verifica se o setupOEE já existe
            setupOEE_exists = await crud.get_oee_setup_by_id(db, oee_id=1)
            if setupOEE_exists:
                print("📷 Tabela setupOEE já possui registros. Nenhuma ação necessária.")
            else:
                # Insere o setup OEE inicial
                user = "instalação"
                start_shift = datetime.strptime("08:00", "%H:%M")  # Hora de início: 08:00 AM
                stop_shift = datetime.strptime("17:00", "%H:%M")  # Hora de término: 05:00 PM
                stop_time = 60.0  # 60 segundos
                line_speed = 120  # 120 unidades por minuto
                digest_time = 60.0 # 60 segundos entre cada resumo 
                camera_name_id = 1  # ID da câmera
                #await crud.create_oee_setup(db, )
                oee_setup = await crud.create_oee_setup(
                    db=db, 
                    user=user, 
                    start_shift=start_shift, 
                    stop_shift=stop_shift,
                    stop_time=stop_time, 
                    line_speed=line_speed, 
                    digest_time=digest_time,
                    camera_name_id=camera_name_id
                )
                print("✅ Dados iniciais inseridos na tabela setupOEE!")

        except SQLAlchemyError as e:
            await db.rollback()  # Reverte alterações no caso de erro
            print(f"❌ Erro ao inicializar o banco de dados: {e}")


if __name__ == "__main__":
    asyncio.run(init_db())  
