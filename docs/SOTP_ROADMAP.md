# SOTP — Roadmapa Projektu
> **Cel:** Doprowadzić projekt do stanu portfolio-ready pod DevOps/SRE.
> **Zasada:** Każdy krok to osobny PR. Małe, atomiczne zmiany.

---

## ⚠️ NAJPIERW: Analiza stanu obecnego

### Duplikaty do usunięcia (zrób to jako PIERWSZY commit)

| Problem | Lokalizacja | Co zrobić |
|---|---|---|
| Dwa foldery backendu | `apps/core_backend/` (underscore) vs `apps/core-backend/` (hyphen) | Zostaw `core-backend` (hyphen) — tak jest w docker-compose. Usuń `core_backend`. |
| Duplikat frontendu | `apps/web-frontend/test/` | Cały folder do usunięcia — to stara wersja. |
| ICMP logic w 3 miejscach | `core_backend/app/tasks/monitoring_tasks.py` + `network-worker/src/app/tasks/monitoring_tasks.py` + `network-worker/src/app/worker.py` | Zostaw tylko `network-worker/src/app/tasks/monitoring_tasks.py`. Z core-backend usuń tasks. |
| Celery app w 2 miejscach | `core_backend/app/tasks/celery_app.py` + `network-worker/src/app/celery/celery_app.py` | Każdy serwis ma swój — ok, ale `core-backend` nie powinien już mieć Celery workera. |
| Beat schedule w 2 miejscach | `core_backend/app/tasks/celery_Beat_for_icmp.py` + `network-worker/src/app/celery/celery_Beat_for_icmp.py` | Zostaw tylko w `network-worker`. |
| Bug w celery_app.py | `network-worker/src/app/celery/celery_app.py` ma dwa razy `include=` | Jeden `include=` z listą obu tasków. |

### Braki architektoniczne (po refactorze)

- `core-backend` nadal ma `celery-worker` i `celery-beat` w docker-compose — powinny być w `network-worker`
- `core-backend/app/services/device_services.py` istnieje ale `main.py` go nie używa (logika nadal w main.py bezpośrednio)
- Frontend: `DevicesTable` jest zakomentowany, strona `/devices` nic nie robi
- Brak JWT — wszystkie endpointy są publiczne
- Brak `.env` (tylko `.env.example`) — trzeba to opisać w README

---

## FAZA 0 — Cleanup & Stabilizacja
> **Kiedy:** Teraz, zanim cokolwiek nowego dodasz.
> **Cel:** Projekt musi startować `make dev` bez błędów i być spójny.

### Krok 0.1 — Usuń duplikaty
```
git checkout -b chore/cleanup-duplicates
```
- Usuń `apps/core_backend/` (zostaw `apps/core-backend/`)
- Usuń `apps/web-frontend/test/`
- Usuń `apps/core-backend/app/tasks/` (monitoring przechodzi do network-worker)
- Napraw bug w `network-worker/src/app/celery/celery_app.py`

**Efekt:** Jasna granica — core-backend = REST API, network-worker = Celery tasks.

### Krok 0.2 — Refactor: Service Layer w core-backend
Przenieś logikę CRUD z `main.py` do `device_service.py`.
Issue #43 masz już opisany.

