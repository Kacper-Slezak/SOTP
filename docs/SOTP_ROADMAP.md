# SOTP — Project Roadmap v3.1

> **Goal:** Portfolio-ready network infrastructure monitoring platform — solo project.
> **Context:** SRE Intern CV project; Kubernetes (K8s) is a core component.
> **Rule:** Every step = separate branch + PR. Every step must have a dedicated GitHub issue.

---

## Current Status (April 10, 2026)

**Phase 1 — fully completed ✅**

All backend foundation work is done:

* JWT Authentication (register / login / refresh) — working in production.
* RBAC — `require_role()` applied to all device endpoints with correct per-role permissions.
* Auth integration tests — `test_auth.py` covers registration, login, refresh, token expiry, RBAC edge cases. The old `passlib` bcrypt incompatibility was resolved by switching to direct `bcrypt` calls in `security.py`.
* Device CRUD API tests — `test_device_api.py` covers all HTTP methods with dependency-override mocking for all four roles; `test_device_service.py` covers `DeviceService` unit tests with mocked `AsyncSession`.
* Pagination, sorting, filtering — `DeviceService.get_all()` accepts `limit`, `offset`, `sort_by`, `sort_order`, `is_active`, `device_type`, `vendor`; response uses `PaginatedResponse[DeviceOut]`.

Infrastructure and CI/CD work done in parallel:

* Full Docker Compose dev stack — PostgreSQL, TimescaleDB, Redis, Vault, Prometheus, Grafana, Celery worker + beat.
* Alembic — dual-branch migrations (postgres / timescale) including TimescaleDB hypertables.
* DevContainers — backend, frontend, DevOps profiles.
* `Makefile` shortcuts for all common workflows.
* GitHub Actions pipeline — `quality` → `security` → `test` → `build` → Discord notifications.
* Tag-triggered `deploy-prod.yml` — GHCR push + GitHub Release with auto-changelog.
* Monorepo structure — `apps/core_backend`, `apps/network_worker`, `apps/web_frontend`, `apps/sotp_agent`.

Network Worker done:

* Standalone Celery service, isolated from core backend.
* ICMP collector (`icmplib`) — async ping, writes `PingResult` to TimescaleDB.
* SNMP collector (`pysnmp`) — CPU, RAM, uptime, interface count via SNMPv3 USM.
* Celery Beat schedule — ICMP every 10 min (active) / every hour (all), SNMP every 60 s.

Frontend MVP done:

* Next.js 15 App Router — persistent layout (Sidebar + Navbar with mobile hamburger).
* Home dashboard with card links.
* `/devices/new` — Add Device form with IP validation, `useMutation`, `QueryClient` invalidation.
* `@tanstack/react-query`, `zustand`, `axios` configured.
* `shadcn/ui` Button and Table primitives.

**In progress:**

* Phase 2 — Vault integration (`VaultService`).
* Phase 5 — `DevicesTable` component wired to `GET /api/v1/devices`.

---

## PHASE 1 — Backend: Auth & Security ✅ COMPLETED

### Step 1.1 — JWT Authentication ✅
* `app/core/security.py` — `create_access_token`, `create_refresh_token`, `decode_access_token` (python-jose + direct bcrypt).
* `app/api/v1/auth.py` — `POST /api/v1/auth/register`, `/login`, `/refresh`.
* `app/api/dependencies.py` — `get_current_user` dependency validating the Bearer token.
* `app/schemas/auth.py` — `TokenResponse`, `LoginRequest`, `RegisterRequest`, `RefreshRequest`.

### Step 1.2 — RBAC ✅
* `require_role(allowed_roles)` dependency in `app/api/dependencies.py`.
* `GET /devices` → ADMIN, OPERATOR, READONLY, AUDITOR.
* `POST /devices` → ADMIN only.
* `PUT /devices/{id}` → ADMIN, OPERATOR.
* `DELETE /devices/{id}` → ADMIN only.
* `GET /api/v1/users/me` — returns current user and role.

### Step 1.3 — Auth Tests ✅
* `tests/integration/test_auth.py` — registration, login, token refresh, `401` without token, `403` for wrong role.
* `tests/unit/test_rbac.py` — dependency-override pattern, 4 tests.
* **Resolved:** `passlib 1.7.4` + `bcrypt 4.x` incompatibility fixed by importing `bcrypt` directly in `security.py` instead of using `passlib.hash.bcrypt`.

