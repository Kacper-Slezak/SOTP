# ADR-003: Celery + Redis for network collectors

- **Status:** Accepted
- **Date:** 2026-10-12
- **Deciders:** Kacper Ślęzak

## Context

Collectors (ICMP ping, SNMP polling, later SSH command execution) perform slow,
failure-prone network I/O against many devices on a fixed schedule. Running
them inside the FastAPI process would tie API latency and availability to the
state of the monitored network, and would make it impossible to scale
collection independently of request handling.

Requirements: periodic scheduling, fan-out to one task per device, retries with
backoff, horizontal scaling, and the ability to trigger an ad-hoc check from the
API.

Alternatives considered:

- **FastAPI background tasks / an asyncio loop in the API:** simplest, but no
  persistence, no retries, and scaling the API scales collection with it.
- **APScheduler in a standalone process:** good scheduling, but no distributed
  work queue — one process does all the work.
- **Kafka / RabbitMQ with custom consumers:** more powerful streaming, but far
  more infrastructure and code for a polling workload.
- **Dramatiq / RQ / arq:** lighter alternatives; Celery won on maturity, built-in
  periodic scheduling (Beat) and ecosystem support (Flower, KEDA scaler,
  OpenTelemetry instrumentation).

## Decision

Run all collectors in a separate **`apps/network_worker`** service built on
**Celery**, with **Redis** as broker and result backend:

- **Celery Beat** owns the schedule (ICMP every 10 min for active devices and
  hourly for all, SNMP every 60 s) and enqueues "schedule all" tasks.
- Those tasks fan out into one task per device; **Celery workers** execute
  them and write results directly to TimescaleDB.
- The API only enqueues work or reads results; it never performs network I/O
  itself.

## Consequences

- **+** API latency is independent of network conditions on monitored devices.
- **+** Workers scale horizontally; in Kubernetes the worker Deployment can be
  autoscaled by KEDA on Redis queue length.
- **+** Retries, time limits and rate limits come from Celery rather than custom
  code.
- **−** Celery is sync-first; async libraries such as `icmplib` and `pysnmp`
  need an event loop per task, which adds boilerplate.
- **−** Beat must run as exactly one replica, or schedules fire twice.
- **−** Redis becomes a critical dependency: if it is down, nothing is
  collected. Redis is not a durable queue, so in-flight tasks can be lost on
  restart — acceptable because collection is periodic and self-healing.
- **−** The worker needs its own database configuration and models, which
  currently duplicates part of `core_backend` (see [ADR-001](0001-monorepo.md)).