📖 Zasoby:
- [FastAPI Best Practices — Service Layer](https://github.com/zhanymkanov/fastapi-best-practices#project-structure)
- [SQLAlchemy Async Sessions](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

### Krok 0.3 — Zaktualizuj docker-compose
Przenieś `celery-worker` i `celery-beat` do osobnego compose dla network-worker lub opisz to w Makefile.

📖 Zasoby:
- [Docker Compose — Multiple Compose Files](https://docs.docker.com/compose/multiple-compose-files/)

---

## FAZA 1 — Backend: Auth & Security
> **Cel:** Żaden endpoint nie jest publiczny. Podstawa każdego real-world projektu.

### Krok 1.1 — JWT Authentication (Issue #47)
```
git checkout -b feat/jwt-authentication
```

Co zaimplementować:
- `POST /api/v1/auth/register` — rejestracja
- `POST /api/v1/auth/login` → zwraca `access_token` (15min) + `refresh_token` (7d)
- `POST /api/v1/auth/refresh` → nowy access_token
- Dependency `get_current_user` — sprawdza Bearer token na każdym endpoincie
- Zaszyfrowane hasła przez `passlib[bcrypt]`

📖 Zasoby:
- [FastAPI — OAuth2 with JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [python-jose docs](https://python-jose.readthedocs.io/en/latest/)
- [Video: FastAPI Auth od zera (ArjanCodes)](https://www.youtube.com/watch?v=5GxQ1rLTwaU)

### Krok 1.2 — RBAC (Issue #48)
```
git checkout -b feat/rbac
```

Co zaimplementować:
- Role już masz w modelu: `ADMIN`, `OPERATOR`, `AUDITOR`, `READONLY`
- Dependency `require_role([UserRole.ADMIN, UserRole.OPERATOR])`
- Zabezpiecz endpointy devices według tabeli z issue #48
- `GET /api/v1/users/me` — zwraca aktualnego usera

📖 Zasoby:
- [FastAPI — Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI Advanced Security](https://fastapi.tiangolo.com/advanced/security/)

### Krok 1.3 — Testy Auth (Issue #53)
Napisz testy integracyjne dla całego flow auth z `httpx.AsyncClient`.

📖 Zasoby:
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/latest/)
- [httpx AsyncClient w testach](https://www.python-httpx.org/async/)

---

## FAZA 2 — Backend: Vault Integration
> **Cel:** Żadne credentials urządzeń nie leżą w bazie danych plain-text.
> **Dlaczego ważne dla SRE:** Secrets management to podstawa produkcyjnych systemów.

### Krok 2.1 — VaultService (Issue #49)
```
git checkout -b feat/vault-integration
```

Co zaimplementować:
- `VaultService` z metodami `get_credentials` i `set_credentials`
- Modyfikacja `POST /devices` — SNMP/SSH creds idą do Vault, w DB tylko `vault_path`
- Obsługa błędów połączenia z Vault

📖 Zasoby:
- [HashiCorp Vault — Getting Started](https://developer.hashicorp.com/vault/tutorials/getting-started)
- [hvac (Python Vault client) docs](https://hvac.readthedocs.io/en/stable/)
- [Vault KV Secrets Engine](https://developer.hashicorp.com/vault/docs/secrets/kv/kv-v2)
- [Video: Vault basics (TechWorld with Nana)](https://www.youtube.com/watch?v=ci_0TrDN8C0)

---

## FAZA 3 — Network Worker: SNMP & SSH
> **Cel:** Kompletny, izolowany serwis do zbierania metryk.

### Krok 3.1 — Dopracuj ICMP Collector
Masz już działający kod — teraz:
- Upewnij się, że `device_id` jest poprawnie przekazywany do `PingResult`
- Dodaj proper error handling dla edge cases
- Przetestuj z prawdziwymi urządzeniami (lub mockami)

### Krok 3.2 — SNMP Collector (Issue #54)
```
git checkout -b feat/snmp-collector-cpu-ram
```

Rozszerz istniejący `snmp_collector.py` o:
- CPU utilization (`1.3.6.1.4.1.2021.11.11.0`)
- RAM usage (`1.3.6.1.4.1.2021.4.5.0`, `1.3.6.1.4.1.2021.4.6.0`)
- Poprawne zapisywanie do TimescaleDB

📖 Zasoby:
- [pysnmp documentation](https://pysnmp.readthedocs.io/en/latest/)
- [SNMP OID Reference](https://www.oid-info.com/)
- [Net-SNMP — standard OIDs](http://www.net-snmp.org/docs/mibs/)

### Krok 3.3 — SSH Executor (Issue #55)
```
git checkout -b feat/ssh-executor
```

Co zaimplementować:
- Celery task `execute_ssh_command(device_id, command)`
- Whitelist dozwolonych komend (bezpieczeństwo!)
- Używa credentials z Vault
- Wynik zapisuje do bazy/zwraca przez API

📖 Zasoby:
- [Netmiko documentation](https://github.com/ktbyers/netmiko)
- [Netmiko — supported devices](https://github.com/ktbyers/netmiko/blob/develop/PLATFORMS.md)

---

## FAZA 4 — Frontend: Minimum Viable UI
> **Cel:** Projekt nie może wyglądać jak backend-only. Podstawowe strony wystarczą.
> **Strategia:** Używaj Claude do generowania komponentów — opisz co chcesz, dostaniesz kod.

### Krok 4.1 — Podłącz Devices Table (Issue #15)
`DevicesTable` jest zakomentowany. Odkomentuj i podłącz do API.
- React Query `useQuery` → `GET /api/v1/devices`
- Tabela z kolumnami: Nazwa, IP, Typ, Status, Akcje
- Loading state, error state

### Krok 4.2 — Strony Auth (Issue #51)
- `/login` — formularz + POST do `/api/v1/auth/login`
- Zapis tokenów (zustand + localStorage)
- Redirect po zalogowaniu

### Krok 4.3 — Route Protection (Issue #52)
- Middleware lub `AuthGuard` komponent
- Niezalogowany user → redirect do `/login`

📖 Zasoby:
- [TanStack Query — Getting Started](https://tanstack.com/query/latest/docs/framework/react/overview)
- [Zustand docs](https://zustand-demo.pmnd.rs/)
- [Next.js Middleware](https://nextjs.org/docs/app/building-your-application/routing/middleware)

---

## FAZA 5 — Observability Stack
> **Cel:** Pełny stack obserwabilności: metrics + logs + (opcjonalnie) traces.
> **Dlaczego ważne dla SRE:** To jest serce tej roli.

### Krok 5.1 — Prometheus Metrics z FastAPI (Issue #63)
```
git checkout -b feat/prometheus-fastapi-metrics
```

`prometheus-fastapi-instrumentator` już masz w requirements. Wystarczy:
- Skonfigurować w `main.py` (2 linijki kodu)
- Zaktualizować `prometheus.yml` — zmień target z `localhost:9090` na `backend:8000`
- Zweryfikować w Grafanie

📖 Zasoby:
- [prometheus-fastapi-instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator)
- [Prometheus — Getting Started](https://prometheus.io/docs/prometheus/latest/getting_started/)
- [PromQL Tutorial](https://promlabs.com/promql-tutorial/)

### Krok 5.2 — Loki + Promtail (Issue #72)
```
git checkout -b feat/loki-promtail
```

Dodaj do `docker-compose.dev.yml`:
- Serwis `loki` (image: `grafana/loki:latest`)
- Serwis `promtail` — automatycznie zbiera logi ze wszystkich kontenerów przez Docker socket
- Datasource Loki w Grafanie

📖 Zasoby:
- [Loki — Docker Compose setup](https://grafana.com/docs/loki/latest/setup/install/docker/)
- [Promtail — Docker target](https://grafana.com/docs/loki/latest/send-data/promtail/configuration/)
- [Grafana — Loki datasource](https://grafana.com/docs/grafana/latest/datasources/loki/)
- [Video: Loki + Promtail setup (TechWorld with Nana)](https://www.youtube.com/watch?v=h_GGd7HfKQ8)

### Krok 5.3 — Grafana Dashboards (Issue #58)
Stwórz jako JSON (provisioning, nie ręcznie):
- **Device Overview** — devices up/down, avg RTT, top CPU
- **Device Details** — wykresy dla konkretnego urządzenia (RTT, CPU, RAM)

📖 Zasoby:
- [Grafana — Dashboard provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/#dashboards)
- [Grafana — Dashboard JSON model](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/view-dashboard-json-model/)
- [Grafana — Variables](https://grafana.com/docs/grafana/latest/dashboards/variables/)

---

## FAZA 6 — Infrastructure: Traefik
> **Cel:** Jeden adres dla całej aplikacji. Koniec z portem 3000 i 8000 osobno.

### Krok 6.1 — Traefik jako Reverse Proxy (Issue #82)
```
git checkout -b feat/traefik-reverse-proxy
```

Cel:
- `sotp.localhost/` → Frontend
- `sotp.localhost/api` → Backend
- Rozwiązuje CORS issues
- Dashboard Traefika pod `sotp.localhost/dashboard`

📖 Zasoby:
- [Traefik — Docker Provider](https://doc.traefik.io/traefik/providers/docker/)
- [Traefik — Quick Start](https://doc.traefik.io/traefik/getting-started/quick-start/)
- [Video: Traefik + Docker Compose (TechWorld with Nana)](https://www.youtube.com/watch?v=C6IL8tjwC5E)

---

## FAZA 7 — SOTP Agent
> **Cel:** Własny agent zbierający metryki z Linuxa. Pokazuje rozumienie push vs pull w monitoringu.

### Krok 7.1 — Python Agent (Issue #86)
```
git checkout -b feat/sotp-agent
```

Co zaimplementować:
- Zbiera: CPU, RAM, disk, load average (`psutil`)
- Push do `POST /api/v1/ingest/metrics` (Issue #87)
- Działa jako Docker container lub systemd service
- Konfigurowalny interval i adres serwera

📖 Zasoby:
- [psutil docs](https://psutil.readthedocs.io/en/latest/)
- [Python schedule library](https://schedule.readthedocs.io/en/stable/)
- [systemd service file](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

## FAZA 8 — Kubernetes (Osobny temat — inżynierka)
> **Cel:** Portfolio-ready K8s deployment. Helm charts dla każdego serwisu.
> **Uwaga:** To jest materiał na inżynierkę — tu tylko zarys żebyś wiedział co Cię czeka.

### Co musisz mieć zanim zaczniesz K8s:
- [ ] Działający `docker-compose.prod.yml` (Issue #2)
- [ ] Obrazy wypychane do GHCR (CI już to robi dla tagów `v*`)
- [ ] Secrets w Vault lub K8s Secrets

### Kolejność nauki K8s dla tego projektu:
1. Podstawy — Pod, Deployment, Service, Ingress
2. ConfigMaps i Secrets
3. StatefulSets (dla PostgreSQL, TimescaleDB, Redis)
4. Helm — tworzenie własnych chartów (Issue #75)
5. k3d do lokalnego developmentu
6. (opcjonalnie) ArgoCD (Issue #76)

📖 Zasoby:
- [Kubernetes — Official Docs](https://kubernetes.io/docs/home/)
- [Helm — Getting Started](https://helm.sh/docs/chart_template_guide/getting_started/)
- [k3d — local K8s](https://k3d.io/)
- [Video: Kubernetes Tutorial (TechWorld with Nana — full course)](https://www.youtube.com/watch?v=X48VuDVv0do)
- [Video: Helm explained (TechWorld with Nana)](https://www.youtube.com/watch?v=-ykwb1d0DXU)
- [Learn Kubernetes by Doing (Killer.sh)](https://killercoda.com/killer-shell-cka)

---

## Kolejność priorytetów — TL;DR

```
TERAZ:
  0.1 Cleanup duplikatów
  0.2 Service layer refactor
  0.3 Docker compose fix

NASTĘPNIE (wybierz jedno na raz):
  1.1 → 1.2 JWT + RBAC
  2.1 Vault
  5.1 Prometheus metrics (2 linijki kodu, duży efekt)
  5.2 Loki

POTEM:
  3.1 → 3.2 SNMP/SSH w network-worker
  4.1 → 4.2 Frontend minimum
  6.1 Traefik
  7.1 Agent

INŻYNIERKA:
  8.x Kubernetes + Helm
```

---

## Zasady pracy

- Każdy krok = osobna branch + PR
- Branch naming: `feat/jwt-auth`, `fix/celery-duplicate`, `chore/cleanup-test-folder`
- Commit convention: masz już opisany w `.github/COMMIT_COVENCTIONS.md` — trzymaj się go
- Przed merge: CI musi być zielone
- Po każdej fazie: zaktualizuj `README.md` i odpowiedni plik w `docs/`

---

*Ostatnia aktualizacja: 2026-03-16*