### Step 1.4 — CRUD API Tests ✅
* `tests/integration/test_device_api.py` — full API tests via `httpx.AsyncClient` for `GET /`, `GET /{id}`, `POST /`, `PUT /{id}`, `DELETE /{id}` — all roles, all error paths (404, 409, 422, 401).
* `tests/unit/test_device_service.py` — unit tests for `DeviceService.get_all`, `get_by_id`, `create`, `update`, `soft_delete` with mocked `AsyncSession`.
* `tests/unit/test_soft_delete.py` — focused soft-delete tests.

### Step 1.5 — Pagination, Sorting, Filtering ✅
* `DeviceService.get_all()` — `limit`, `offset`, `sort_by`, `sort_order`, `is_active`, `device_type`, `vendor`.
* `PaginatedResponse[DeviceOut]` schema — `{ items, total_count, limit, offset }`.
* Sortable fields whitelist: `id`, `name`, `ip_address`, `created_at`.

---

## PHASE 2 — Backend: Vault Integration

> **Goal:** Store device credentials (SNMP/SSH) safely in Vault, not plain-text in the database.

### Step 2.1 — VaultService

**Issue:** [#49](../../issues/49)

```bash
git checkout -b feat/49-vault-service
```

* `app/services/vault_service.py` — `VaultService` exposing `set_device_credentials` and `get_device_credentials`.
* Modify `POST /devices` and `PUT /devices` to accept optional `snmp_community` and `ssh_password`, saving them via Vault.
* Vault dev mode is already operational in `docker-compose`.

📖 [hvac — Python Vault client](https://hvac.readthedocs.io/en/stable/) | [Vault KV v2](https://developer.hashicorp.com/vault/docs/secrets/kv/kv-v2)

---

## PHASE 3 — Network Worker: Collector Refinement

> **Goal:** Ensure `network_worker` is a fully isolated, standalone service. ICMP, SNMP, and SSH execution must work flawlessly.

### Step 3.1 — Refine ICMP Collector

```bash
git checkout -b fix/icmp-device-id-propagation
```

* `device_icmp` task is not passing `device_id` to `_async_insert_ping_result` — fix this.
* `PingResult` is created without `device_id` in `monitoring_tasks.py` — fix this.
* Implement `tenacity` retry logic (3 attempts, exponential backoff).

### Step 3.2 — SNMP Collector: CPU/RAM

**Issue:** [#54](../../issues/54)

```bash
git checkout -b feat/54-snmp-cpu-ram
```

* Fetch credentials dynamically from Vault instead of using hardcoded `Config`.
* OIDs to track: CPU `1.3.6.1.4.1.2021.11.11.0`, RAM Total `1.3.6.1.4.1.2021.4.5.0`, RAM Available `1.3.6.1.4.1.2021.4.6.0`.

### Step 3.3 — SSH Executor

**Issue:** [#55](../../issues/55)

```bash
git checkout -b feat/55-ssh-executor
```

* `apps/network_worker/src/app/tasks/ssh_tasks.py` — Celery task `execute_ssh_command(device_id, command)` using Netmiko.
* Strict command whitelist.
* Credentials from Vault.

### Step 3.4 — Collector Testing

**Issue:** [#59](../../issues/59)

```bash
git checkout -b test/59-snmp-ssh-integration-tests
```

* SNMP integration tests using mocks.
* SSH integration tests via a mock server.

---

## PHASE 4 — Observability Stack

> **Goal:** Run the complete PLT stack (Prometheus + Loki + Tempo) locally for full visibility.

### Step 4.1 — Prometheus: FastAPI Metrics

**Issue:** [#63](../../issues/63)

```bash
git checkout -b fix/63-prometheus-target
```

`Instrumentator().instrument(app).expose(app)` is already in `main.py` ✅.
Fix `infrastructure/prometheus/prometheus.yml` — already done ✅ (target `backend:8000` is configured).

**Verification:** `http://localhost:9090/targets` → `backend:8000` should be UP.

### Step 4.2 — Loki + Promtail

**Issue:** [#72](../../issues/72)

```bash
git checkout -b feat/72-loki-promtail
```

* Add `loki` and `promtail` services to `docker-compose.dev.yml`.
* Mount Docker socket to collect logs from all containers.
* Add Loki as a Grafana datasource.

### Step 4.3 — Grafana Tempo + OpenTelemetry

**Issues:** [#73](../../issues/73) & [#74](../../issues/74)

```bash
git checkout -b feat/73-74-tempo-opentelemetry
```

* Add `tempo` service to `docker-compose`, add datasource to Grafana.
* `app/core/observability.py` — initialize the OTLP exporter pointing to Tempo.
* Add `opentelemetry-distro`, `opentelemetry-exporter-otlp`, `opentelemetry-instrumentation-fastapi`, `opentelemetry-instrumentation-sqlalchemy` to `requirements.txt`.

### Step 4.4 — Grafana Dashboards as Code

```bash
git checkout -b feat/grafana-dashboards-as-code
```

* `network-overview.json` — devices up/down, avg RTT, % reachable.
* `device-details.json` — template variable `$device`, showing RTT, CPU, RAM.

### Step 4.5 — Traefik Reverse Proxy

**Issue:** [#82](../../issues/82)

```bash
git checkout -b feat/82-traefik-reverse-proxy
```

* `sotp.localhost/` → Frontend.
* `sotp.localhost/api` → Backend.

---

## PHASE 5 — Frontend: Minimum Viable UI

> **Goal:** Ensure the project isn't strictly backend-only.

### Step 5.1 — Devices Table Connected to API

**Issue:** [#15](../../issues/15)

```bash
git checkout -b feat/15-devices-table-api
```

* `DevicesTable` component — currently scaffolded and commented out in `devices/page.tsx`.
* React Query `useQuery` → `GET /api/v1/devices`.
* Columns: Name, IP, Type, Status dot (green/red), Actions.
* Loading skeletons, error state.
* "Add Device" button — routing to `/devices/new` (already implemented ✅).

### Step 5.2 — Device Add/Edit Form ✅ (partially)

**Issue:** [#16](../../issues/16)

* `/devices/new` page is done — form with IP validation, POST to API, QueryClient invalidation ✅.
* Edit form (`PUT`) still needed.

### Step 5.3 — Auth Pages

**Issue:** [#51](../../issues/51)

```bash
git checkout -b feat/51-auth-pages
```

* `/login` page — email + password, calls `POST /api/v1/auth/login`.
* Zustand store with persist middleware — `accessToken`, `refreshToken`, `user`.
* Redirect to `/devices` on success.

### Step 5.4 — Route Protection

**Issue:** [#52](../../issues/52)

```bash
git checkout -b feat/52-route-protection
```

* Next.js Middleware or `AuthGuard` in `(dashboard)/layout.tsx`.
* Axios interceptor — `401` → refresh → retry.

### Step 5.5 — Device Page Metrics Tab

**Issue:** [#57](../../issues/57)

```bash
git checkout -b feat/57-device-metrics-tab
```

* Backend: `GET /api/v1/devices/{id}/metrics?metric_name=cpu&time_range=1h`.
* Frontend: `recharts` charts for RTT, CPU, RAM with time-range selector.

### Step 5.6 — UI Component Tests

**Issue:** [#18](../../issues/18)

```bash
git checkout -b test/18-ui-component-tests
```

* `DeviceTable` — renders data supplied via props.
* `DeviceForm` — validation triggers and submit handler.

---

## PHASE 6 — SOTP Agent

> **Goal:** Lightweight metric push agent to demonstrate Push vs. Pull monitoring.

### Step 6.1 — Metrics Ingestion Endpoint

**Issue:** [#87](../../issues/87)

```bash
git checkout -b feat/87-metrics-ingestion-endpoint
```

* `POST /api/v1/ingest/metrics` — persists to TimescaleDB `device_metrics`.
* Static API key auth in headers.

### Step 6.2 — Python Agent

**Issue:** [#86](../../issues/86)

```bash
git checkout -b feat/86-sotp-agent
```

* `apps/sotp_agent/agent.py` — collects CPU, RAM, disk, load averages via `psutil`.
* Pushes to `POST /api/v1/ingest/metrics` at N-second interval.
* Config via env vars: `SOTP_SERVER_URL`, `SOTP_API_KEY`, `COLLECT_INTERVAL`.

---

## PHASE 7 — Kubernetes

> **Goal:** SOTP runs on a local K3d cluster. Helm chart. GitOps via ArgoCD.

### Step 7.0 — docker-compose.prod.yml

**Issue:** [#2](../../issues/2) (reopened)

```bash
git checkout -b build/2-docker-compose-prod
```

* Pull images from GHCR, strip local code volumes, enforce health checks.

### Step 7.1 — Local K3d Cluster

```bash
git checkout -b build/k3d-local-cluster
```

* `scripts/k3d-cluster.sh` — bootstrap cluster + local registry.
* `Makefile` shortcuts: `make k3d-up`, `make k3d-down`, `make k3d-push`.

### Step 7.2 — Helm Chart

**Issue:** [#75](../../issues/75)

```bash
git checkout -b build/75-helm-chart
```

* `infrastructure/helm/sotp/` — templates for all microservices.
* `migrations-job.yaml` as `helm hook: pre-install` — Alembic runs before backend pods start.

### Step 7.3 — Database StatefulSets

* PostgreSQL and TimescaleDB as `StatefulSets` with PVCs.

### Step 7.4 — Vault in K8s

* Vault Agent Injector via pod annotations.

### Step 7.5 — GitOps with ArgoCD

**Issue:** [#76](../../issues/76)

```bash
git checkout -b feat/76-argocd-gitops
```

1. New repo `sotp-k8s-config` — move Helm chart there.
2. Install ArgoCD on K3d.
3. Deploy `infrastructure/argocd/application.yaml`.
4. CI pipeline commits updated `image.tag` to `sotp-k8s-config` after a successful build.

**Resulting workflow:** `git push` → CI builds image → commits to config repo → ArgoCD detects → deploys.

---

## PHASE 8 — Production Functionality

### Step 8.1 — Alert System
* `AlertService` evaluates rules against latest metrics (Celery task every 1 min).
* Notification channels: Email, Slack, webhook.

### Step 8.2 — Audit Middleware

**Issue:** [#77](../../issues/77)

* Middleware intercepts `POST` / `PUT` / `DELETE` — extracts `user_id` from JWT, writes to `audit_logs`.
* `/logs` view with filtering.

### Step 8.3 — Reporting System
* `ReportService` aggregates TimescaleDB data.
* Export: PDF (`WeasyPrint`) or CSV.
* `/reports` page with generation form and download links.

### Step 8.4 — In-App SSH Console
* `POST /api/v1/devices/{id}/execute` with command whitelist.
* "Console" tab showing near-real-time stdout/stderr.

### Step 8.5 — E2E Testing

**Issue:** [#62](../../issues/62)

```bash
git checkout -b test/62-e2e-tests
```

* Playwright tests: login flow, device creation, device details navigation.
* Run in CI post-build.

---

## PHASE 9 — Advanced Topics *(Choose 1–2)*

### 9.1 — Linkerd Service Mesh (mTLS)
Automatic mTLS between all microservices. Golden metrics (latency, error rate, traffic) for free.

### 9.2 — Advanced JWT Management

**Issue:** [#61](../../issues/61) — Token blacklisting via Redis + refresh token rotation.

### 9.3 — Closed-Loop Automation
Alertmanager webhook → Celery task → Netmiko auto-remediation.

### 9.4 — ML/AI: Anomaly Prediction
TimescaleDB Toolkit + Facebook Prophet — `predict_trends()` Celery task for proactive monitoring.

### 9.5 — Containerlab: Realistic Collector Tests

**Issue:** [#59](../../issues/59) — Virtual Arista cEOS routers in CI to test collectors against a real NOS.

### 9.6 — TextFSM + SSH Parser

**Issue:** [#60](../../issues/60) — Parse raw CLI output into structured JSON.

---

## Execution Order — TL;DR

```text
DONE ✅:
  Phase 1: JWT → RBAC → Auth Tests → CRUD Tests → Pagination

NOW:
  Phase 2: #49 Vault
  Phase 4: #72 Loki → #73+74 Tempo
  Phase 3: ICMP device_id fix → #54 SNMP → #55 SSH

THEN:
  Phase 5: #15 Devices Table → Edit Form → #51 Auth Pages → #52 Route Protection
  Phase 4: Dashboards as Code → #82 Traefik
  Phase 6: #87 Ingestion Endpoint → #86 SOTP Agent

KUBERNETES:
  Phase 7: #2 docker-compose.prod → K3d → #75 Helm → StatefulSets → Vault K8s → #76 ArgoCD

ADVANCED:
  Phase 8: Alerts → #77 Audit → Reports → SSH Console → #62 E2E Tests
  Phase 9: Pick 1–2 from #61, #59, #60, Linkerd, ML
```

---

## Working Rules

* **1 Step = 1 Branch + 1 PR** to `develop`.
* **Branch naming:** `feat/47-jwt-auth`, `fix/63-prometheus-target`, `test/53-auth-tests`.
* **Commit convention:** strictly follow `.github/COMMIT_COVENCTIONS.md`.
* **Merge requirement:** CI must be fully green.
* **Documentation:** after completing each phase, update `README.md`.

---

*Last updated: 2026-04-10 | Version: 3.1*
*Phase 1 — fully completed*
