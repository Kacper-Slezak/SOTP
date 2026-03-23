# SOTP — Project Roadmap v3.0

> **Goal:** Portfolio-ready network infrastructure monitoring platform — solo project.
> **Context:** SRE Intern CV project; Kubernetes (K8s) is a core component.
> **Rule:** Every step = separate branch + PR. Every step must have a dedicated GitHub issue.

-----

## Current Status (March 23, 2026)

All cleanup/stabilization tasks are **completed**:

* `apps/core_backend/` — Clean `main.py`, `DeviceService` utilized by the router, `DevicePut` in `schemas/devices.py`.
* `apps/network_worker/` — Isolated Celery service, `include=` bug fixed, `celery-worker`/`celery-beat` built natively from `network_worker`.
* **CI/CD** — `ci.yml` pipeline with quality + security + test + build + Discord notifications; all paths are consistent (`apps/core_backend`, `apps/web_frontend`, `apps/network_worker`).
* **Docker Compose** — Prometheus, Grafana, Vault, Redis, TimescaleDB, PostgreSQL, `celery-worker`, and `celery-beat` configured with the correct `working_dir`.
* **Testing** — `test_soft_delete.py` rewritten to use `DeviceService`, `test_icmp_all.py` removed from `core_backend`.

Phase 1 tasks **completed**:

* **JWT Authentication**
* **RBAC (Role-Based Access Control)**

**In progress:**

* **Auth Testing**

-----

## PHASE 1 — Backend: Auth & Security

> **Goal:** No public endpoints. End-to-end JWT + RBAC implementation.

### Step 1.1 — JWT Authentication

