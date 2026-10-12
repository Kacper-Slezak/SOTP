# ADR-002: Separate PostgreSQL and TimescaleDB instances

- **Status:** Accepted
- **Date:** 2026-10-12
- **Deciders:** Kacper Ślęzak

## Context

SOTP stores two very different kinds of data:

- **Relational / inventory data** — users, roles, devices, alerts, audit log.
  Low volume, frequently updated, needs constraints and transactions.
- **Telemetry** — ICMP ping results and SNMP metrics. Append-only, high write
  rate (every device every 10–60 s), queried by time range, and only useful in
  aggregated form after a few weeks.

A general-purpose relational table handles telemetry poorly at scale: indexes
grow without bound, range queries over time scan huge tables, and deleting old
rows is expensive. Dedicated TSDBs (InfluxDB, Prometheus remote storage) solve
that but introduce a second query language and lose SQL joins with inventory.

## Decision

Use **TimescaleDB for telemetry** and **plain PostgreSQL for relational data**,
running as **two separate database instances**:

- TimescaleDB stores `ping_results` and device metrics as hypertables
  (time-partitioned chunks), opening the door to compression, retention
  policies and continuous aggregates.
- PostgreSQL stores everything else.
- The backend opens two async SQLAlchemy engines
  (`db/postgres_session.py`, `db/timescaleDB_session.py`), and Alembic keeps
  two version branches (`versions_postgres/`, `versions_timescale/`), selected
  with `-x db=postgres|timescaledb`.

TimescaleDB is a PostgreSQL extension, so a single instance was possible. We
split them anyway so that telemetry write load, vacuum pressure and storage
growth cannot degrade the API's transactional workload, and so each instance
can be tuned, backed up and scaled on its own schedule.

## Consequences

- **+** Telemetry gets time-series features while staying in SQL — one query
  language and one driver (`asyncpg`) for the whole backend.
- **+** Failure and load isolation: a runaway collector cannot lock up login or
  device CRUD.
- **+** Maps cleanly to the cloud plan (RDS for relational data, a separate
  Timescale instance for metrics) — see [ADR-004](0004-k3d-local-aws-terraform-plan-only.md).
- **−** No foreign keys across databases: `ping_results.device_id` and
  `device_metrics.device_id` are plain integers. Referential integrity (e.g.
  cleaning up metrics for deleted devices) is the application's job.
- **−** No cross-database joins; queries that combine device metadata with
  metrics are done in two steps in the service layer.
- **−** Two connection pools, two migration branches and two sets of
  credentials to manage — more moving parts in Compose, CI and Kubernetes.
