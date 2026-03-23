# SOTP — Roadmapa Projektu v3.0
>
> **Cel:** Portfolio-ready platforma monitoringu infrastruktury sieciowej — solo.
> **Kontekst:** SRE intern, projekt do CV, K8s jest częścią tego projektu.
> **Zasada:** Każdy krok = osobna branch + PR. Każdy krok ma issue na GitHubie.

---

## Stan Obecny (23.03.2026):

Wszystkie zadania cleanup/stabilizacji zakończone:

- `apps/core_backend/` — czysty `main.py`, `DeviceService` używany przez router, `DevicePut` w `schemas/devices.py`
- `apps/network_worker/` — izolowany serwis Celery, naprawiony bug `include=`, `celery-worker`/`celery-beat` zbudowane z `network_worker`
- CI/CD — `ci.yml` z quality + security + test + build + Discord notifications, wszystkie ścieżki spójne (`apps/core_backend`, `apps/web_frontend`, `apps/network_worker`)
- Docker Compose — Prometheus, Grafana, Vault, Redis, TimescaleDB, PostgreSQL, `celery-worker` i `celery-beat` z poprawnym working_dir
- Testy — `test_soft_delete.py` przepisany na `DeviceService`, `test_icmp_all.py` usunięty z `core_backend`

Zadania fazy 1 zakończone:

- **JWT Authentication**
- **RBAC**

W trakcie:

- **Test Auth**

---

## FAZA 1 — Backend: Auth & Security

> **Cel:** Żaden endpoint nie jest publiczny. JWT + RBAC działające end-to-end.

### Krok 1.1 — JWT Authentication

