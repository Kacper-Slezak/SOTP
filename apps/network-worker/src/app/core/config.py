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
    TIMESCALE_USER = os.getenv("TIMESCALE_USER")
    TIMESCALE_PASSWORD = os.getenv("TIMESCALE_PASSWORD")
    TIMESCALE_DB = os.getenv("TIMESCALE_DB")
    TIMESCALE_HOST = os.getenv("TIMESCALE_HOST", "timescale")
    TIMESCALE_URL = f"postgresql+asyncpg://{TIMESCALE_USER}:{TIMESCALE_PASSWORD}@{TIMESCALE_HOST}:5432/{TIMESCALE_DB}"

    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"



    SNMP_USER = os.getenv("SNMP_USER")
    SNMP_AUTH = os.getenv("SNMP_AUTH")
    SNMP_PRIV = os.getenv("SNMP_PRIV")
