# SOTP — Project Roadmap v4.0

> **Goal:** Portfolio-ready network infrastructure monitoring platform — solo project.
> **Target Role:** SRE / Cloud / DevSecOps Engineer.
> **Core Architecture:** Kubernetes (K3d) + Helm + ArgoCD GitOps + PLT Observability + DevSecOps Pipeline + AWS IaC (plan-only).
> **Execution Rule:** 1 issue = 1 branch = 1 PR to `main` · CI must be green · Title format: `[Phase][Area] Task` · Work top-down from P0 to P8.

---

## Roadmap Overview & Milestones

The v4 roadmap is organized into 9 sequential phases corresponding to GitHub milestones. Within each phase, tasks are prioritized: 🔴 Critical → 🟠 High → 🟡 Medium → ⚪ Low.

| Phase | Milestone | Focus | Key Deliverable |
| :--- | :--- | :--- | :--- |
| **P0** | [Milestone 1 · P0 · Cleanup & Truth](https://github.com/Kacper-Slezak/SOTP/milestone/1) | Hygiene & ADRs | Honest tracker, clean tree, architectural decision records |
| **P1** | [Milestone 2 · P1 · Works End-to-End](https://github.com/Kacper-Slezak/SOTP/milestone/2) | Core Loop | `make dev` → `make seed` → UI table → Grafana ICMP ping charts |
| **P2** | [Milestone 3 · P2 · DevSecOps Pipeline](https://github.com/Kacper-Slezak/SOTP/milestone/3) | Supply Chain | Gitleaks, Trivy, pip-audit, CodeQL, Cosign signing, SLSA SBOM |
| **P3** | [Milestone 4 · P3 · Kubernetes (K3d + Helm)](https://github.com/Kacper-Slezak/SOTP/milestone/4) | Container Platform | Umbrella Helm chart, CloudNativePG, NetworkPolicies, KEDA |
| **P4** | [Milestone 5 · P4 · GitOps, Secrets & Policy](https://github.com/Kacper-Slezak/SOTP/milestone/5) | GitOps & Security | ArgoCD app-of-apps, Vault + External Secrets, Kyverno policy |
| **P5** | [Milestone 6 · P5 · Observability & SRE](https://github.com/Kacper-Slezak/SOTP/milestone/6) | Production SRE | Loki + Alloy, Tempo OTel tracing, Sloth SLOs & burn alerts |
| **P6** | [Milestone 7 · P6 · Cloud IaC (AWS, plan-only)](https://github.com/Kacper-Slezak/SOTP/milestone/7) | Cloud Architecture | Terraform VPC, EKS, RDS, ECR (validated in CI, $0 cloud cost) |
| **P7** | [Milestone 8 · P7 · Product Features](https://github.com/Kacper-Slezak/SOTP/milestone/8) | Network Features | SNMP Vault creds, SSH executor, SOTP agent, metrics UI |
| **P8** | [Milestone 9 · P8 · Advanced / Stretch](https://github.com/Kacper-Slezak/SOTP/milestone/9) | Flagship Topics | Istio ambient mTLS, Chaos Mesh, k6 load testing, Containerlab |

---

## Current Status (October 2026)

**Foundation Completed ✅:**
* **Authentication & RBAC:** JWT registration, login, refresh tokens, role-based dependency `require_role()` across device endpoints. Password hashing switched from passlib to native `bcrypt`.
* **Device CRUD API:** Endpoints for list, get, create, update, and soft delete with pagination, sorting, and filtering (`limit`, `offset`, `sort_by`, `sort_order`). Unit and integration tests with mocked `AsyncSession` and `httpx.AsyncClient`.
* **Multi-service Monorepo:** Structured as `apps/core_backend`, `apps/network_worker`, `apps/web_frontend`, and `apps/sotp_agent`.
* **Docker Compose Dev Stack:** PostgreSQL, TimescaleDB, Redis, Vault, Prometheus, Grafana, Celery worker + beat.
* **Database Migrations:** Dual-branch Alembic migrations supporting PostgreSQL relational tables and TimescaleDB hypertables (`ping_results`).
* **Frontend App Shell:** Next.js 15 App Router layout, navigation, and `/devices/new` add-device page with IP validation.
* **Prometheus Instrumentator:** FastAPI middleware exporting `/metrics` target ([#63](https://github.com/Kacper-Slezak/SOTP/issues/63)).

**Active Focus:**
* **Phase P0 (In Progress):** Cleaning up obsolete artifacts, stale branches, and establishing the ADR baseline.

---

## PHASE P0 — Cleanup & Truth
> **Milestone:** [P0 · Cleanup & Truth](https://github.com/Kacper-Slezak/SOTP/milestone/1)
> **Goal:** Align tracker, repository, and roadmap with reality.

### Step 0.1 — Repository & Tracker Hygiene
* **Issue:** [#115](https://github.com/Kacper-Slezak/SOTP/issues/115) 🟠 *High*
* **Branch:** `chore/115-repo-cleanup`
* Remove obsolete root files (`errors.txt`, `issues.json`, `scripts/resturkturyzacjia.sh`, unused root locks) and enforce `.gitignore`.
* Delete dead remote/local branches.
* Enforce trunk-based development on `main`.
* Update roadmap and convert all remaining Polish workflow text to English.

### Step 0.2 — Architecture Decision Records (ADR)
* **Issue:** [#116](https://github.com/Kacper-Slezak/SOTP/issues/116) 🟡 *Medium*
* **Branch:** `docs/116-adr-folder`
* Create `docs/adr/` with template (Context, Decision, Consequences).
* Seed initial ADRs:
  * `ADR-001`: Monorepo structure (`apps/`)
  * `ADR-002`: PostgreSQL vs. TimescaleDB database split
  * `ADR-003`: Celery with Redis for asynchronous collectors
  * `ADR-004`: Local K3d cluster + AWS Terraform (plan-only)
  * `ADR-005`: GitOps repository structure

---

## PHASE P1 — Works End-to-End
> **Milestone:** [P1 · Works End-to-End](https://github.com/Kacper-Slezak/SOTP/milestone/2)
> **Goal:** Complete core end-to-end loop: `make dev` → `make seed` → UI displays devices → Grafana plots ICMP pings. CI fails on any test failure.

### Step 1.1 — Network Worker Import Refactor
* **Issue:** [#117](https://github.com/Kacper-Slezak/SOTP/issues/117) 🔴 *Critical*
* **Branch:** `fix/117-worker-shared-imports`
* Extract shared database sessions and models into an importable shared package or properly decouple `network_worker`.
* Resolve `ModuleNotFoundError: No module named 'app.db'` so worker tests run standalone.

### Step 1.2 — Celery Worker & Beat Scheduling
* **Issue:** [#104](https://github.com/Kacper-Slezak/SOTP/issues/104) 🔴 *Critical*
* **Branch:** `fix/104-celery-worker-beat`
* Correct Celery application import path, configure Beat schedules, and ensure `celery-worker` starts cleanly in `docker-compose.dev.yml`.

### Step 1.3 — CI Testing Gate
* **Issue:** [#107](https://github.com/Kacper-Slezak/SOTP/issues/107) 🔴 *Critical*
* **Branch:** `ci/107-strict-test-gate`
* Remove `continue-on-error: true` from pytest steps in `.github/workflows/ci.yml`.
* Provide PostgreSQL and TimescaleDB service containers in CI so auth and worker integration tests pass reliably.

### Step 1.4 — Wire Devices Table to API
* **Issue:** [#15](https://github.com/Kacper-Slezak/SOTP/issues/15) 🔴 *Critical*
* **Branch:** `feat/15-wire-devices-table`
* Uncomment and implement `<DevicesTable />` on `/devices` page.
* Connect to `GET /api/v1/devices` using `@tanstack/react-query` with loading skeletons and error handling.

### Step 1.5 — Minimal Login Page & Auth Storage
* **Issue:** [#51](https://github.com/Kacper-Slezak/SOTP/issues/51) 🟠 *High*
* **Branch:** `feat/51-login-page`
* Implement `/login` page and persist JWT tokens in Zustand store with Axios interceptor headers so authenticated API calls succeed.

### Step 1.6 — Database Seeding Script
* **Issue:** [#105](https://github.com/Kacper-Slezak/SOTP/issues/105) 🟠 *High*
* **Branch:** `fix/105-seed-demo-data`
* Fix script imports in `scripts/seed-demo-data.py` to seed demo network devices and default admin credentials (`admin@sotp.local`).

### Step 1.7 — Backend Security Quick Wins
* **Issue:** [#118](https://github.com/Kacper-Slezak/SOTP/issues/118) 🟠 *High*
* **Branch:** `fix/118-security-quick-wins`
* Tighten default secrets, enforce environment variable validation, and secure auth endpoints.

### Step 1.8 — End-to-End Demo Documentation
* **Issue:** [#119](https://github.com/Kacper-Slezak/SOTP/issues/119) 🟠 *High*
* **Branch:** `docs/119-e2e-demo-guide`
* Record demo walkthrough GIF/screenshot and update README with quickstart (`make dev` → `make seed` → login).

---

## PHASE P2 — DevSecOps Pipeline
> **Milestone:** [P2 · DevSecOps Pipeline](https://github.com/Kacper-Slezak/SOTP/milestone/3)
> **Goal:** Secure the software supply chain: secret scanning, SAST, SCA, hardened container images, container vulnerability scanning, SBOM, cryptographic signing, and GHCR publishing.

### Step 2.1 — Production Dockerfiles & Compose
* **Issue:** [#106](https://github.com/Kacper-Slezak/SOTP/issues/106) 🟠 *High*
* **Branch:** `build/106-docker-compose-prod`
* Build production-grade images without source mounts; maintain `infrastructure/docker/docker-compose.prod.yml`.

### Step 2.2 — Secret Scanning with Gitleaks
* **Issue:** [#120](https://github.com/Kacper-Slezak/SOTP/issues/120) 🟠 *High*
* **Branch:** `sec/120-gitleaks-secret-scanning`
* Integrate `gitleaks` into pre-commit configuration and CI workflow to block committed credentials.

### Step 2.3 — Container Hardening & Hadolint
* **Issue:** [#121](https://github.com/Kacper-Slezak/SOTP/issues/121) 🟠 *High*
* **Branch:** `build/121-harden-dockerfiles`
* Enforce non-root users (`USER appuser`), pin base image digests, and add `hadolint` to CI.

### Step 2.4 — Container Image Scanning with Trivy
* **Issue:** [#122](https://github.com/Kacper-Slezak/SOTP/issues/122) 🟠 *High*
* **Branch:** `sec/122-trivy-image-scan`
* Scan container images in CI using Trivy; fail build on unpatched `HIGH` or `CRITICAL` vulnerabilities.

### Step 2.5 — GHCR Publishing with SHA & Semver
* **Issue:** [#125](https://github.com/Kacper-Slezak/SOTP/issues/125) 🟠 *High*
* **Branch:** `ci/125-ghcr-image-publishing`
* Publish images to `ghcr.io/kacper-slezak/sotp-{backend,worker,frontend}` tagged with Git commit SHA on `main` and semver on release tags.

### Step 2.6 — SBOM & Image Signing (Cosign + Syft)
* **Issue:** [#126](https://github.com/Kacper-Slezak/SOTP/issues/126) 🟠 *High*
* **Branch:** `sec/126-sbom-cosign-signing`
* Generate Software Bill of Materials (SBOM) with Syft and sign images keylessly with Cosign in GitHub Actions (SLSA provenance).

### Step 2.7 — Dependency Vulnerability Scanning (SCA)
* **Issue:** [#123](https://github.com/Kacper-Slezak/SOTP/issues/123) 🟡 *Medium*
* **Branch:** `sec/123-sca-pip-audit-npm`
* Replace legacy `safety` with `pip-audit` for Python and configure `npm audit` for frontend; enable Dependabot/Renovate.

### Step 2.8 — SAST with GitHub CodeQL & Bandit
* **Issue:** [#124](https://github.com/Kacper-Slezak/SOTP/issues/124) 🟡 *Medium*
* **Branch:** `sec/124-codeql-sast`
* Enable GitHub CodeQL analysis for Python and TypeScript/JavaScript alongside Bandit.

### Step 2.9 — Branch Protection & Conventional Commits
* **Issue:** [#127](https://github.com/Kacper-Slezak/SOTP/issues/127) 🟡 *Medium*
* **Branch:** `ci/127-branch-protection-rules`
* Add CI PR linting for conventional commit titles and enforce green status checks on `main`.

### Step 2.10 — DAST Baseline Scan (OWASP ZAP)
* **Issue:** [#128](https://github.com/Kacper-Slezak/SOTP/issues/128) ⚪ *Low*
* **Branch:** `sec/128-owasp-zap-dast`
* Execute OWASP ZAP baseline scan against the ephemeral running API in CI.

---

## PHASE P3 — Kubernetes (K3d + Helm)
> **Milestone:** [P3 · Kubernetes (K3d + Helm)](https://github.com/Kacper-Slezak/SOTP/milestone/4)
> **Goal:** Run SOTP locally on K3d via an umbrella Helm chart, with production-grade operators, security baselines, and CI smoke tests.

### Step 3.1 — Local K3d Cluster Bootstrap
* **Issue:** [#129](https://github.com/Kacper-Slezak/SOTP/issues/129) 🔴 *Critical*
* **Branch:** `k8s/129-k3d-bootstrap`
* Script local cluster setup (`scripts/k3d-cluster.sh`) with local image registry and Makefile targets (`make k3d-up`, `make k3d-down`).

### Step 3.2 — Umbrella Helm Chart
* **Issue:** [#75](https://github.com/Kacper-Slezak/SOTP/issues/75) 🔴 *Critical*
* **Branch:** `k8s/75-helm-chart`
* Create `infrastructure/helm/sotp/` packaging `core_backend`, `network_worker`, `celery_beat`, and `web_frontend`.
* Use Helm pre-install hooks for Alembic migration jobs.

### Step 3.3 — Traefik Ingress & TLS (cert-manager)
* **Issue:** [#82](https://github.com/Kacper-Slezak/SOTP/issues/82) 🟠 *High*
* **Branch:** `k8s/82-ingress-traefik-tls`
* Route `https://sotp.localhost/` to frontend and `https://sotp.localhost/api` to backend; manage self-signed certificates with cert-manager.

### Step 3.4 — CloudNativePG Operator for Databases
* **Issue:** [#130](https://github.com/Kacper-Slezak/SOTP/issues/130) 🟠 *High*
* **Branch:** `k8s/130-cloudnative-pg-operator`
* Deploy PostgreSQL and TimescaleDB on Kubernetes using the CloudNativePG operator with automated failover and PVC management.

### Step 3.5 — Kubernetes Security Baseline
* **Issue:** [#131](https://github.com/Kacper-Slezak/SOTP/issues/131) 🟠 *High*
* **Branch:** `sec/131-k8s-security-baseline`
* Enforce Pod Security Standards (`restricted`), apply strict `securityContext` (read-only root filesystem, drop capabilities), and configure default-deny NetworkPolicies.

### Step 3.6 — CI Ephemeral Cluster Smoke Tests
* **Issue:** [#133](https://github.com/Kacper-Slezak/SOTP/issues/133) 🟠 *High*
* **Branch:** `ci/133-k8s-ephemeral-smoke-test`
* Spin up ephemeral `kind`/`k3d` cluster in GitHub Actions to test `helm install` and verify healthy readiness probes.

### Step 3.7 — Autoscaling: HPA & KEDA
* **Issue:** [#132](https://github.com/Kacper-Slezak/SOTP/issues/132) 🟡 *Medium*
* **Branch:** `k8s/132-autoscaling-hpa-keda`
* Configure Horizontal Pod Autoscaler (HPA) on backend CPU and KEDA scaler for network worker based on Redis Celery queue length.

---

## PHASE P4 — GitOps, Secrets & Policy
> **Milestone:** [P4 · GitOps, Secrets & Policy](https://github.com/Kacper-Slezak/SOTP/milestone/5)
> **Goal:** Continuous delivery via ArgoCD, secret synchronization via Vault and External Secrets Operator, and cluster policy enforcement with Kyverno.

### Step 4.1 — HashiCorp Vault Integration (`VaultService`)
* **Issue:** [#49](https://github.com/Kacper-Slezak/SOTP/issues/49) 🟠 *High*
* **Branch:** `sec/49-vault-service`
* Implement `apps/core_backend/app/services/vault_service.py` to store SNMP community strings and SSH credentials in Vault KV v2 instead of PostgreSQL.

### Step 4.2 — ArgoCD GitOps Deployment
* **Issue:** [#76](https://github.com/Kacper-Slezak/SOTP/issues/76) 🟠 *High*
* **Branch:** `gitops/76-argocd-deployment`
* Deploy ArgoCD with an App-of-Apps pattern. CI updates image tags in Git, triggering automated synchronization to K3d.

### Step 4.3 — Vault & External Secrets Operator on K8s
* **Issue:** [#134](https://github.com/Kacper-Slezak/SOTP/issues/134) 🟠 *High*
* **Branch:** `sec/134-vault-external-secrets`
* Run Vault on K8s and deploy External Secrets Operator (ESO) to sync database and API secrets into Kubernetes Secrets without storing secrets in Git.

### Step 4.4 — Kyverno Policy Enforcement
* **Issue:** [#135](https://github.com/Kacper-Slezak/SOTP/issues/135) 🟠 *High*
* **Branch:** `sec/135-kyverno-admission-policies`
* Deploy Kyverno policies: require Cosign cryptographic image signatures, disallow `:latest` image tags, and enforce resource limits.

---

## PHASE P5 — Observability & SRE
> **Milestone:** [P5 · Observability & SRE](https://github.com/Kacper-Slezak/SOTP/milestone/6)
> **Goal:** Complete the modern observability triangle (Metrics, Logs, Traces) with SRE error budget alerting and runbooks.

### Step 5.1 — Prometheus & FastAPI Instrumentator ✅
* **Issue:** [#63](https://github.com/Kacper-Slezak/SOTP/issues/63) ✅ *Completed*
* Backend metrics exposed at `/metrics` and scraped by Prometheus.

### Step 5.2 — Centralized Logging: Loki + Grafana Alloy
* **Issue:** [#72](https://github.com/Kacper-Slezak/SOTP/issues/72) 🟠 *High*
* **Branch:** `obs/72-loki-alloy-logging`
* Deploy Grafana Loki for log aggregation and configure Grafana Alloy as the collector for container logs.

### Step 5.3 — Prometheus Operator & ServiceMonitors
* **Issue:** [#136](https://github.com/Kacper-Slezak/SOTP/issues/136) 🟠 *High*
* **Branch:** `obs/136-kube-prometheus-stack`
* Install `kube-prometheus-stack` with custom `ServiceMonitor` definitions for FastAPI, Celery, PostgreSQL, and TimescaleDB.

### Step 5.4 — SLOs & Burn-Rate Alerts to Discord
* **Issue:** [#137](https://github.com/Kacper-Slezak/SOTP/issues/137) 🟠 *High*
* **Branch:** `sre/137-slos-burn-rate-alerts`
* Define Service Level Objectives using Sloth/Pyrra (e.g. 99.5% availability on API endpoints). Route multi-window multi-burn-rate alerts via Alertmanager to Discord webhook.

### Step 5.5 — Distributed Tracing with Grafana Tempo
* **Issue:** [#73](https://github.com/Kacper-Slezak/SOTP/issues/73) 🟡 *Medium*
* **Branch:** `obs/73-tempo-tracing-backend`
* Deploy Grafana Tempo backend and integrate trace-to-log correlation in Grafana.

### Step 5.6 — OpenTelemetry Instrumentation
* **Issue:** [#74](https://github.com/Kacper-Slezak/SOTP/issues/74) 🟡 *Medium*
* **Branch:** `obs/74-opentelemetry-instrumentation`
* Instrument FastAPI, SQLAlchemy async engine, and Celery tasks with OpenTelemetry SDK sending traces to Tempo.

### Step 5.7 — Grafana Dashboards as Code
* **Issue:** [#138](https://github.com/Kacper-Slezak/SOTP/issues/138) 🟡 *Medium*
* **Branch:** `obs/138-dashboards-as-code`
* Provision dashboards as JSON configmaps: Network Fleet Overview, Device Details (RTT/CPU/RAM), and SLO Error Budget Burn.

### Step 5.8 — Operational Runbooks & Postmortem Template
* **Issue:** [#139](https://github.com/Kacper-Slezak/SOTP/issues/139) 🟡 *Medium*
* **Branch:** `docs/139-runbooks-postmortems`
* Create actionable operational runbooks in `docs/runbooks/` linked from Alertmanager alerts, and provide a blameless postmortem template.

---

## PHASE P6 — Cloud IaC (AWS, plan-only)
> **Milestone:** [P6 · Cloud IaC (AWS, plan-only)](https://github.com/Kacper-Slezak/SOTP/milestone/7)
> **Goal:** Production-grade Terraform defining AWS infrastructure, validated and scanned in CI with zero cloud spend (never applied).

### Step 6.1 — Terraform: AWS VPC & EKS Module
* **Issue:** [#140](https://github.com/Kacper-Slezak/SOTP/issues/140) 🟠 *High*
* **Branch:** `iac/140-terraform-vpc-eks`
* Write clean Terraform modules in `infrastructure/terraform/` for VPC (multi-AZ public/private subnets) and managed EKS cluster.

### Step 6.2 — Terraform CI Pipeline & Infracost
* **Issue:** [#142](https://github.com/Kacper-Slezak/SOTP/issues/142) 🟠 *High*
* **Branch:** `ci/142-terraform-pipeline`
* CI pipeline executing `terraform fmt -check`, `validate`, `tflint`, Trivy/Checkov static security scans, and `infracost` pull-request cost projections.

### Step 6.3 — Terraform: Managed Cloud Services
* **Issue:** [#141](https://github.com/Kacper-Slezak/SOTP/issues/141) 🟡 *Medium*
* **Branch:** `iac/141-terraform-managed-services`
* Define ECR registries, IAM least-privilege roles (IRSA), RDS PostgreSQL instance, and AWS Secrets Manager.

### Step 6.4 — Architecture Mapping & Cost Documentation
* **Issue:** [#143](https://github.com/Kacper-Slezak/SOTP/issues/143) 🟡 *Medium*
* **Branch:** `docs/143-aws-architecture-cost`
* Document local vs. cloud architecture mapping diagram, failure domains, and cost estimation summary in `docs/AWS_ARCHITECTURE.md`.

---

## PHASE P7 — Product Features
> **Milestone:** [P7 · Product Features](https://github.com/Kacper-Slezak/SOTP/milestone/8)
> **Goal:** Deepen network monitoring capabilities: enhanced SNMP/SSH collectors, push agent, detailed UI metrics, and audit trail.

### Step 7.1 — Device Edit Form
* **Issue:** [#16](https://github.com/Kacper-Slezak/SOTP/issues/16) 🟡 *Medium*
* **Branch:** `feat/16-device-edit-form`
* Add `/devices/[id]/edit` form supporting `PUT /api/v1/devices/{id}` with validation and notifications.

### Step 7.2 — Frontend Route Protection & Silent Refresh
* **Issue:** [#52](https://github.com/Kacper-Slezak/SOTP/issues/52) 🟡 *Medium*
* **Branch:** `feat/52-route-protection`
* Add Next.js auth middleware redirecting unauthenticated users to `/login` and handling silent access token refreshes.

### Step 7.3 — SNMP Collector: Vault Credentials & Interface Stats
* **Issue:** [#54](https://github.com/Kacper-Slezak/SOTP/issues/54) 🟡 *Medium*
* **Branch:** `feat/54-snmp-vault-interface-metrics`
* Fetch SNMPv3 credentials dynamically from Vault; poll interface packet counters, errors, and operational status.

### Step 7.4 — SSH Command Executor (Netmiko)
* **Issue:** [#55](https://github.com/Kacper-Slezak/SOTP/issues/55) 🟡 *Medium*
* **Branch:** `feat/55-ssh-command-executor`
* Celery task executing read-only commands on network devices via Netmiko with strict command allow-listing and audit logging.

### Step 7.5 — Device Details Page with Historical Metrics
* **Issue:** [#57](https://github.com/Kacper-Slezak/SOTP/issues/57) 🟡 *Medium*
* **Branch:** `feat/57-device-details-metrics`
* UI page at `/devices/[id]` featuring Recharts time-series charts (RTT, packet loss, CPU, RAM) querying TimescaleDB downsampled buckets.

### Step 7.6 — Collector Integration Tests
* **Issue:** [#59](https://github.com/Kacper-Slezak/SOTP/issues/59) 🟡 *Medium*
* **Branch:** `test/59-collector-integration-tests`
* Integration test suite running mock SNMP and SSH daemon containers in CI to validate collector error handling.

### Step 7.7 — Audit Log Middleware
* **Issue:** [#77](https://github.com/Kacper-Slezak/SOTP/issues/77) 🟡 *Medium*
* **Branch:** `feat/77-audit-log-middleware`
* FastAPI middleware recording all state-modifying requests (`POST`, `PUT`, `DELETE`) with user identity and IP to the `audit_logs` table.

### Step 7.8 — UI Component Tests
* **Issue:** [#18](https://github.com/Kacper-Slezak/SOTP/issues/18) ⚪ *Low*
* **Branch:** `test/18-frontend-component-tests`
* Vitest and React Testing Library tests for `DevicesTable`, `DeviceForm`, and auth views.

### Step 7.9 — Home Fleet Summary Dashboard
* **Issue:** [#56](https://github.com/Kacper-Slezak/SOTP/issues/56) ⚪ *Low*
* **Branch:** `feat/56-home-fleet-dashboard`
* Home dashboard overview cards: active device count, average round-trip time, network health score, and recent alerts.

### Step 7.10 — E2E Testing with Playwright
* **Issue:** [#62](https://github.com/Kacper-Slezak/SOTP/issues/62) ⚪ *Low*
* **Branch:** `test/62-playwright-e2e-tests`
* Playwright end-to-end tests covering login flow, adding a device, and verifying table listing against the deployed K3d stack.

### Step 7.11 — Lightweight SOTP Push Agent
* **Issue:** [#86](https://github.com/Kacper-Slezak/SOTP/issues/86) ⚪ *Low*
* **Branch:** `feat/86-sotp-push-agent`
* Python agent in `apps/sotp_agent` collecting host metrics via `psutil` and pushing to the ingestion API.

### Step 7.12 — Metrics Ingestion Endpoint
* **Issue:** [#87](https://github.com/Kacper-Slezak/SOTP/issues/87) ⚪ *Low*
* **Branch:** `feat/87-metrics-ingest-endpoint`
* Endpoint `POST /api/v1/ingest/metrics` with API key authentication writing directly to TimescaleDB.

---

## PHASE P8 — Advanced / Stretch Goals
> **Milestone:** [P8 · Advanced / Stretch](https://github.com/Kacper-Slezak/SOTP/milestone/9)
> **Goal:** Flagship portfolio differentiators (select 1–2 based on capacity).

### Step 8.1 — Istio Ambient Service Mesh (mTLS)
* **Issue:** [#144](https://github.com/Kacper-Slezak/SOTP/issues/144) 🟡 *Medium*
* **Branch:** `mesh/144-istio-ambient-mtls`
* Zero-trust mutual TLS between microservices with Layer 4/7 AuthorizationPolicies, linking back to academic research on service mesh overhead.

### Step 8.2 — TextFSM / ntc-templates SSH Output Parser
* **Issue:** [#60](https://github.com/Kacper-Slezak/SOTP/issues/60) ⚪ *Low*
* **Branch:** `feat/60-textfsm-ssh-parsing`
* Parse unstructured CLI output into structured JSON using `ntc-templates`.

### Step 8.3 — Advanced JWT Management (Revocation & Rotation)
* **Issue:** [#61](https://github.com/Kacper-Slezak/SOTP/issues/61) ⚪ *Low*
* **Branch:** `feat/61-jwt-rotation-revocation`
* Redis-backed token revocation list (blocklist) and refresh token rotation on reuse.

### Step 8.4 — Chaos Mesh Fault Injection Experiments
* **Issue:** [#145](https://github.com/Kacper-Slezak/SOTP/issues/145) ⚪ *Low*
* **Branch:** `test/145-chaos-mesh-experiments`
* Inject pod failure, network delay, and database partitions to validate error budget alerts and system self-healing. Document findings in a postmortem.

### Step 8.5 — Performance & Load Testing with k6
* **Issue:** [#146](https://github.com/Kacper-Slezak/SOTP/issues/146) ⚪ *Low*
* **Branch:** `test/146-k6-load-testing`
* Load test API endpoints with k6 and visualize saturation boundaries against SLO thresholds in Grafana.

### Step 8.6 — Containerlab Realistic Network Topology
* **Issue:** [#147](https://github.com/Kacper-Slezak/SOTP/issues/147) ⚪ *Low*
* **Branch:** `test/147-containerlab-testing`
* Spin up virtual network routers (e.g. Arista cEOS / Nokia SR Linux) in Containerlab for realistic SNMP and SSH collector validation.

---

## Working Rules & Workflow

1. **Trunk-Based Delivery:** Every task is executed on a dedicated feature branch merged into `main` via a Pull Request.
2. **Branch Naming Standard:**
   * Features: `feat/<issue-id>-<short-description>`
   * Fixes: `fix/<issue-id>-<short-description>`
   * Infrastructure / Build: `build/<issue-id>-<short-description>` or `k8s/...`
   * CI / DevSecOps: `ci/<issue-id>-<short-description>` or `sec/...`
   * Tests: `test/<issue-id>-<short-description>`
   * Documentation: `docs/<issue-id>-<short-description>`
3. **Commit Standards:** Strictly comply with [Conventional Commits](.github/COMMIT_COVENCTIONS.md).
4. **CI Gates:** A PR cannot be merged until all automated quality, security, and test checks pass.
5. **Phase Completion Checklist:** After completing all issues in a phase:
   * Close the corresponding GitHub milestone.
   * Update `README.md` and docs.
   * Attach screenshot/GIF proof of working functionality.

---

*Last updated: October 2026 | Roadmap Version: 4.0*
