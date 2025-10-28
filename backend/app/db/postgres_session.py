from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 1. Importuj fabrykę silnika PostgreSQL
from app.utils.databases import create_postgres

# 2. Utwórz silnik, wywołując funkcję z fabryki
postgres_engine: AsyncEngine = create_postgres()

# 3. Utwórz "fabrykę" sesji (sessionmaker) powiązaną z tym silnikiem
AsyncPostgresSessionLocal = sessionmaker(
    bind=postgres_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 4. Utwórz asynchroniczny context manager
@asynccontextmanager
async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:

    async with AsyncPostgresSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
