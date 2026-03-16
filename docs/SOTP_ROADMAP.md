# SOTP — Roadmapa Projektu v2.0
>
> **Cel:** Zbudowanie portfolio-ready platformy monitoringu infrastruktury sieciowej — solo.
> **Kontekst:** SRE intern, projekt do CV, K8s jest częścią tego projektu (nie inżynierki).
> **Zasada:** Każdy krok = osobna branch + PR. Docker Compose do Fazy 4, K8s od Fazy 5.

---

## Stan Obecny (po refactorze — marzec 2026)

### ✅ Co działa poprawnie

- `apps/core_backend/` — czysty `main.py`, `DeviceService` istnieje i jest używany przez router
- `apps/network_worker/` — `celery_app.py` ma naprawiony bug z duplikatem `include=`
- CI/CD — `ci.yml` z quality + security + test + build + Discord notifications
- Docker Compose — Prometheus, Grafana, Vault, Redis, TimescaleDB, PostgreSQL
- Modele SQLAlchemy — Device, User, PingResult, DeviceMetric, Alert, AuditLog
- Alembic — dual-database migrations (postgres + timescale branches)

### ❌ Co jest nadal zepsute (napraw PRZED kolejnymi fazami)

| Problem | Plik | Co zrobić |
|---|---|---|
| Test importuje usunięty kod | `core_backend/tests/unit/test_soft_delete.py` importuje `delete_device` z `main.py` — ale tej funkcji już tam nie ma | Przepisać test żeby testował `DeviceService.soft_delete` |
| Test importuje nieistniejący moduł | `core_backend/tests/unit/test_icmp_all.py` importuje `app.tasks.monitoring_tasks` — ale tasks są przeniesione do `network_worker` | Usunąć ten test z `core_backend`, jest duplikatem w `network_worker` |
| CI wskazuje zły folder | `ci.yml` używa `apps/core_backend` (underscore), `docker-compose.dev.yml` używa `apps/core_backend` (hyphen) | Zdecyduj jedno nazewnictwo i zunifikuj wszędzie |
| Celery w złym serwisie | `docker-compose.dev.yml` buduje `celery-worker` i `celery-beat` z kontekstu `core_backend` | Powinny być budowane z `network_worker` |
| `test_soft_delete.py` rozbity | Test oczekuje `delete_device` w `main.py` | Zaktualizować lub usunąć |

---

## FAZA 0 — Cleanup & Stabilizacja *(TERAZ)*
>
> **Cel:** `make dev` startuje bez błędów. CI jest zielone. Wszystko spójne.

### Krok 0.1 — Napraw testy i CI

```bash
git checkout -b fix/broken-tests-and-ci
```

**Co zrobić:**

- Przepisz `test_soft_delete.py` — niech testuje `DeviceService.soft_delete` (mocki na sesję)
- Usuń `core_backend/tests/unit/test_icmp_all.py` — ten sam test jest w `network_worker`
- Zunifikuj nazewnictwo: zdecyduj `core_backend` (underscore) lub `core_backend` (hyphen) i zmień wszędzie: `ci.yml`, `docker-compose.dev.yml`, `Makefile`

**Weryfikacja:** `make test` działa, CI jest zielone.

