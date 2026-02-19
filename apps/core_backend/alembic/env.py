# backend/alembic/env.py

import os
from logging.config import fileConfig

from alembic import context

# Import your Config to get database URLs
from app.core.config import Config

# Import all models
from app.models.alert import Alert, AlertRule
from app.models.audit_log import AuditLog
from app.models.base import Base  # Keep this base
from app.models.device import Credential, Device
from app.models.metric import DeviceMetric  # TimescaleDB model
from app.models.PingResult import PingResult
from app.models.user import User
from sqlalchemy import (  # Use create_engine for sync connection in migrations
    create_engine,
    pool,
)

# configuration from alembic.ini
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from sqlalchemy import MetaData  # <-- Import MetaData

# --- Define which models go to which database ---


# Create new, separate MetaData objects
postgres_metadata = MetaData()
timescale_metadata = MetaData()

# <<<--- POPRAWKA NR 2: Zdefiniuj listę modeli dla timescale
timescale_tables = {DeviceMetric.__tablename__, PingResult.__tablename__}

for table_name, table_obj in Base.metadata.tables.items():
    if table_name in timescale_tables:
        # Kopiuj modele TimescaleDB do timescale_metadata
        table_obj.to_metadata(timescale_metadata)
    else:
        # Kopiuj wszystkie pozostałe modele do postgres_metadata
        table_obj.to_metadata(postgres_metadata)


# --- Function to determine target metadata based on command-line argument ---
def get_target_metadata():
    db_name = context.get_x_argument(as_dictionary=True).get("db")
    if db_name == "timescale":
        print("Targeting TimescaleDB metadata")
        return timescale_metadata
    elif db_name == "postgres":
        print("Targeting PostgreSQL metadata")
        return postgres_metadata
    else:
        # Default or if no argument provided, maybe raise error or default to postgres
        print(
            "Defaulting to PostgreSQL metadata (use -x db=postgres or -x db=timescaledb)"
        )
        return postgres_metadata


target_metadata = get_target_metadata()


# --- Function to get the correct database URL ---
# --- Function to get the correct database URL ---
def get_db_url():
    db_name = context.get_x_argument(as_dictionary=True).get("db")
    if db_name == "timescale":
        print(
            f"Using TimescaleDB URL: {Config.TIMESCALE_URL.replace('+asyncpg', '+psycopg2')}"
        )
        # Alembic needs a sync driver, replace asyncpg with psycopg2
        return Config.TIMESCALE_URL.replace("+asyncpg", "+psycopg2")
    else:  # Default to postgres
        print(
            f"Using PostgreSQL URL: {Config.POSTGRES_URL.replace('+asyncpg', '+psycopg2')}"
        )
        return Config.POSTGRES_URL.replace("+asyncpg", "+psycopg2")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    # Create a standard SQLAlchemy engine (not async)
    connectable = create_engine(get_db_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
