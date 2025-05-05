from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = DATABASE_URL = os.getenv("DATABASE_URL", default = None)
print("DATABASE_URL", DATABASE_URL)

# Configuração do engine assíncrono
engine = create_async_engine(DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Dependência assíncrona
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session