<a id="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<br />
<div align="center">
  <a href="https://github.com/Kacper-Slezak/SOTP">
    <img src="apps/web_frontend/public/SOTP.png" alt="SOTP Logo" width="120" height="120">
  </a>

<h3 align="center">SOTP — System Observability & Telemetry Platform</h3>

  <p align="center">
    A modern, Kubernetes-ready platform for monitoring network infrastructure — built as a full portfolio project covering backend, frontend, collectors, CI/CD, and observability.
    <br />
    <a href="https://github.com/Kacper-Slezak/SOTP/tree/main/docs"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Kacper-Slezak/SOTP/issues/new?labels=bug&template=bug_report.md">Report Bug</a>
    &middot;
    <a href="https://github.com/Kacper-Slezak/SOTP/issues/new?labels=enhancement&template=feature_request.md">Request Feature</a>
  </p>
</div>

---

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#architecture">Architecture</a></li>
    <li><a href="#tech-stack">Tech Stack</a></li>
    <li><a href="#project-structure">Project Structure</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#current-status--roadmap">Current Status & Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

---

## About The Project

SOTP is a **network observability and telemetry platform** built to monitor infrastructure — routers, switches, servers — using ICMP, SNMP, and SSH. It is designed as a realistic, production-grade portfolio project demonstrating modern software engineering practices end-to-end.

The project intentionally covers a wide surface area: async Python microservices, a Next.js frontend, distributed task workers, time-series databases, secrets management, CI/CD, and a path toward full Kubernetes deployment with GitOps.