📖 [pytest — dokumentacja](https://docs.pytest.org/en/stable/)

### Krok 0.2 — Przenieś Celery do network_worker w docker-compose

```bash
git checkout -b fix/celery-in-correct-service
```

**Co zrobić:**

- W `docker-compose.dev.yml`: zmień kontekst buildu `celery-worker` i `celery-beat` z `core_backend` na `network_worker`
- Dodaj brakujące zmienne środowiskowe do `celery-worker` (POSTGRES, TIMESCALE, REDIS)
- Usuń `celery-worker` i `celery-beat` jeśli nadal są w kontekście `core_backend`

📖 [Docker Compose — build context](https://docs.docker.com/compose/compose-file/build/)

### Krok 0.3 — Napraw Pydantic schemas w core_backend

```bash
git checkout -b fix/pydantic-schemas
```

Zauważ że `apps/core_backend/app/schemas/user.py` jest pusty. `DevicePut` jest zdefiniowany bezpośrednio w `main.py` — przenieś go do `schemas/device.py`.

**Weryfikacja końcowa Fazy 0:** `make dev` → backend healthy, Celery worker startuje z `network_worker`, CI zielone.

---

## FAZA 1 — Backend: Auth & Security
>
> **Cel:** Żaden endpoint nie jest publiczny. JWT + RBAC działające end-to-end.

### Krok 1.1 — JWT Authentication

```bash
git checkout -b feat/47-jwt-authentication
```

**Co zaimplementować** (w `apps/core_backend/`):

- `app/core/security.py` — funkcje `create_access_token`, `create_refresh_token`, `decode_token` (biblioteka `python-jose`)
- `app/api/v1/auth.py` — endpointy: `POST /api/v1/auth/register`, `/login`, `/refresh`
- `app/api/dependencies.py` — dependency `get_current_user` sprawdzająca Bearer token
- `app/schemas/auth.py` — Pydantic schemas: `TokenResponse`, `LoginRequest`, `RegisterRequest`
- Hasła hashowane przez `passlib[bcrypt]`
- Zabezpiecz endpointy `/api/v1/devices` (dodaj `Depends(get_current_user)`)

**Zmienne środowiskowe** (dodaj do `.env.example`): `SECRET_KEY`, `ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES=15`, `REFRESH_TOKEN_EXPIRE_DAYS=7`

📖 [FastAPI — OAuth2 with JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
📖 [python-jose docs](https://python-jose.readthedocs.io/en/latest/)
📖 [Video: FastAPI Auth (ArjanCodes)](https://www.youtube.com/watch?v=5GxQ1rLTwaU)

### Krok 1.2 — RBAC

```bash
git checkout -b feat/48-rbac
```

**Co zaimplementować:**

- `app/api/dependencies.py` — dependency `require_role(allowed_roles: list[UserRole])`
- Zabezpiecz endpointy według schematu:
  - `GET /devices` → ADMIN, OPERATOR, READONLY
  - `POST /devices` → ADMIN
  - `PUT /devices/{id}` → ADMIN, OPERATOR
  - `DELETE /devices/{id}` → ADMIN
- Endpoint `GET /api/v1/users/me` — zwraca aktualnego usera z rolą

📖 [FastAPI — Dependencies in depth](https://fastapi.tiangolo.com/tutorial/dependencies/)

### Krok 1.3 — Testy Auth

```bash
git checkout -b test/53-auth-integration-tests
```

Napisz testy dla: rejestracji, logowania, odświeżania tokena, dostępu bez tokena (401), dostępu z niewystarczającą rolą (403).

📖 [FastAPI Testing z httpx](https://fastapi.tiangolo.com/tutorial/testing/)
📖 [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/latest/)

---

## FAZA 2 — Backend: Vault Integration
>
> **Cel:** Credentials urządzeń (SNMP/SSH) w Vault, nie w bazie plain-text.

### Krok 2.1 — VaultService

```bash
git checkout -b feat/49-vault-service
```

**Co zaimplementować** (w `apps/core_backend/`):

- `app/services/vault_service.py` — klasa `VaultService` z metodami:
  - `set_device_credentials(device_id, credential_type, data: dict)` — zapisuje do `secret/data/devices/{id}/{type}`, tworzy rekord `Credential` w Postgres
  - `get_device_credentials(device_id, credential_type) -> dict` — pobiera z Vault po `vault_path` z tabeli `Credential`
- Modyfikacja `POST /devices` i `PUT /devices` — przyjmują opcjonalne pola `snmp_community`, `ssh_password`, zapisują przez `VaultService`
- Obsługa błędów: Vault niedostępny, ścieżka nie istnieje

**Konfiguracja Vault dev mode** jest już w `docker-compose.dev.yml` — token jest `VAULT_TOKEN` z `.env`.

📖 [hvac — Python Vault client](https://hvac.readthedocs.io/en/stable/)
📖 [Vault KV v2 API](https://developer.hashicorp.com/vault/docs/secrets/kv/kv-v2)
📖 [Video: HashiCorp Vault basics (TechWorld with Nana)](https://www.youtube.com/watch?v=ci_0TrDN8C0)

---

## FAZA 3 — Network Worker: Dopracowanie Kolektorów
>
> **Cel:** `network_worker` jest kompletnym, izolowanym serwisem. ICMP + SNMP + SSH działają.

### Krok 3.1 — Dopracuj ICMP Collector

```bash
git checkout -b fix/icmp-device-id-propagation
```

**Co naprawić** w `apps/network_worker/src/app/tasks/monitoring_tasks.py`:

- `device_icmp` nie przekazuje `device_id` do `insert_ping_result` — napraw to
- `_async_insert_ping_result` nie ustawia `device_id` w obiekcie `PingResult` — napraw
- Dodaj `tenacity` retry logic (3 próby, exponential backoff) dla timeoutów sieci

📖 [tenacity — retry library](https://tenacity.readthedocs.io/en/latest/)

### Krok 3.2 — SNMP Collector: CPU/RAM

```bash
git checkout -b feat/54-snmp-cpu-ram
```

Rozszerz `apps/network_worker/src/app/tasks/snmp_collector.py`:

- Pobieranie przez Vault (`VaultService`) credentials zamiast hardcoded config z `Config`
- OIDy dla CPU: `1.3.6.1.4.1.2021.11.11.0`, RAM total: `1.3.6.1.4.1.2021.4.5.0`, available: `1.3.6.1.4.1.2021.4.6.0`
- Poprawne zapisywanie do TimescaleDB przez `save_metrics()`

📖 [pysnmp — async hlapi](https://pysnmp.readthedocs.io/en/latest/)
📖 [SNMP OID reference](https://www.oid-info.com/)

### Krok 3.3 — SSH Executor

```bash
git checkout -b feat/55-ssh-executor
```

Stwórz `apps/network_worker/src/app/tasks/ssh_tasks.py`:

- Celery task `execute_ssh_command(device_id, command)` — używa `netmiko`
- Whitelist dozwolonych komend (konfigurowana przez env var lub plik YAML)
- Pobieranie credentials z Vault
- Zwraca raw output — parsowanie przez TextFSM opcjonalne

📖 [netmiko — Getting Started](https://github.com/ktbyers/netmiko)
📖 [TextFSM templates (ntc-templates)](https://github.com/networktocode/ntc-templates)

---

## FAZA 4 — Observability Stack (Docker Compose)
>
> **Cel:** Pełny stos PLT (Prometheus + Loki + Tempo) działający lokalnie.
> **Dlaczego ważne dla SRE:** To jest serce tej roli.

### Krok 4.1 — Prometheus: metryki FastAPI

```bash
git checkout -b feat/63-prometheus-fastapi-metrics
```

`prometheus-fastapi-instrumentator` już masz w `requirements.txt`. Wystarczy:

- W `main.py`: `Instrumentator().instrument(app).expose(app)` — **masz to już zrobione!**
- Zaktualizuj `infrastructure/prometheus/prometheus.yml` — zmień target z `localhost:9090` na `backend:8000`
- Zweryfikuj w Grafanie: `http://localhost:9090/targets` powinien pokazywać `backend` jako UP

📖 [prometheus-fastapi-instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator)
📖 [PromQL Tutorial (promlabs)](https://promlabs.com/promql-tutorial/)

### Krok 4.2 — Loki + Promtail

```bash
git checkout -b feat/72-loki-promtail
```

Dodaj do `docker-compose.dev.yml`:

```yaml
loki:
  image: grafana/loki:latest
  ports: ["3100:3100"]

promtail:
  image: grafana/promtail:latest
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
    - ./promtail-config.yml:/etc/promtail/config.yml
```

Stwórz `infrastructure/promtail/promtail-config.yml` — Docker target zbierający logi ze wszystkich kontenerów.
Zaktualizuj `infrastructure/grafana/datasources/datasource.yml` — dodaj Loki.

📖 [Loki — Docker Compose quickstart](https://grafana.com/docs/loki/latest/setup/install/docker/)
📖 [Promtail — Docker driver config](https://grafana.com/docs/loki/latest/send-data/promtail/configuration/)
📖 [Video: Loki + Promtail (TechWorld with Nana)](https://www.youtube.com/watch?v=h_GGd7HfKQ8)

### Krok 4.3 — Grafana Tempo (Distributed Tracing)

```bash
git checkout -b feat/73-74-tempo-opentelemetry
```

**Infrastruktura:** Dodaj `tempo` service do `docker-compose.dev.yml`, zaktualizuj datasources Grafany.

**Instrumentacja backendu:**

- Dodaj do `requirements.txt`: `opentelemetry-distro`, `opentelemetry-exporter-otlp`, `opentelemetry-instrumentation-fastapi`, `opentelemetry-instrumentation-sqlalchemy`
- Stwórz `app/core/observability.py` — inicjalizuje SDK z OTLP exporter do Tempo
- Wywołaj w `main.py` przy starcie aplikacji

**Cel:** Po wywołaniu API możesz w Grafanie zobaczyć pełny trace: HTTP request → SQLAlchemy query → czas odpowiedzi.

📖 [OpenTelemetry Python — Getting Started](https://opentelemetry.io/docs/languages/python/getting-started/)
📖 [Grafana Tempo — Docker Compose setup](https://grafana.com/docs/tempo/latest/getting-started/)
📖 [Video: OpenTelemetry explained (ByteByteGo)](https://www.youtube.com/watch?v=LAgI8vHKeeg)

### Krok 4.4 — Grafana Dashboards jako kod

```bash
git checkout -b feat/58-grafana-dashboards-as-code
```

Stwórz jako provisioned JSON (nie ręcznie w UI):

- `network-overview.json` — Stat: devices up/down, Gauge: % reachable, Time series: avg RTT
- `device-details.json` — z template variable `$device`, wykresy: RTT, packet loss, CPU, RAM

📖 [Grafana — Dashboard JSON model](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/view-dashboard-json-model/)
📖 [Grafana — Provisioning dashboards](https://grafana.com/docs/grafana/latest/administration/provisioning/#dashboards)

### Krok 4.5 — Traefik jako Reverse Proxy

```bash
git checkout -b feat/82-traefik-reverse-proxy
```

Dodaj `traefik` service do `docker-compose.dev.yml`. Cel:

- `sotp.localhost/` → Frontend (port 3000)
- `sotp.localhost/api` → Backend (port 8000)
- `sotp.localhost/dashboard` → Traefik Dashboard
- Rozwiązuje CORS issues

📖 [Traefik — Docker Provider](https://doc.traefik.io/traefik/providers/docker/)
📖 [Video: Traefik + Docker Compose (TechWorld with Nana)](https://www.youtube.com/watch?v=C6IL8tjwC5E)

---

## FAZA 5 — Frontend: Minimum Viable UI
>
> **Cel:** Projekt nie może wyglądać jak backend-only. Podstawowe strony działające z prawdziwym API.
> **Strategia:** Opisz co chcesz — Claude generuje komponenty.

### Krok 5.1 — Devices Table podłączona do API

```bash
git checkout -b feat/15-devices-table-api
```

`apps/web_frontend/src/app/(dashboard)/devices/page.tsx` — odkomentuj i podłącz:

- React Query `useQuery` → `GET /api/v1/devices`
- Tabela: Nazwa, IP, Typ, Status (zielona/czerwona kropka), Akcje (Edytuj / Usuń)
- Loading skeleton, error state z komunikatem
- Przycisk "Dodaj urządzenie" → nawiguje do `/devices/new`

### Krok 5.2 — Strony Auth

```bash
git checkout -b feat/51-auth-pages
```

- `/login` — formularz email + hasło, `POST /api/v1/auth/login`, zapis tokenów do Zustand store
- Zustand store z persist middleware (`localStorage`) — `accessToken`, `refreshToken`, `user`
- Redirect po zalogowaniu → `/devices`

### Krok 5.3 — Route Protection

```bash
git checkout -b feat/52-route-protection
```

- Next.js Middleware lub `AuthGuard` w `(dashboard)/layout.tsx`
- Niezalogowany user → redirect do `/login`
- Axios interceptor: jeśli 401 → wywołaj `/auth/refresh` → retry

📖 [TanStack Query — Getting Started](https://tanstack.com/query/latest/docs/framework/react/overview)
📖 [Zustand — persist middleware](https://zustand.docs.pmnd.rs/integrations/persisting-store-data)
📖 [Next.js Middleware](https://nextjs.org/docs/app/building-your-application/routing/middleware)

---

## FAZA 6 — SOTP Agent
>
> **Cel:** Własny lekki agent zbierający metryki systemowe. Pokazuje rozumienie push vs pull.

### Krok 6.1 — Backend: Metrics Ingestion Endpoint

```bash
git checkout -b feat/87-metrics-ingestion-endpoint
```

Stwórz `apps/core_backend/app/api/v1/ingest.py`:

- `POST /api/v1/ingest/metrics` — przyjmuje JSON z metrykami agenta
- Zapisuje do TimescaleDB (ta sama tabela `device_metrics`)
- Autentykacja przez API key (nie JWT — agent to nie użytkownik)

### Krok 6.2 — Agent Python

```bash
git checkout -b feat/86-sotp-agent
```

Rozbuduj `apps/sotp_agent/agent.py`:

- Zbiera co N sekund: CPU (`psutil.cpu_percent`), RAM (`psutil.virtual_memory`), disk (`psutil.disk_usage`), load average
- Push do `POST /api/v1/ingest/metrics` z API key w nagłówku
- Konfiguracja przez env vars: `SOTP_SERVER_URL`, `SOTP_API_KEY`, `COLLECT_INTERVAL`
- Może działać jako Docker container lub systemd service

📖 [psutil — dokumentacja](https://psutil.readthedocs.io/en/latest/)
📖 [schedule library](https://schedule.readthedocs.io/en/stable/)
📖 [systemd service file](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

## FAZA 7 — Kubernetes
>
> **Cel:** Cały SOTP działa na lokalnym K3d. Helm chart. Podstawy GitOps z ArgoCD.
> **Prerequisite:** Działający `docker-compose.prod.yml` + obrazy w GHCR.

### Krok 7.0 — docker-compose.prod.yml

```bash
git checkout -b build/2-docker-compose-prod
```

Stwórz `infrastructure/docker/docker-compose.prod.yml` — obrazy budowane z Dockerfile bez volume mounts na kod źródłowy.

### Krok 7.1 — Lokalny klaster K3d

```bash
git checkout -b build/k3d-local-cluster
```

Stwórz `scripts/k3d-cluster.sh`:

- Tworzy klaster K3d z local registry
- Konfiguruje port forwarding
- Dodaje wpis `sotp.localhost` do `/etc/hosts`

Zaktualizuj `Makefile` o: `make k3d-up`, `make k3d-down`, `make k3d-push`.

📖 [k3d — Quick Start](https://k3d.io/v5.7.5/usage/commands/k3d_cluster_create/)
📖 [Video: k3d tutorial](https://www.youtube.com/watch?v=mCesuGk-Fks)

### Krok 7.2 — Helm Chart

```bash
git checkout -b build/75-helm-chart
```

Stwórz `infrastructure/helm/sotp/` z szablonami dla: backend, frontend, network_worker, postgres (StatefulSet), timescaledb (StatefulSet), redis, vault, prometheus, loki, grafana, traefik ingress, migrations Job.

**Kluczowe:** Migracje Alembic jako K8s Job (`migrations-job.yaml`) — musi uruchomić się PRZED startem backendu (`initContainers` lub `helm hook: pre-install`).

📖 [Helm — Chart Template Guide](https://helm.sh/docs/chart_template_guide/getting_started/)
📖 [Helm — Hooks](https://helm.sh/docs/topics/charts_hooks/)
📖 [Video: Helm explained (TechWorld with Nana)](https://www.youtube.com/watch?v=-ykwb1d0DXU)

### Krok 7.3 — StatefulSets dla baz danych

Postgres i TimescaleDB jako StatefulSets z PersistentVolumeClaims. Redis jako StatefulSet lub Deployment z emptyDir (dev).

📖 [K8s — StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
📖 [K8s — Storage Classes + PVC](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)

### Krok 7.4 — Secrets Management w K8s

Vault działa w K8s. Sekrety wstrzykiwane przez Vault Agent Injector (adnotacje na podach) zamiast K8s Secrets plain-text.

📖 [Vault — Kubernetes Auth Method](https://developer.hashicorp.com/vault/docs/auth/kubernetes)
📖 [Vault Agent Injector](https://developer.hashicorp.com/vault/docs/platform/k8s/injector)

### Krok 7.5 — GitOps z ArgoCD

```bash
git checkout -b feat/76-argocd-gitops
```

1. Stwórz drugie repo: `sotp-k8s-config` — przenies tam Helm chart
2. Zainstaluj ArgoCD na klastrze
3. Stwórz `infrastructure/argocd/application.yaml`
4. Zaktualizuj `deploy-prod.yml` w CI: po zbudowaniu obrazu → commit do `sotp-k8s-config` z nowym `image.tag`

**Efekt:** `git push` → CI buduje obraz → aktualizuje `sotp-k8s-config` → ArgoCD wykrywa zmianę → automatyczne wdrożenie.

📖 [ArgoCD — Getting Started](https://argo-cd.readthedocs.io/en/stable/getting_started/)
📖 [Video: ArgoCD Tutorial (TechWorld with Nana)](https://www.youtube.com/watch?v=MeU5_k9ssrs)
📖 [Killercoda — ArgoCD labs](https://killercoda.com/killer-shell-ckad)

---

## FAZA 8 — Funkcjonalność Produkcyjna
>
> **Cel:** Pełna platforma: alerty, logi, raporty, SSH konsola, audit trail.

### Krok 8.1 — System Alertów

- `AlertRule` model już istnieje — zaimplementuj `AlertService`
- Celery task (`alert_tasks.py`) — co minutę ewaluuje reguły vs ostatnie metryki
- Alertmanager webhook → endpoint `POST /api/v1/webhooks/alerts`
- Kanały powiadomień: Email (SMTP), Slack (webhook), ogólny webhook

📖 [Prometheus Alertmanager — Configuration](https://prometheus.io/docs/alerting/latest/configuration/)

### Krok 8.2 — Audit Middleware

- Middleware FastAPI przechwytujące POST/PUT/DELETE
- Pobiera `user_id` z tokenu JWT
- Zapisuje do tabeli `audit_logs`
- UI: strona `/logs` z filtrowaniem po akcji, użytkowniku, czasie

### Krok 8.3 — System Raportowania

- `ReportService` — agreguje dane z TimescaleDB (dostępność, avg RTT, top CPU)
- Endpoint `POST /api/v1/reports` — parametry: typ, zakres dat
- Generuje PDF (`WeasyPrint`) lub CSV
- UI: strona `/reports` z formularzem i pobieraniem pliku

📖 [WeasyPrint docs](https://doc.courtbouillon.org/weasyprint/stable/)

### Krok 8.4 — SSH Konsola w UI

- Endpoint `POST /api/v1/devices/{id}/execute` (z whitelistą poleceń)
- Kolejkuje zadanie Celery, czeka na wynik (polling lub WebSocket)
- UI: zakładka "Konsola" na stronie urządzenia — textarea z outputem

### Krok 8.5 — Backup & Disaster Recovery

- K8s CronJob — codzienny `pg_dump` do MinIO (lokalnie) lub S3
- `scripts/backup.sh` i `scripts/restore.sh`
- `docs/11-DISASTER_RECOVERY.md` z przetestowaną procedurą

---

## FAZA 9 — Zaawansowane Funkcje *(Beyond Faza 5)*
>
> **Cel:** Flagowe funkcje wyróżniające projekt. Wybierz 1-2, nie musisz robić wszystkich.

### 9.1 — Linkerd Service Mesh (mTLS między serwisami)

Zainstaluj Linkerd na klastrze. Wstrzyknij proxy do podów. Efekt: automatyczne mTLS, "Golden Metrics" (RPS, latency, success rate) dla każdego połączenia.

📖 [Linkerd — Getting Started](https://linkerd.io/2.14/getting-started/)

### 9.2 — Closed-Loop Automation (Auto-remediacja)

1. Alertmanager wysyła webhook do `POST /api/v1/webhooks/remediate`
2. Backend waliduje alert i kolejkuje task Celery
3. Task używa Netmiko do automatycznej akcji (restart interfejsu, clear ARP, itp.)
**Efekt:** System nie tylko alarmuje — sam naprawia.

### 9.3 — ML/AI: Predykcja Anomalii

- `TimescaleDB Toolkit` + `Prophet` (Facebook)
- Celery task `predict_trends()` — generuje predykcje na podstawie danych historycznych
- Alert gdy wartość przekroczy przewidywany zakres (anomalia)
**Efekt:** Monitoring reaktywny → proaktywny.

### 9.4 — Network Config Backup (GitOps dla sieci)

- Netmiko pobiera `running-config` z urządzeń
- Celery task zapisuje do repozytorium Git
- Alert przy drifcie konfiguracji

### 9.5 — Containerlab: Realistyczne testy kolektorów

- `sotp-test-environment` repo z `topology.yml` (wirtualne routery Arista cEOS)
- CI uruchamia Containerlab → testy SNMP/SSH na prawdziwym OS routera
**Efekt:** 100% realistyczne testy bez sprzętu.

📖 [Containerlab — Getting Started](https://containerlab.dev/quickstart/)

### 9.6 — Agent MQTT (IoT)

Dodaj `apps/sotp_agent/mqtt_collector.py` — subskrybuje tematy MQTT (czujniki temp/wilgotności), zapisuje do TimescaleDB. Pokazuje że SOTP to universalna platforma telemetryczna.

---

## Kolejność absolutna — TL;DR

```
TERAZ (Faza 0):
  0.1 Napraw testy + zunifikuj nazewnictwo
  0.2 Przenieś Celery do network_worker w docker-compose
  0.3 Przenieś DevicePut do schemas/device.py

NASTĘPNIE — po jednym na raz:
  1.1 → 1.2 → 1.3   JWT + RBAC + testy
  2.1                Vault integration
  4.1                Prometheus (2 linijki kodu, duży efekt !)
  4.2                Loki
  3.1 → 3.2          ICMP fix + SNMP dopracowanie
  5.1 → 5.2 → 5.3    Frontend minimum

POTEM:
  4.3 Tempo (tracing)
  4.4 Dashboards as code
  4.5 Traefik
  6.1 → 6.2 SOTP Agent
  3.3 SSH Executor

KUBERNETES (Faza 7):
  7.0 docker-compose.prod.yml
  7.1 k3d lokalny klaster
  7.2 Helm chart
  7.3 StatefulSets
  7.4 Vault w K8s
  7.5 ArgoCD (GitOps)

ADVANCED (Faza 8-9):
  8.x Funkcje produkcyjne (alerty, raporty, SSH konsola)
  9.x Wybierz 1-2: Linkerd / Auto-remediacja / ML / Containerlab
```

---

## Zasady pracy (bez zmian, dla przypomnienia)

- Każdy krok = osobna branch + PR
- Branch naming: `feat/47-jwt-auth`, `fix/celery-in-wrong-service`, `chore/unify-naming`
- Commit convention: patrz `.github/COMMIT_COVENCTIONS.md`
- Przed merge: CI musi być zielone
- Po każdej fazie: zaktualizuj `README.md` i odpowiedni plik w `docs/`
- Skonsultuj się z Claudem przed każdą fazą — opisz co chcesz zrobić, dostaniesz feedback i kod

---

## Różnice względem poprzedniego planu (v1 → v2)

| Zmiana | Dlaczego |
|---|---|
| K8s to Faza 7 (nie "osobny temat") | Kacper potwierdził że K8s jest częścią tego projektu |
| Faza 0 zawiera konkretne bugi do naprawienia | Znamy dokładny stan kodu po refactorze |
| Docker Compose do Fazy 6 włącznie | Realistyczne dla solo dewelopera |
| SOTP Agent jako osobna faza (6) | Ważny dla SRE — push vs pull w monitoringu |
| Beyond Faza 5 włączone jako Faza 9 | Długoterminowa wizja z oryginalnego dokumentu |
| Audit Middleware jako osobny krok | Ważne dla SRE — accountability trail |
| Tempo/OpenTelemetry jako krok 4.3 | Pełny stos PLT = wyróżnik na CV |
| Linkerd w Fazie 9 (nie 5) | Zaawansowane — po K8s jest działający |

---

*Ostatnia aktualizacja: 2026-03-16 | Wersja: 2.0 | Oparty na: SOTP_Master_Document_v3_5.md + Beyond_Faza_5.md*
