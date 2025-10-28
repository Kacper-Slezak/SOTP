from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import  AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

from app.core.config import Config
from app.utils.databases import create_timescaledb  # Zakładam, że tu masz URL do bazy

# 1. Utwórz silnik (engine) dla TimescaleDB
# Łączy się z bazą danych zdefiniowaną w Twojej konfiguracji
timescale_engine: AsyncEngine = create_timescaledb()

# 2. Utwórz "fabrykę" sesji (sessionmaker)
# To jest konfiguracja dla nowych sesji
AsyncTimescaleSessionLocal = sessionmaker(
    bind=timescale_engine,      # Powiąż z silnikiem Timescale
    class_=AsyncSession,       # Używaj sesji asynchronicznych
    expire_on_commit=False   # Nie wygaszaj obiektów po commicie
)

# 3. Utwórz asynchroniczny context manager
@asynccontextmanager
async def get_timescale_session() -> AsyncGenerator[AsyncSession, None]:
    
    async with AsyncTimescaleSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Zapisz zmiany, jeśli blok 'try' się udał
        except Exception:
            await session.rollback() # Wycofaj zmiany w razie błędu
            raise  # Przekaż błąd dalej
        finally:
            await session.close() # Zawsze zamknij sesję