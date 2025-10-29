from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker


from app.utils.databases import create_postgres


postgres_engine: AsyncEngine = create_postgres()


AsyncPostgresSessionLocal = sessionmaker(
    bind=postgres_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)



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
