import os

from dotenv import load_dotenv

load_dotenv(override=True)


class Config:
    # Postgres
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
    POSTGRES_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"

    # Timescaledb
    TIMESCALEDB_USER = os.getenv("TIMESCALEDB_USER")
    TIMESCALEDB_PASSWORD = os.getenv("TIMESCALEDB_PASSWORD")
    TIMESCALEDB_DB = os.getenv("TIMESCALEDB_DB")
    TIMESCALEDB_HOST = os.getenv("TIMESCALEDB_HOST", "timescaledb")
    TIMESCALEDB_URL = f"postgresql+asyncpg://{TIMESCALEDB_USER}:{TIMESCALEDB_PASSWORD}@{TIMESCALEDB_HOST}:5432/{TIMESCALEDB_DB}"

    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
