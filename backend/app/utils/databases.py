from app.core.config import Config
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import Optional


def create_postgres():
    return create_async_engine(url=Config.POSTGRES_URL, pool_pre_ping=True)


def create_timescaledb():
    return create_async_engine(url=Config.TIMESCALE_URL, pool_pre_ping=True)


def create_redis():
    return Redis.from_url(Config.REDIS_URL, decode_responses=True)






  

    