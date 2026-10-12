# ADR-001: Monorepo with an `apps/` layout

- **Status:** Accepted
- **Date:** 2026-10-12
- **Deciders:** Kacper Ślęzak

## Context

SOTP consists of several deployable units — a FastAPI backend, a Celery network
worker, a Next.js frontend and a planned push agent — plus shared infrastructure
(Docker Compose, Prometheus/Grafana config, later Helm charts and Terraform).
The project is developed by one person, and most features cut across services:
a new metric touches the collector, the TimescaleDB schema, the API and the UI.

Alternatives considered:

- **Polyrepo (one repo per service):** clean ownership boundaries, but every
  cross-cutting change becomes several coordinated PRs, CI config is duplicated,
  and versions between services must be pinned manually.
- **Monorepo with a build tool (Nx, Bazel, Pants):** strong caching and
  dependency graphs, but heavy tooling for four services in two languages.

## Decision

Keep everything in one Git repository with a flat, conventional layout:

- `apps/<service>/` — one directory per deployable, each with its own
  `Dockerfile`, dependency manifest and tests (`core_backend`, `network_worker`,
  `web_frontend`, `sotp_agent`).
- `infrastructure/` — everything needed to run the services (Compose,
  observability config, later `helm/`, `terraform/`, GitOps manifests).
- `docs/` — project documentation, including these ADRs.

No monorepo build tool; a top-level `Makefile` and GitHub Actions jobs are the
orchestration layer.

## Consequences

- **+** A single PR can change the API contract and its consumers atomically.
- **+** One CI pipeline, one issue tracker, one place to look — good for a solo
  project and easy for a reviewer to navigate.
- **+** Each app is still independently buildable as a container, so splitting a
  service into its own repo later is a mechanical change.
- **−** CI builds and tests everything on every push unless jobs are filtered by
  path; this needs to be added as the pipeline grows.
- **−** Python apps keep separate `requirements.txt` files, so shared code
  (models, config) is currently duplicated between `core_backend` and
  `network_worker` rather than packaged as a shared library.
- **−** Repository permissions are all-or-nothing; acceptable at this team size.