**Issue:** [#47](../../issues/47)

```bash
git checkout -b feat/47-jwt-authentication
```

Co zaimplementować w `apps/core_backend/`:

- `app/core/security.py` — `create_access_token`, `create_refresh_token`, `decode_token` (`python-jose`)
- `app/api/v1/auth.py` — `POST /api/v1/auth/register`, `/login`, `/refresh`
- `app/api/dependencies.py` — dependency `get_current_user` sprawdzająca Bearer token
- `app/schemas/auth.py` — `TokenResponse`, `LoginRequest`, `RegisterRequest`
- Hasła przez `passlib[bcrypt]`
- Zabezpiecz `/api/v1/devices` przez `Depends(get_current_user)`

📖 [FastAPI — OAuth2 with JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) | [python-jose](https://python-jose.readthedocs.io/en/latest/) | [Video (ArjanCodes)](https://www.youtube.com/watch?v=5GxQ1rLTwaU)

### Krok 1.2 — RBAC

**Issue:** [#48](../../issues/48)

```bash
git checkout -b feat/48-rbac
```

- `app/api/dependencies.py` — dependency `require_role(allowed_roles: list[UserRole])`
- `GET /devices` → ADMIN, OPERATOR, READONLY
- `POST /devices` → ADMIN
- `PUT /devices/{id}` → ADMIN, OPERATOR
- `DELETE /devices/{id}` → ADMIN
- `GET /api/v1/users/me` — zwraca aktualnego usera z rolą

📖 [FastAPI — Dependencies in depth](https://fastapi.tiangolo.com/tutorial/dependencies/)

### Krok 1.3 — Testy Auth

**Issue:** [#53](../../issues/53)

```bash
git checkout -b test/53-auth-integration-tests
```

Testy: rejestracja, logowanie, odświeżanie tokena, 401 bez tokena, 403 za mała rola.

📖 [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/) | [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/latest/)

### Krok 1.4 — Testy CRUD API

**Issue:** [#17](../../issues/17)

```bash
git checkout -b test/17-device-crud-tests
```

- Unit testy `DeviceService.create`, `get_by_id`, `get_all`, `update` — mock `AsyncSession`
- API testy przez `httpx.AsyncClient` dla każdego endpointu
- Pokrycie > 80%

### Krok 1.5 — Pagination, Sorting, Filtering

**Issue:** [#44](../../issues/44)

```bash
git checkout -b feat/44-device-list-pagination
```

- `DeviceService.get_all()` przyjmuje `limit`, `offset`, `sort_by`, `sort_order`, `is_active`, `device_type`, `vendor`
- Response: `{ "items": [...], "total_count": ..., "limit": ..., "offset": ... }`

---

## FAZA 2 — Backend: Vault Integration

> **Cel:** Credentials urządzeń (SNMP/SSH) w Vault, nie w bazie plain-text.

### Krok 2.1 — VaultService

**Issue:** [#49](../../issues/49)

```bash
git checkout -b feat/49-vault-service
```

- `app/services/vault_service.py` — `VaultService` z `set_device_credentials` i `get_device_credentials`
- Modyfikacja `POST /devices` i `PUT /devices` — przyjmują opcjonalne `snmp_community`, `ssh_password`, zapisują przez Vault
- Vault dev mode już działa w docker-compose

📖 [hvac — Python Vault client](https://hvac.readthedocs.io/en/stable/) | [Vault KV v2](https://developer.hashicorp.com/vault/docs/secrets/kv/kv-v2) | [Video (TechWorld with Nana)](https://www.youtube.com/watch?v=ci_0TrDN8C0)

---

## FAZA 3 — Network Worker: Dopracowanie Kolektorów

> **Cel:** `network_worker` jest kompletnym, izolowanym serwisem. ICMP + SNMP + SSH działają.

### Krok 3.1 — Dopracuj ICMP Collector

**Issue:** brak — stwórz przez `gh issue create` z tytułem `[FIX] ICMP device_id not propagated to PingResult`

```bash
git checkout -b fix/icmp-device-id-propagation
```

- `device_icmp` nie przekazuje `device_id` do `insert_ping_result` — napraw
- `_async_insert_ping_result` nie ustawia `device_id` w `PingResult` — napraw
- Dodaj `tenacity` retry logic (3 próby, exponential backoff)

📖 [tenacity — retry library](https://tenacity.readthedocs.io/en/latest/)

### Krok 3.2 — SNMP Collector: CPU/RAM

**Issue:** [#54](../../issues/54)

```bash
git checkout -b feat/54-snmp-cpu-ram
```

- Pobieranie credentials z Vault zamiast hardcoded `Config`
- OIDy: CPU `1.3.6.1.4.1.2021.11.11.0`, RAM total `1.3.6.1.4.1.2021.4.5.0`, available `1.3.6.1.4.1.2021.4.6.0`

📖 [pysnmp](https://pysnmp.readthedocs.io/en/latest/) | [SNMP OID reference](https://www.oid-info.com/)

### Krok 3.3 — SSH Executor

**Issue:** [#55](../../issues/55)

```bash
git checkout -b feat/55-ssh-executor
```

- `apps/network_worker/src/app/tasks/ssh_tasks.py`
- Celery task `execute_ssh_command(device_id, command)` — `netmiko`
- Whitelist dozwolonych komend
- Credentials z Vault

📖 [netmiko](https://github.com/ktbyers/netmiko) | [ntc-templates](https://github.com/networktocode/ntc-templates)

### Krok 3.4 — Testy kolektorów

**Issue:** [#59](../../issues/59)

```bash
git checkout -b test/59-snmp-ssh-integration-tests
```

- Testy SNMP z `snmpsim` lub mockami
- Testy SSH z mock serverem
- Muszą działać w CI

---

## FAZA 4 — Observability Stack

> **Cel:** Pełny stos PLT (Prometheus + Loki + Tempo) lokalnie.

### Krok 4.1 — Prometheus: metryki FastAPI

**Issue:** [#63](../../issues/63)

```bash
git checkout -b fix/63-prometheus-target
```

`Instrumentator().instrument(app).expose(app)` jest już w `main.py` ✅

Tylko napraw `infrastructure/prometheus/prometheus.yml`:

```yaml
- job_name: 'backend'
  static_configs:
    - targets: ['backend:8000']
```

Weryfikacja: `http://localhost:9090/targets` → `backend:8000` UP.

📖 [prometheus-fastapi-instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator) | [PromQL Tutorial](https://promlabs.com/promql-tutorial/)

### Krok 4.2 — Loki + Promtail

**Issue:** [#72](../../issues/72)

```bash
git checkout -b feat/72-loki-promtail
```

Dodaj do `docker-compose.dev.yml`:

- Serwis `loki` (`grafana/loki:latest`, port 3100)
- Serwis `promtail` — Docker socket, zbiera logi ze wszystkich kontenerów
- Datasource Loki w Grafanie

📖 [Loki Docker Compose](https://grafana.com/docs/loki/latest/setup/install/docker/) | [Video (TechWorld with Nana)](https://www.youtube.com/watch?v=h_GGd7HfKQ8)

### Krok 4.3 — Grafana Tempo + OpenTelemetry

**Issues:** [#73](../../issues/73) + [#74](../../issues/74)

```bash
git checkout -b feat/73-74-tempo-opentelemetry
```

**Infrastruktura:** `tempo` service w docker-compose, datasource w Grafanie.

**Instrumentacja backendu:**

- `requirements.txt`: `opentelemetry-distro`, `opentelemetry-exporter-otlp`, `opentelemetry-instrumentation-fastapi`, `opentelemetry-instrumentation-sqlalchemy`
- `app/core/observability.py` — inicjalizuje OTLP exporter do Tempo
- Wywołaj przy starcie w `main.py`

📖 [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/getting-started/) | [Grafana Tempo](https://grafana.com/docs/tempo/latest/getting-started/) | [Video (ByteByteGo)](https://www.youtube.com/watch?v=LAgI8vHKeeg)

### Krok 4.4 — Grafana Dashboards jako kod

**Issue:** brak — stwórz przez `gh issue create` z tytułem `[INFRA] Grafana dashboards as provisioned JSON`

```bash
git checkout -b feat/grafana-dashboards-as-code
```

- `network-overview.json` — devices up/down, avg RTT, % reachable
- `device-details.json` — template variable `$device`, RTT, CPU, RAM

📖 [Grafana Dashboard JSON](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/view-dashboard-json-model/) | [Grafana Provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/#dashboards)

### Krok 4.5 — Traefik Reverse Proxy

**Issue:** [#82](../../issues/82)

```bash
git checkout -b feat/82-traefik-reverse-proxy
```

- `sotp.localhost/` → Frontend
- `sotp.localhost/api` → Backend
- Rozwiązuje CORS

📖 [Traefik Docker Provider](https://doc.traefik.io/traefik/providers/docker/) | [Video (TechWorld with Nana)](https://www.youtube.com/watch?v=C6IL8tjwC5E)

---

## FAZA 5 — Frontend: Minimum Viable UI

> **Cel:** Projekt nie wygląda jak backend-only. Opisz Claudowi co chcesz — dostaniesz komponent.

### Krok 5.1 — Devices Table podłączona do API

**Issue:** [#15](../../issues/15)

```bash
git checkout -b feat/15-devices-table-api
```

- React Query `useQuery` → `GET /api/v1/devices`
- Tabela: Nazwa, IP, Typ, Status (zielona/czerwona kropka), Akcje
- Loading skeleton, error state
- Przycisk "Dodaj urządzenie" → `/devices/new`

### Krok 5.2 — Form dodawania/edycji urządzenia

**Issue:** [#16](../../issues/16)

```bash
git checkout -b feat/16-device-form
```

- Formularz z walidacją (IP format)
- `POST` / `PUT /api/v1/devices`
- Toast notifications sukces/błąd
- Po dodaniu — odświeżenie listy

### Krok 5.3 — Strony Auth

**Issue:** [#51](../../issues/51)

```bash
git checkout -b feat/51-auth-pages
```

- `/login` — email + hasło, `POST /api/v1/auth/login`
- Zustand store z persist middleware — `accessToken`, `refreshToken`, `user`
- Redirect po zalogowaniu → `/devices`

### Krok 5.4 — Route Protection

**Issue:** [#52](../../issues/52)

```bash
git checkout -b feat/52-route-protection
```

- Next.js Middleware lub `AuthGuard` w `(dashboard)/layout.tsx`
- Niezalogowany → `/login`
- Axios interceptor: 401 → refresh → retry

### Krok 5.5 — Metrics Tab na stronie urządzenia

**Issue:** [#57](../../issues/57)

```bash
git checkout -b feat/57-device-metrics-tab
```

- Backend: `GET /api/v1/devices/{id}/metrics?metric_name=cpu&time_range=1h`
- Frontend: wykresy `recharts` dla RTT, CPU, RAM z wyborem zakresu czasu

### Krok 5.6 — Testy komponentów UI

**Issue:** [#18](../../issues/18)

```bash
git checkout -b test/18-ui-component-tests
```

- Testy `DeviceTable` — renderuje dane z props
- Testy `DeviceForm` — walidacja, submit handler

📖 [TanStack Query](https://tanstack.com/query/latest/docs/framework/react/overview) | [Zustand persist](https://zustand.docs.pmnd.rs/integrations/persisting-store-data) | [Next.js Middleware](https://nextjs.org/docs/app/building-your-application/routing/middleware)

---

## FAZA 6 — SOTP Agent

> **Cel:** Lekki agent push metryk. Pokazuje rozumienie push vs pull w monitoringu.

### Krok 6.1 — Metrics Ingestion Endpoint

**Issue:** [#87](../../issues/87)

```bash
git checkout -b feat/87-metrics-ingestion-endpoint
```

- `app/api/v1/ingest.py` — `POST /api/v1/ingest/metrics`
- Zapisuje do TimescaleDB (`device_metrics`)
- Autentykacja przez API key w nagłówku (nie JWT)

### Krok 6.2 — Python Agent

**Issue:** [#86](../../issues/86)

```bash
git checkout -b feat/86-sotp-agent
```

- `apps/sotp_agent/agent.py` — zbiera CPU, RAM, disk, load average (`psutil`)
- Push do `POST /api/v1/ingest/metrics` co N sekund
- Config przez env vars: `SOTP_SERVER_URL`, `SOTP_API_KEY`, `COLLECT_INTERVAL`
- Działa jako Docker container lub systemd service

📖 [psutil](https://psutil.readthedocs.io/en/latest/) | [schedule library](https://schedule.readthedocs.io/en/stable/) | [systemd service](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

## FAZA 7 — Kubernetes

> **Cel:** SOTP działa na lokalnym K3d. Helm chart. GitOps z ArgoCD.

### Krok 7.0 — docker-compose.prod.yml

**Issue:** [#2](../../issues/2) (reopened)

```bash
git checkout -b build/2-docker-compose-prod
```

Obrazy z GHCR, bez volume mounts na kod, health checks obowiązkowe.

### Krok 7.1 — Lokalny klaster K3d

**Issue:** stwórz `[BUILD] k3d local cluster setup script`

```bash
git checkout -b build/k3d-local-cluster
```

- `scripts/k3d-cluster.sh` — tworzy klaster z local registry
- `Makefile`: `make k3d-up`, `make k3d-down`, `make k3d-push`

📖 [k3d Quick Start](https://k3d.io/v5.7.5/usage/commands/k3d_cluster_create/) | [Video: k3d](https://www.youtube.com/watch?v=mCesuGk-Fks)

### Krok 7.2 — Helm Chart

**Issue:** [#75](../../issues/75)

```bash
git checkout -b build/75-helm-chart
```

`infrastructure/helm/sotp/` z szablonami dla wszystkich serwisów.
Kluczowe: `migrations-job.yaml` jako `helm hook: pre-install` — migracje Alembic PRZED startem backendu.

📖 [Helm Chart Template Guide](https://helm.sh/docs/chart_template_guide/getting_started/) | [Helm Hooks](https://helm.sh/docs/topics/charts_hooks/) | [Video (TechWorld with Nana)](https://www.youtube.com/watch?v=-ykwb1d0DXU)

### Krok 7.3 — StatefulSets dla baz danych

**Issue:** stwórz `[BUILD] K8s StatefulSets for PostgreSQL and TimescaleDB`

Postgres i TimescaleDB jako StatefulSets z PVC.

📖 [K8s StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) | [PersistentVolumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)

### Krok 7.4 — Vault w K8s

**Issue:** stwórz `[BUILD] Vault Agent Injector in K8s`

Sekrety przez Vault Agent Injector (adnotacje na podach) zamiast K8s Secrets plain-text.

📖 [Vault Kubernetes Auth](https://developer.hashicorp.com/vault/docs/auth/kubernetes) | [Vault Agent Injector](https://developer.hashicorp.com/vault/docs/platform/k8s/injector)

### Krok 7.5 — GitOps z ArgoCD

**Issue:** [#76](../../issues/76) (zamknięty — reopen lub nowy)

```bash
git checkout -b feat/76-argocd-gitops
```

1. Nowe repo `sotp-k8s-config` — przenies Helm chart
2. Zainstaluj ArgoCD na klastrze
3. `infrastructure/argocd/application.yaml`
4. CI po zbudowaniu obrazu → commit do `sotp-k8s-config` z nowym `image.tag`

**Efekt:** `git push` → CI → ArgoCD → automatyczne wdrożenie.

📖 [ArgoCD Getting Started](https://argo-cd.readthedocs.io/en/stable/getting_started/) | [Video (TechWorld with Nana)](https://www.youtube.com/watch?v=MeU5_k9ssrs) | [Killercoda ArgoCD labs](https://killercoda.com/killer-shell-ckad)

---

## FAZA 8 — Funkcjonalność Produkcyjna

> **Cel:** Pełna platforma — alerty, audit trail, raporty, SSH konsola.

### Krok 8.1 — System Alertów

**Issue:** stwórz `[FEAT] Alert evaluation service and notification channels`

- `AlertService` ewaluuje reguły vs ostatnie metryki (Celery task co minutę)
- Alertmanager webhook → `POST /api/v1/webhooks/alerts`
- Kanały: Email, Slack, webhook

📖 [Prometheus Alertmanager](https://prometheus.io/docs/alerting/latest/configuration/)

### Krok 8.2 — Audit Middleware

**Issue:** [#77](../../issues/77)

- Middleware FastAPI przechwytuje POST/PUT/DELETE
- Pobiera `user_id` z JWT, zapisuje do `audit_logs`
- UI: `/logs` z filtrowaniem

### Krok 8.3 — System Raportowania

**Issue:** stwórz `[FEAT] Report generation API and UI`

- `ReportService` — agreguje dane z TimescaleDB
- PDF (`WeasyPrint`) lub CSV
- UI: `/reports` z formularzem i pobieraniem

### Krok 8.4 — SSH Konsola w UI

**Issue:** stwórz `[FEAT] SSH console tab on device details page`

- `POST /api/v1/devices/{id}/execute` (whitelist poleceń)
- UI: zakładka "Konsola" z outputem
- Połączony z krok 3.3

### Krok 8.5 — E2E Tests

**Issue:** [#62](../../issues/62)

```bash
git checkout -b test/62-e2e-tests
```

- Playwright — login flow, dodanie urządzenia, widok szczegółów
- Uruchamiane w CI po build

---

## FAZA 9 — Zaawansowane *(wybierz 1-2)*

> **Cel:** Flagowe funkcje wyróżniające projekt na tle innych.

### 9.1 — Linkerd Service Mesh (mTLS)

Automatyczne mTLS między serwisami. Golden Metrics dla każdego połączenia.
📖 [Linkerd Getting Started](https://linkerd.io/2.14/getting-started/)

### 9.2 — Advanced JWT (Blacklisting, Rotation)

**Issue:** [#61](../../issues/61) — token blacklisting przez Redis, refresh token rotation.

### 9.3 — Closed-Loop Automation (Auto-remediacja)

Alertmanager → webhook → Celery task → Netmiko naprawia problem automatycznie.

### 9.4 — ML/AI: Predykcja Anomalii

TimescaleDB Toolkit + Prophet. Celery task `predict_trends()`. Monitoring reaktywny → proaktywny.

### 9.5 — Containerlab: Realistyczne testy kolektorów

**Issue:** [#59](../../issues/59) — wirtualne routery Arista cEOS w CI.
📖 [Containerlab](https://containerlab.dev/quickstart/)

### 9.6 — TextFSM + SSH Parser

**Issue:** [#60](../../issues/60) — parsowanie output SSH do strukturalnego JSON.

---

## Kolejność — TL;DR

```
TERAZ:
  Faza 1: #47 JWT → #48 RBAC → #53 testy auth → #17 testy CRUD → #44 pagination

NASTĘPNIE:
  Faza 2: #49 Vault
  Faza 4: #63 Prometheus fix (2 linijki!) → #72 Loki → #73+#74 Tempo
  Faza 3: ICMP fix → #54 SNMP → #55 SSH

POTEM:
  Faza 5: #15 devices table → #16 form → #51 auth pages → #52 route protection
  Faza 4: dashboards as code → #82 Traefik
  Faza 6: #87 ingest endpoint → #86 agent

KUBERNETES:
  Faza 7: #2 docker-compose.prod → k3d → #75 Helm → StatefulSets → Vault K8s → #76 ArgoCD

ADVANCED:
  Faza 8: alerty → #77 audit → raporty → SSH konsola → #62 E2E
  Faza 9: wybierz 1-2 z #61, #59, #60, Linkerd, ML
```

---

## Zasady pracy

- Każdy krok = osobna branch + PR do `develop`
- Branch naming: `feat/47-jwt-auth`, `fix/63-prometheus-target`, `test/53-auth-tests`
- Commit convention: `.github/COMMIT_COVENCTIONS.md`
- Przed merge: CI zielone
- Po każdej fazie: zaktualizuj `README.md`

---

*Ostatnia aktualizacja: 2026-03-16 | Wersja: 3.0*
*Faza 0 (Cleanup) — ukończona ✅*