**Issue:** [\#47](https://www.google.com/search?q=../../issues/47)

```bash
git checkout -b feat/47-jwt-authentication
```

What to implement in `apps/core_backend/`:

* `app/core/security.py` — `create_access_token`, `create_refresh_token`, `decode_token` (using `python-jose`).
* `app/api/v1/auth.py` — `POST /api/v1/auth/register`, `/login`, `/refresh`.
* `app/api/dependencies.py` — `get_current_user` dependency validating the Bearer token.
* `app/schemas/auth.py` — `TokenResponse`, `LoginRequest`, `RegisterRequest`.
* Passwords hashed via `passlib[bcrypt]`.
* Secure `/api/v1/devices` using `Depends(get_current_user)`.

📖 [FastAPI — OAuth2 with JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) | [python-jose](https://python-jose.readthedocs.io/en/latest/) | [Video (ArjanCodes)](https://www.youtube.com/watch?v=5GxQ1rLTwaU)

### Step 1.2 — RBAC

**Issue:** [\#48](https://www.google.com/search?q=../../issues/48)

```bash
git checkout -b feat/48-rbac
```

* `app/api/dependencies.py` — `require_role(allowed_roles: list[UserRole])` dependency.
* `GET /devices` → ADMIN, OPERATOR, READONLY.
* `POST /devices` → ADMIN.
* `PUT /devices/{id}` → ADMIN, OPERATOR.
* `DELETE /devices/{id}` → ADMIN.
* `GET /api/v1/users/me` — Returns the current user and their role.

📖 [FastAPI — Dependencies in depth](https://fastapi.tiangolo.com/tutorial/dependencies/)

### Step 1.3 — Auth Tests

**Issue:** [\#53](https://www.google.com/search?q=../../issues/53)

```bash
git checkout -b test/53-auth-integration-tests
```

Tests to cover: Registration, login, token refresh, `401 Unauthorized` without a token, and `403 Forbidden` for insufficient roles.

📖 [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/) | [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/latest/)

### Step 1.4 — CRUD API Tests

**Issue:** [\#17](https://www.google.com/search?q=../../issues/17)

```bash
git checkout -b test/17-device-crud-tests
```

* Unit tests for `DeviceService.create`, `get_by_id`, `get_all`, `update` — mocking `AsyncSession`.
* API integration tests via `httpx.AsyncClient` for every endpoint.
* Target coverage \> 80%.

### Step 1.5 — Pagination, Sorting, Filtering

**Issue:** [\#44](https://www.google.com/search?q=../../issues/44)

```bash
git checkout -b feat/44-device-list-pagination
```

* `DeviceService.get_all()` must accept `limit`, `offset`, `sort_by`, `sort_order`, `is_active`, `device_type`, `vendor`.
* Expected API response structure: `{ "items": [...], "total_count": ..., "limit": ..., "offset": ... }`.

-----

## PHASE 2 — Backend: Vault Integration

> **Goal:** Store device credentials (SNMP/SSH) safely in Vault, not plain-text in the database.

### Step 2.1 — VaultService

**Issue:** [\#49](https://www.google.com/search?q=../../issues/49)

```bash
git checkout -b feat/49-vault-service
```

* `app/services/vault_service.py` — `VaultService` exposing `set_device_credentials` and `get_device_credentials`.
* Modify `POST /devices` and `PUT /devices` to accept optional `snmp_community` and `ssh_password`, saving them directly via Vault.
* Vault dev mode is already operational in `docker-compose`.

📖 [hvac — Python Vault client](https://hvac.readthedocs.io/en/stable/) | [Vault KV v2](https://developer.hashicorp.com/vault/docs/secrets/kv/kv-v2) | [Video (TechWorld with Nana)](https://www.youtube.com/watch?v=ci_0TrDN8C0)

-----

## PHASE 3 — Network Worker: Collector Refinement

> **Goal:** Ensure `network_worker` is a fully isolated, standalone service. ICMP, SNMP, and SSH execution must work flawlessly.

### Step 3.1 — Refine ICMP Collector

**Issue:** *None — create via `gh issue create` with title `[FIX] ICMP device_id not propagated to PingResult`*

```bash
git checkout -b fix/icmp-device-id-propagation
```

* `device_icmp` is not passing `device_id` to `insert_ping_result` — fix this.
* `_async_insert_ping_result` is not setting `device_id` inside `PingResult` — fix this.
* Implement `tenacity` retry logic (3 attempts, exponential backoff).

📖 [tenacity — retry library](https://tenacity.readthedocs.io/en/latest/)

### Step 3.2 — SNMP Collector: CPU/RAM

**Issue:** [\#54](https://www.google.com/search?q=../../issues/54)

```bash
git checkout -b feat/54-snmp-cpu-ram
```

* Fetch credentials dynamically from Vault instead of using a hardcoded `Config`.
* OIDs to track: CPU `1.3.6.1.4.1.2021.11.11.0`, RAM Total `1.3.6.1.4.1.2021.4.5.0`, RAM Available `1.3.6.1.4.1.2021.4.6.0`.

📖 [pysnmp](https://pysnmp.readthedocs.io/en/latest/) | [SNMP OID reference](https://www.oid-info.com/)

### Step 3.3 — SSH Executor

**Issue:** [\#55](https://www.google.com/search?q=../../issues/55)

```bash
git checkout -b feat/55-ssh-executor
```

* Location: `apps/network_worker/src/app/tasks/ssh_tasks.py`.
* Create a Celery task `execute_ssh_command(device_id, command)` using `netmiko`.
* Implement a strict whitelist of allowed commands.
* Fetch device credentials securely from Vault.

📖 [netmiko](https://github.com/ktbyers/netmiko) | [ntc-templates](https://github.com/networktocode/ntc-templates)

### Step 3.4 — Collector Testing

**Issue:** [\#59](https://www.google.com/search?q=../../issues/59)

```bash
git checkout -b test/59-snmp-ssh-integration-tests
```

* SNMP integration tests using `snmpsim` or mocks.
* SSH integration tests via a mock server.
* Must be able to execute successfully within the CI pipeline.

-----

## PHASE 4 — Observability Stack

> **Goal:** Run the complete PLT stack (Prometheus + Loki + Tempo) locally for full visibility.

### Step 4.1 — Prometheus: FastAPI Metrics

**Issue:** [\#63](https://www.google.com/search?q=../../issues/63)

```bash
git checkout -b fix/63-prometheus-target
```

`Instrumentator().instrument(app).expose(app)` is already configured in `main.py` ✅.
You just need to fix `infrastructure/prometheus/prometheus.yml`:

```yaml
- job_name: 'backend'
  static_configs:
    - targets: ['backend:8000']
```

**Verification:** Check `http://localhost:9090/targets` → `backend:8000` should be UP.

📖 [prometheus-fastapi-instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator) | [PromQL Tutorial](https://promlabs.com/promql-tutorial/)

### Step 4.2 — Loki + Promtail

**Issue:** [\#72](https://www.google.com/search?q=../../issues/72)

```bash
git checkout -b feat/72-loki-promtail
```

Add to `docker-compose.dev.yml`:

* `loki` service (`grafana/loki:latest`, port 3100).
* `promtail` service — mount the Docker socket to collect logs from all containers.
* Add Loki as a native Datasource inside Grafana.

📖 [Loki Docker Compose](https://grafana.com/docs/loki/latest/setup/install/docker/) | [Video (TechWorld with Nana)](https://www.youtube.com/watch?v=h_GGd7HfKQ8)

### Step 4.3 — Grafana Tempo + OpenTelemetry

**Issues:** [\#73](https://www.google.com/search?q=../../issues/73) & [\#74](https://www.google.com/search?q=../../issues/74)

```bash
git checkout -b feat/73-74-tempo-opentelemetry
```

**Infrastructure:** Add `tempo` service to `docker-compose`, add datasource to Grafana.
**Backend Instrumentation:**

* Add to `requirements.txt`: `opentelemetry-distro`, `opentelemetry-exporter-otlp`, `opentelemetry-instrumentation-fastapi`, `opentelemetry-instrumentation-sqlalchemy`.
* `app/core/observability.py` — Initialize the OTLP exporter pointing to Tempo.
* Call the initializer on startup in `main.py`.

📖 [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/getting-started/) | [Grafana Tempo](https://grafana.com/docs/tempo/latest/getting-started/) | [Video (ByteByteGo)](https://www.youtube.com/watch?v=LAgI8vHKeeg)

### Step 4.4 — Grafana Dashboards as Code

**Issue:** *None — create via `gh issue create` with title `[INFRA] Grafana dashboards as provisioned JSON`*

```bash
git checkout -b feat/grafana-dashboards-as-code
```

* `network-overview.json` — Devices up/down, avg RTT, % reachable.
* `device-details.json` — Template variable `$device`, showing specific RTT, CPU, RAM.

📖 [Grafana Dashboard JSON](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/view-dashboard-json-model/) | [Grafana Provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/#dashboards)

### Step 4.5 — Traefik Reverse Proxy

**Issue:** [\#82](https://www.google.com/search?q=../../issues/82)

```bash
git checkout -b feat/82-traefik-reverse-proxy
```

* `sotp.localhost/` → Routes to Frontend.
* `sotp.localhost/api` → Routes to Backend.
* This architecture inherently solves frontend-backend CORS issues.

📖 [Traefik Docker Provider](https://doc.traefik.io/traefik/providers/docker/) | [Video (TechWorld with Nana)](https://www.youtube.com/watch?v=C6IL8tjwC5E)

-----

## PHASE 5 — Frontend: Minimum Viable UI

> **Goal:** Ensure the project isn't strictly backend-only. Utilize LLMs to accelerate component drafting.

### Step 5.1 — Devices Table Connected to API

**Issue:** [\#15](https://www.google.com/search?q=../../issues/15)

```bash
git checkout -b feat/15-devices-table-api
```

* Use React Query `useQuery` → `GET /api/v1/devices`.
* Table Columns: Name, IP, Type, Status (green/red indicator dot), Actions.
* Implement loading skeletons and error states.
* "Add Device" button routing to `/devices/new`.

### Step 5.2 — Device Add/Edit Form

**Issue:** [\#16](https://www.google.com/search?q=../../issues/16)

```bash
git checkout -b feat/16-device-form
```

* Form featuring strict validation (e.g., proper IP formatting).
* Handles `POST` / `PUT` via `/api/v1/devices`.
* Toast notifications for success or failure.
* Trigger an automatic list refresh upon successful addition.

### Step 5.3 — Auth Pages

**Issue:** [\#51](https://www.google.com/search?q=../../issues/51)

```bash
git checkout -b feat/51-auth-pages
```

* `/login` page — Email + Password layout, triggering `POST /api/v1/auth/login`.
* Implement a Zustand store with the persist middleware holding: `accessToken`, `refreshToken`, `user`.
* Automatic redirect to `/devices` upon successful authentication.

### Step 5.4 — Route Protection

**Issue:** [\#52](https://www.google.com/search?q=../../issues/52)

```bash
git checkout -b feat/52-route-protection
```

* Utilize Next.js Middleware or an `AuthGuard` wrapper inside `(dashboard)/layout.tsx`.
* Unauthorized users are redirected to `/login`.
* Set up an Axios interceptor: `401 Unauthorized` → attempt token refresh → retry original request.

### Step 5.5 — Device Page Metrics Tab

**Issue:** [\#57](https://www.google.com/search?q=../../issues/57)

```bash
git checkout -b feat/57-device-metrics-tab
```

* **Backend:** Endpoint `GET /api/v1/devices/{id}/metrics?metric_name=cpu&time_range=1h`.
* **Frontend:** `recharts` visualizations for RTT, CPU, and RAM with a time-range selector.

### Step 5.6 — UI Component Tests

**Issue:** [\#18](https://www.google.com/search?q=../../issues/18)

```bash
git checkout -b test/18-ui-component-tests
```

* `DeviceTable` tests — Ensure it properly renders data supplied via props.
* `DeviceForm` tests — Verify validation triggers and submit handler behavior.

📖 [TanStack Query](https://tanstack.com/query/latest/docs/framework/react/overview) | [Zustand persist](https://zustand.docs.pmnd.rs/integrations/persisting-store-data) | [Next.js Middleware](https://nextjs.org/docs/app/building-your-application/routing/middleware)

-----

## PHASE 6 — SOTP Agent

> **Goal:** Build a lightweight metric push agent to demonstrate understanding of Push vs. Pull monitoring models.

### Step 6.1 — Metrics Ingestion Endpoint

**Issue:** [\#87](https://www.google.com/search?q=../../issues/87)

```bash
git checkout -b feat/87-metrics-ingestion-endpoint
```

* `app/api/v1/ingest.py` — `POST /api/v1/ingest/metrics`.
* Persists data natively to TimescaleDB (`device_metrics` table).
* Secured via static API key in the headers (no JWT overhead required here).

### Step 6.2 — Python Agent

**Issue:** [\#86](https://www.google.com/search?q=../../issues/86)

```bash
git checkout -b feat/86-sotp-agent
```

* `apps/sotp_agent/agent.py` — Gathers CPU, RAM, disk space, and load averages (using `psutil`).
* Pushes payload to `POST /api/v1/ingest/metrics` at an N-second interval.
* Configured via environment variables: `SOTP_SERVER_URL`, `SOTP_API_KEY`, `COLLECT_INTERVAL`.
* Packaged to run easily as either a Docker container or a systemd service.

📖 [psutil](https://psutil.readthedocs.io/en/latest/) | [schedule library](https://schedule.readthedocs.io/en/stable/) | [systemd service](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

-----

## PHASE 7 — Kubernetes

> **Goal:** SOTP runs smoothly on a local K3d cluster. Helm chart implementation. GitOps utilizing ArgoCD.

### Step 7.0 — docker-compose.prod.yml

**Issue:** [\#2](https://www.google.com/search?q=../../issues/2) (reopened)

```bash
git checkout -b build/2-docker-compose-prod
```

Configure to pull images from GHCR, strip out all local code volume mounts, and enforce mandatory health checks.

### Step 7.1 — Local K3d Cluster

**Issue:** *Create `[BUILD] k3d local cluster setup script`*

```bash
git checkout -b build/k3d-local-cluster
```

* `scripts/k3d-cluster.sh` — Script to bootstrap the cluster alongside a local image registry.
* `Makefile` shortcuts: `make k3d-up`, `make k3d-down`, `make k3d-push`.

📖 [k3d Quick Start](https://k3d.io/v5.7.5/usage/commands/k3d_cluster_create/) | [Video: k3d](https://www.youtube.com/watch?v=mCesuGk-Fks)

### Step 7.2 — Helm Chart

**Issue:** [\#75](https://www.google.com/search?q=../../issues/75)

```bash
git checkout -b build/75-helm-chart
```

* Build `infrastructure/helm/sotp/` containing templates for all microservices.
* **Crucial implementation:** `migrations-job.yaml` must be set as a `helm hook: pre-install` to ensure Alembic migrations execute BEFORE the backend deployments spin up.

📖 [Helm Chart Template Guide](https://helm.sh/docs/chart_template_guide/getting_started/) | [Helm Hooks](https://helm.sh/docs/topics/charts_hooks/) | [Video (TechWorld with Nana)](https://www.youtube.com/watch?v=-ykwb1d0DXU)

### Step 7.3 — Database StatefulSets

**Issue:** *Create `[BUILD] K8s StatefulSets for PostgreSQL and TimescaleDB`*
Deploy PostgreSQL and TimescaleDB properly as `StatefulSets` backed by Persistent Volume Claims (PVCs).

📖 [K8s StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) | [PersistentVolumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)

### Step 7.4 — Vault in K8s

**Issue:** *Create `[BUILD] Vault Agent Injector in K8s`*
Mount secrets natively into pods utilizing the Vault Agent Injector (via pod annotations) instead of relying on plain-text K8s Secrets.

📖 [Vault Kubernetes Auth](https://developer.hashicorp.com/vault/docs/auth/kubernetes) | [Vault Agent Injector](https://developer.hashicorp.com/vault/docs/platform/k8s/injector)

### Step 7.5 — GitOps with ArgoCD

**Issue:** [\#76](https://www.google.com/search?q=../../issues/76) *(closed — reopen or recreate)*

```bash
git checkout -b feat/76-argocd-gitops
```

1. Initialize a new repository: `sotp-k8s-config` and move the Helm chart there.
2. Install ArgoCD on the K3d cluster.
3. Deploy `infrastructure/argocd/application.yaml`.
4. Configure the CI pipeline so that after a successful image build, it automatically pushes a commit updating the `image.tag` inside `sotp-k8s-config`.

**Resulting Workflow:** `git push` → CI Pipeline Builds → Commits to Config Repo → ArgoCD detects change → Automated cluster deployment.

📖 [ArgoCD Getting Started](https://argo-cd.readthedocs.io/en/stable/getting_started/) | [Video (TechWorld with Nana)](https://www.youtube.com/watch?v=MeU5_k9ssrs) | [Killercoda ArgoCD labs](https://killercoda.com/killer-shell-ckad)

-----

## PHASE 8 — Production Functionality

> **Goal:** Polish the system into a complete platform — alerting, audit trails, reporting, and interactive SSH capabilities.

### Step 8.1 — Alert System

**Issue:** *Create `[FEAT] Alert evaluation service and notification channels`*

* `AlertService` periodically evaluates custom rules against the latest polled metrics (via a Celery task every 1 minute).
* Alertmanager webhook target → `POST /api/v1/webhooks/alerts`.
* Supported Notification Channels: Email, Slack, generic webhook.

📖 [Prometheus Alertmanager](https://prometheus.io/docs/alerting/latest/configuration/)

### Step 8.2 — Audit Middleware

**Issue:** [\#77](https://www.google.com/search?q=../../issues/77)

* FastAPI middleware to intercept all `POST` / `PUT` / `DELETE` requests.
* Extracts the `user_id` from the JWT and records the action into `audit_logs`.
* **UI Integration:** `/logs` view with actionable filtering.

### Step 8.3 — Reporting System

**Issue:** *Create `[FEAT] Report generation API and UI`*

* `ReportService` to intelligently aggregate historical data from TimescaleDB.
* Export options: PDF (using `WeasyPrint`) or raw CSV.
* **UI Integration:** `/reports` page featuring an interactive generation form and download links.

### Step 8.4 — In-App SSH Console

**Issue:** *Create `[FEAT] SSH console tab on device details page`*

* Backend endpoint `POST /api/v1/devices/{id}/execute` (strictly enforcing command whitelists).
* **UI Integration:** "Console" tab displaying near real-time stdout/stderr output.
* Directly links to backend logic established in Step 3.3.

### Step 8.5 — End-to-End (E2E) Testing

**Issue:** [\#62](https://www.google.com/search?q=../../issues/62)

```bash
git checkout -b test/62-e2e-tests
```

* Implement `Playwright` tests covering: The login flow, device creation, and successful navigation to the device details view.
* Automate test execution within the CI pipeline post-build.

-----

## PHASE 9 — Advanced Topics *(Choose 1-2)*

> **Goal:** Develop flagship features that make the project stand out technically.

### 9.1 — Linkerd Service Mesh (mTLS)

Inject an automatic mTLS layer between all microservices. Out-of-the-box Golden Metrics (Latency, Error Rate, Traffic) for inter-service communication.
📖 [Linkerd Getting Started](https://linkerd.io/2.14/getting-started/)

### 9.2 — Advanced JWT Management

**Issue:** [\#61](https://www.google.com/search?q=../../issues/61) — Implement strict token blacklisting via Redis and refresh token rotation logic.

### 9.3 — Closed-Loop Automation (Auto-remediation)

Architect a flow where Alertmanager triggers a webhook → kicks off a Celery task → Netmiko logs in and executes a script to automatically resolve the recognized network issue.

### 9.4 — ML/AI: Anomaly Prediction

Incorporate TimescaleDB Toolkit + Facebook's Prophet framework. Create a `predict_trends()` Celery task to shift the monitoring paradigm from reactive to proactive.

### 9.5 — Containerlab: Realistic Collector Tests

**Issue:** [\#59](https://www.google.com/search?q=../../issues/59) — Spin up virtual Arista cEOS network routers directly within the CI pipeline to test data collection against actual NOS behavior.
📖 [Containerlab](https://containerlab.dev/quickstart/)

### 9.6 — TextFSM + SSH Parser

**Issue:** [\#60](https://www.google.com/search?q=../../issues/60) — Parse unstructured raw CLI output from SSH sessions into strictly formatted JSON objects for data modeling.

-----

## Execution Order — TL;DR

```text
NOW:
  Phase 1: #47 JWT → #48 RBAC → #53 Auth Tests → #17 CRUD Tests → #44 Pagination

NEXT:
  Phase 2: #49 Vault
  Phase 4: #63 Prometheus fix (just 2 lines!) → #72 Loki → #73+#74 Tempo
  Phase 3: ICMP fix → #54 SNMP → #55 SSH

THEN:
  Phase 5: #15 Devices Table → #16 UI Form → #51 Auth Pages → #52 Route Protection
  Phase 4: Dashboards as Code → #82 Traefik
  Phase 6: #87 Ingestion Endpoint → #86 SOTP Agent

KUBERNETES:
  Phase 7: #2 docker-compose.prod → K3d → #75 Helm → StatefulSets → Vault K8s → #76 ArgoCD

ADVANCED:
  Phase 8: Alerts → #77 Audit → Reports → SSH Console → #62 E2E Tests
  Phase 9: Pick 1-2 items from #61, #59, #60, Linkerd, ML
```

-----

## Working Rules

* **1 Step = 1 Branch + 1 PR** to the `develop` branch.
* **Branch Naming Convention:** `feat/47-jwt-auth`, `fix/63-prometheus-target`, `test/53-auth-tests`.
* **Commit Convention:** Strictly adhere to `.github/COMMIT_COVENCTIONS.md`.
* **Merge Requirements:** The CI pipeline must be fully green before any merge.
* **Documentation:** After completing each phase, update the `README.md` to reflect the new state.

-----

*Last updated: 2026-03-23 | Version: 3.0*
*Phase 0 (Cleanup) — completed ✅*
