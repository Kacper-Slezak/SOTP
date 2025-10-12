from redis.asyncio import Redis
from sqlalchemy import create_engine
from app.core.config import Config

def create_postgres():
    return create_engine(url=Config.POSTGRES_URL, pool_pre_ping=True)

def create_timescaledb():
    return create_engine(url=Config.TIMESCALEDB_URL, pool_pre_ping=True)

def create_redis():
    return Redis.from_url(Config.REDIS_URL, decode_responses=True)