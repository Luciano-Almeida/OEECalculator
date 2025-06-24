import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

#DATABASE_URL = (
#    f"postgresql+asyncpg://{os.getenv('DB1_USER')}:{os.getenv('DB1_PASSWORD')}"
#    f"@{os.getenv('DB1_HOST')}:{os.getenv('DB1_PORT')}/{os.getenv('DB1_NAME')}"
#)
EXTERNAL_DATABASE_URL = os.getenv("EXTERNAL_DATABASE_URL", default = None)
print("EXTERNAL_DATABASE_URL", EXTERNAL_DATABASE_URL)

engine_db1 = create_async_engine(
    EXTERNAL_DATABASE_URL, 
    echo=False,
    pool_size=10,
    max_overflow=20
    )
AsyncSessionLocalDB1 = sessionmaker(engine_db1, class_=AsyncSession, expire_on_commit=False)

# Dependência assíncrona
async def get_external_db():
    async with AsyncSessionLocalDB1() as session:
        yield session
