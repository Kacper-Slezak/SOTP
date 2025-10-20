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
from app.models.user import User
from sqlalchemy import (  # Use create_engine for sync connection in migrations
    create_engine,
    pool,
)

# configuration from alembic.ini
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Define which models go to which database ---
# All models inherit from Base by default
# We only need to specify the target_metadata for TimescaleDB explicitly
timescale_metadata = Base.metadata  # Initially assume all, then filter
postgres_metadata = Base.metadata

# Filter metadata: Keep only DeviceMetric in timescale_metadata
timescale_metadata.tables = {
    k: v for k, v in Base.metadata.tables.items() if k == DeviceMetric.__tablename__
}
# Filter metadata: Remove DeviceMetric from postgres_metadata
postgres_metadata.tables = {
    k: v for k, v in Base.metadata.tables.items() if k != DeviceMetric.__tablename__
}


# --- Function to determine target metadata based on command-line argument ---
def get_target_metadata():
    db_name = context.get_x_argument(as_dictionary=True).get("db")
    if db_name == "timescaledb":
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
def get_db_url():
    db_name = context.get_x_argument(as_dictionary=True).get("db")
    if db_name == "timescaledb":
        print(
            f"Using TimescaleDB URL: {Config.TIMESCALEDB_URL.replace('+asyncpg', '+psycopg2')}"
        )
        # Alembic needs a sync driver, replace asyncpg with psycopg2
        return Config.TIMESCALEDB_URL.replace("+asyncpg", "+psycopg2")
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
