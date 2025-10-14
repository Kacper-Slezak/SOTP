# backend/alembic/env.py

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool

from alembic import context

# Import your Base and all your models here so Alembic can see them
from app.models.base import Base
from app.models.user import User
from app.models.device import Device, Credential
from app.models.alert import Alert, AlertRule
from app.models.audit_log import AuditLog
from app.models.metric import DeviceMetric

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_db_url():
    # TA FUNKCJA MUSI WSKAZYWAĆ NA TIMESCALEDB!
    return URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("TIMESCALEDB_USER"),
        password=os.getenv("TIMESCALEDB_PASSWORD"),
        host=os.getenv("TIMESCALEDB_HOST"),
        port=int(os.getenv("TIMESCALEDB_PORT", 5433)),
        database=os.getenv("TIMESCALEDB_DB"),
    )


def run_migrations_offline() -> None:
    url = get_db_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_db_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
