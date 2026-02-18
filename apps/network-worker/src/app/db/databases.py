from typing import Optional

from app.core.config import Config
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


def create_postgres():
    return create_async_engine(url=Config.POSTGRES_URL, pool_pre_ping=True)


def create_timescaledb():
    return create_async_engine(url=Config.TIMESCALE_URL, pool_pre_ping=True)


def create_redis():
    return Redis.from_url(Config.REDIS_URL, decode_responses=True)
