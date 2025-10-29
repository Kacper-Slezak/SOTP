from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import Config
from app.utils.databases import create_timescaledb 


timescale_engine: AsyncEngine = create_timescaledb()


AsyncTimescaleSessionLocal = sessionmaker(
    bind=timescale_engine,  
    class_=AsyncSession, 
    expire_on_commit=False,  
)



@asynccontextmanager
async def get_timescale_session() -> AsyncGenerator[AsyncSession, None]:

    async with AsyncTimescaleSessionLocal() as session:
        try:
            yield session
            await session.commit()  
        except Exception:
            await session.rollback()  
            raise  
        finally:
            await session.close() 