**Key design goals:**
- All collector logic runs as isolated **Celery tasks** — the API never blocks on network I/O
- Credentials (SNMP community strings, SSH passwords) are stored exclusively in **HashiCorp Vault**
- Metrics go into **TimescaleDB** (hypertables), while relational data stays in **PostgreSQL**
- Every component is containerized; the entire stack starts with a single `make dev`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                     │
│         Next.js 15 (App Router) + Tailwind CSS              │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    API GATEWAY LAYER                        │
│              FastAPI (REST) + JWT Auth + RBAC               │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  TASK QUEUE LAYER                           │
│            Redis (broker) + Celery (workers + beat)         │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                NETWORK WORKER SERVICE                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   ICMP   │  │   SNMP   │  │   SSH    │  │ Syslog   │     │
│  │ Collector│  │ Collector│  │ Executor │  │(planned) │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    DATA LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  PostgreSQL  │  │ TimescaleDB  │  │    Vault     │       │
│  │ (inventory,  │  │ (metrics,    │  │  (secrets)   │       │  
│  │  users, RBAC)│  │  ping results│  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Tech Stack

**Backend**

[![FastAPI][FastAPI-badge]][FastAPI-url]
[![Python][Python-badge]][Python-url]
[![Celery][Celery-badge]][Celery-url]
[![SQLAlchemy][SQLAlchemy-badge]][SQLAlchemy-url]
[![Alembic][Alembic-badge]][Alembic-url]

**Frontend**

[![Next.js][Next-badge]][Next-url]
[![React][React-badge]][React-url]
[![TypeScript][TS-badge]][TS-url]
[![Tailwind][Tailwind-badge]][Tailwind-url]

**Data & Messaging**

[![PostgreSQL][PG-badge]][PG-url]
[![TimescaleDB][TS-db-badge]][TS-db-url]
[![Redis][Redis-badge]][Redis-url]
[![Vault][Vault-badge]][Vault-url]

**Observability**

[![Prometheus][Prom-badge]][Prom-url]
[![Grafana][Grafana-badge]][Grafana-url]

**Infrastructure & CI/CD**

[![Docker][Docker-badge]][Docker-url]
[![GitHub Actions][GHA-badge]][GHA-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Project Structure

```
SOTP/
├── apps/
│   ├── core_backend/          # FastAPI application (API, auth, services, models)
│   │   ├── app/
│   │   │   ├── api/v1/        # Routers: auth, devices, users
│   │   │   ├── core/          # Config, security (JWT), observability
│   │   │   ├── db/            # Session factories, dependencies
│   │   │   ├── models/        # SQLAlchemy models (User, Device, Metric, ...)
│   │   │   ├── schemas/       # Pydantic request/response schemas
│   │   │   └── services/      # DeviceService, PingService, (VaultService)
│   │   ├── alembic/           # Migrations — separate branches for PG and TimescaleDB
│   │   └── tests/             # Unit + integration tests (pytest)
│   │
│   ├── network_worker/        # Standalone Celery service for collectors
│   │   └── src/app/
│   │       ├── tasks/         # monitoring_tasks.py (ICMP), snmp_collector.py
│   │       ├── celery/        # Celery app config, Beat schedule
│   │       └── tests/         # Worker unit + integration tests
│   │
│   ├── web_frontend/          # Next.js 15 application
│   │   └── src/
│   │       ├── app/           # App Router pages ((dashboard)/devices, ...)
│   │       ├── components/    # Sidebar, Navbar, UI primitives
│   │       └── lib/           # API client (api.ts), utils
│   │
│   └── sotp_agent/            # (Planned) Lightweight Python push-metrics agent
│
├── infrastructure/
│   ├── docker/                # docker-compose.dev.yml + init scripts
│   ├── prometheus/            # prometheus.yml
│   ├── grafana/               # Datasources + dashboard provisioning
│   └── k8s/                   # Early Kubernetes manifests (in progress)
│
├── docs/                      # Architecture, API, DB schema, deployment guides
└── .github/
    └── workflows/             # ci.yml, deploy-prod.yml, discord_notifier.yml
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Getting Started

### Prerequisites

- [Docker Engine](https://docs.docker.com/engine/install/) + [Docker Compose](https://docs.docker.com/compose/install/)
- `make` (optional but recommended)
- Git

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/Kacper-Slezak/SOTP.git
   cd SOTP
   ```

2. Create your environment file:
   ```sh
   cp .env.example .env
   # Review .env — defaults work for local development
   ```

3. Start the full stack:
   ```sh
   make dev
   ```

   This builds all images, runs Alembic migrations (PostgreSQL + TimescaleDB), and starts every service.

4. Verify everything is running:
   ```sh
   curl http://localhost:8000/health
   # Should return: {"status": "ok", ...}
   ```

**Access points:**

| Service | URL | Notes |
|---|---|---|
| Frontend | http://localhost:3000 | Next.js dev server |
| Backend API | http://localhost:8000/docs | Interactive Swagger UI |
| Grafana | http://localhost:3001 | admin / admin |
| Prometheus | http://localhost:9090 | — |
| Vault | http://localhost:8200 | dev mode, token from `.env` |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Usage

### Makefile Commands

```sh
make dev            # Build and start all services in background
make down           # Stop and remove containers
make logs           # Tail logs from all services
make shell-backend  # Open bash in the backend container
make test           # Run pytest inside the backend container
make seed           # Populate DB with demo users and devices
make clean          # Stop containers and delete all volumes (fresh start)
```

### API Authentication

All device endpoints require a Bearer token. The full flow:

```sh
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com", "password": "StrongPass1!"}'

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "StrongPass1!"}'
# Returns: {"access_token": "...", "refresh_token": "..."}

# 3. Use the token
curl http://localhost:8000/api/v1/devices \
  -H "Authorization: Bearer <access_token>"
```

Full API reference is at `http://localhost:8000/docs` when the stack is running, or see [`docs/API.md`](docs/API.md).

### RBAC Roles

| Role | GET devices | POST/PUT devices | DELETE devices | Admin actions |
|---|:---:|:---:|:---:|:---:|
| ADMIN | ✅ | ✅ | ✅ | ✅ |
| OPERATOR | ✅ | ✅ | ❌ | ❌ |
| AUDITOR | ✅ | ❌ | ❌ | ❌ |
| READONLY | ✅ | ❌ | ❌ | ❌ |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Current Status & Roadmap

### Completed

**Foundation & Infrastructure**
- Monorepo structure (`apps/core_backend`, `apps/network_worker`, `apps/web_frontend`, `apps/sotp_agent`)
- Full Docker Compose dev stack — PostgreSQL, TimescaleDB, Redis, Vault, Prometheus, Grafana, Celery worker + beat
- Alembic migrations with separate branches for PostgreSQL and TimescaleDB (including hypertables)
- DevContainers for backend, frontend, and DevOps profiles
- `Makefile` shortcuts for all common workflows

**Backend (Core API)**
- FastAPI application with async SQLAlchemy sessions (dual-DB: PostgreSQL + TimescaleDB)
- Complete Device CRUD with `DeviceService` (soft delete, IP conflict checks)
- JWT authentication — register, login, refresh token (`python-jose` + `passlib/bcrypt`)
- RBAC — `require_role()` dependency applied to all device endpoints
- `GET /api/v1/users/me` endpoint
- Health check endpoint (`/health`) verifying all three datastores
- Prometheus metrics exposed via `prometheus-fastapi-instrumentator`

**Network Worker**
- Standalone Celery service with isolated `network_worker` app
- ICMP collector (`icmplib`) — async ping, writes `PingResult` to TimescaleDB
- SNMP collector (`pysnmp`) — CPU, RAM, uptime, interface count via SNMPv3 USM
- Celery Beat schedule — ICMP every 10 min (active) / every hour (all), SNMP every 60s

**Observability Stack**
- Prometheus scraping the FastAPI `/metrics` endpoint
- Grafana with auto-provisioned Prometheus datasource and example dashboard
- Dashboard JSON under version control (`infrastructure/grafana/dashboards/`)

**Frontend (MVP)**
- Next.js 15 App Router with TypeScript
- Persistent layout — Sidebar (`FiGrid`, `FiBarChart2`, ...) + Navbar with mobile hamburger
- Home dashboard with card links
- `/devices/new` — Add Device form with validation, `useMutation`, and `QueryClient` invalidation
- `@tanstack/react-query`, `zustand`, `axios` configured
- shadcn/ui Button and Table primitives

**CI/CD**
- GitHub Actions pipeline: `quality` (pre-commit) → `security` (Bandit + Safety) → `test` (pytest + ESLint) → `build` (Docker images for all three apps)
- Separate `deploy-prod.yml` triggered on version tags — pushes to GitHub Container Registry + creates GitHub Release with auto-changelog
- Reusable `discord_notifier.yml` with success / warning (no tests found) / failure states
- Conventional Commits convention + PR template + Issue templates

**Testing**
- Unit tests: `test_rbac.py` (dependency override pattern), `test_soft_delete.py` (mocked `AsyncSession`)
- Integration tests: `test_auth.py` (skipped in CI, run locally against live DB)
- Worker tests: `test_icmp_all.py`, `test_snmp_collector.py` with mocked sessions and Celery `.delay`

---

### In Progress

**Phase 1.3 — Auth Tests**
Integration tests for the full JWT + RBAC flow. Currently blocked by a `bcrypt` version incompatibility (`passlib 1.7.4` + `bcrypt 4.x`) — fix: downgrade `bcrypt` to `3.x` or switch to `pwdlib`. See `errors.txt` for the traceback.

**Phase 5 — Frontend Devices Table**
The `DevicesTable` component is scaffolded but commented out while the API integration and loading states are finalized.

---

### Up Next (Planned Phases)

| Phase | Description | Key Items |
|---|---|---|
| **1.4** | CRUD API tests | `DeviceService` unit tests, `httpx.AsyncClient` API tests, >80% coverage |
| **1.5** | Pagination & filtering | `limit/offset`, `sort_by`, `filter` on `GET /devices` |
| **2** | Vault integration | `VaultService` — store/retrieve SNMP & SSH credentials via `hvac` |
| **3** | Worker refinement | Fix `device_id` propagation in ICMP, SNMP CPU/RAM from Vault, SSH executor (Netmiko) |
| **4** | Full observability | Loki + Promtail, Grafana Tempo, OpenTelemetry instrumentation, Traefik reverse proxy |
| **5** | Frontend polish | Devices table wired to API, Auth pages, route protection (Zustand + Next.js middleware), Metrics tab with `recharts` |
| **6** | SOTP Agent | Lightweight Python agent (`psutil`) pushing metrics to `POST /api/v1/ingest/metrics` |
| **7** | Kubernetes | K3d local cluster, Helm chart, StatefulSets for DBs, Vault Agent Injector, ArgoCD GitOps |
| **8** | Production features | Alerting system, audit middleware, PDF/CSV reporting, in-app SSH console |
| **9** | Advanced (pick 1–2) | Linkerd mTLS, ML anomaly detection, Containerlab E2E tests, TextFSM SSH parser |

See [`docs/SOTP_ROADMAP.md`](docs/SOTP_ROADMAP.md) for full per-step detail including branch names and acceptance criteria.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Contributing

1. Fork the repository
2. Check the [open issues](https://github.com/Kacper-Slezak/SOTP/issues) and assign yourself one
3. Create a branch following the convention: `feat/47-jwt-auth`, `fix/63-prometheus-target`, `test/53-auth-tests`
4. Commit using [Conventional Commits](.github/COMMIT_COVENCTIONS.md): `feat(api): add device pagination`
5. Open a Pull Request against `develop` — CI must be green before merge

See [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) for the full workflow.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Contact

**Kacper Ślęzak** — [LinkedIn](https://www.linkedin.com/in/kacper-slezak)

Project: [https://github.com/Kacper-Slezak/SOTP](https://github.com/Kacper-Slezak/SOTP)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- BADGE LINKS -->
[contributors-shield]: https://img.shields.io/github/contributors/Kacper-Slezak/SOTP.svg?style=for-the-badge
[contributors-url]: https://github.com/Kacper-Slezak/SOTP/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Kacper-Slezak/SOTP.svg?style=for-the-badge
[forks-url]: https://github.com/Kacper-Slezak/SOTP/network/members
[stars-shield]: https://img.shields.io/github/stars/Kacper-Slezak/SOTP.svg?style=for-the-badge
[stars-url]: https://github.com/Kacper-Slezak/SOTP/stargazers
[issues-shield]: https://img.shields.io/github/issues/Kacper-Slezak/SOTP.svg?style=for-the-badge
[issues-url]: https://github.com/Kacper-Slezak/SOTP/issues
[license-shield]: https://img.shields.io/github/license/Kacper-Slezak/SOTP.svg?style=for-the-badge
[license-url]: https://github.com/Kacper-Slezak/SOTP/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/kacper-slezak

<!-- TECH STACK BADGES -->
[FastAPI-badge]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com/
[Python-badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Celery-badge]: https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white
[Celery-url]: https://docs.celeryq.dev/
[SQLAlchemy-badge]: https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white
[SQLAlchemy-url]: https://www.sqlalchemy.org/
[Alembic-badge]: https://img.shields.io/badge/Alembic-6BA539?style=for-the-badge
[Alembic-url]: https://alembic.sqlalchemy.org/
[Next-badge]: https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React-badge]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[TS-badge]: https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white
[TS-url]: https://www.typescriptlang.org/
[Tailwind-badge]: https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white
[Tailwind-url]: https://tailwindcss.com/
[PG-badge]: https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white
[PG-url]: https://www.postgresql.org/
[TS-db-badge]: https://img.shields.io/badge/TimescaleDB-FDB515?style=for-the-badge&logo=timescale&logoColor=black
[TS-db-url]: https://www.timescale.com/
[Redis-badge]: https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white
[Redis-url]: https://redis.io/
[Vault-badge]: https://img.shields.io/badge/Vault-FFEC6E?style=for-the-badge&logo=vault&logoColor=black
[Vault-url]: https://www.vaultproject.io/
[Prom-badge]: https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=Prometheus&logoColor=white
[Prom-url]: https://prometheus.io/
[Grafana-badge]: https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white
[Grafana-url]: https://grafana.com/
[Docker-badge]: https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
[GHA-badge]: https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white
[GHA-url]: https://github.com/features/actions
