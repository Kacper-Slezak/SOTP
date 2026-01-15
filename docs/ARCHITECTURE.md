# SOTP Architecture Documentation

## 1. System Overview

SOTP (System Observability & Telemetry Platform) is a hybrid cloud-native monitoring solution designed to bridge the gap between legacy network infrastructure and modern server environments.

Unlike traditional NMS (Network Monitoring Systems), SOTP employs a microservices architecture to handle two distinct telemetry models:

1. **Agentless (Pull):** For network devices (Routers, Switches) via SNMP/ICMP.
2. **Agent-based (Push):** For servers and cloud instances via a custom lightweight agent.

---

## 2. High-Level Architecture

The system is designed as a **Monorepo** containing independent microservices deployed on Kubernetes.

```mermaid
 flowchart TD

    subgraph "Infrastructure (Home Lab)"

        Ingress["Ingress Controller<br/>(Traefik)"]



        subgraph "Services"

            Core["SOTP Core API"]

            DB[("TimescaleDB")]

            Redis[("Redis")]

            NetWorker["Network Worker"]



            Core -->|"Zapis/Odczyt"| DB

            Core -->|"Cache"| Redis

            NetWorker -->|"Kolejka Zadań"| Redis

            NetWorker -->|"Zapis Wyników"| Core

        end

    end


    subgraph "Świat Zewnętrzny (Urządzenia)"

        Router1["Router Cisco"]

        Router2["Switch HP"]

        Server1["Twój Serwer / Laptop"]

        Agent["SOTP Python Agent"]



        NetWorker -- "PULL (SNMP/ICMP)" --> Router1

        NetWorker -- "PULL (SNMP/ICMP)" --> Router2

        Agent -- "PUSH (HTTP POST)" --> Ingress

        Agent -.-> Server1

    end


    User["Użytkownik"] -->|"Przeglądarka"| Frontend["SOTP Frontend"]

    Frontend -->|"API REST"| Ingress --> Core

    end

```

---

## 3. Core Components

### 3.1. Core Backend (`apps/core-backend`)

* **Role:** The central brain of the platform.
* **Tech Stack:** Python 3.11, FastAPI.
* **Responsibilities:**
* REST API for the Frontend.
* Ingestion endpoint for SOTP Agents (`POST /api/v1/ingest`).
* Authentication & Authorization.
* Data aggregation and storage in TimescaleDB.

### 3.2. Network Worker (`apps/network-worker`)

* **Role:** A specialized worker for network tasks.
* **Tech Stack:** Python, Celery (optional), Netmiko, PySNMP.
* **Responsibilities:**
* Executes active checks (ICMP Ping) against routers.
* Polls SNMP data from network devices.
* Connects to routers via SSH for configuration backups.
* Operates asynchronously from the Core API.

### 3.3. SOTP Agent (`apps/sotp-agent`)

* **Role:** Lightweight metric collector.
* **Tech Stack:** Python (Zero-dependency mostly).
* **Responsibilities:**
* Runs as a systemd service on target Linux servers.
* Collects CPU, RAM, and Disk usage via `psutil`.
* Pushes data to the Core API at defined intervals.

### 3.4. Web Frontend (`apps/web-frontend`)

* **Role:** User Interface.
* **Tech Stack:** Next.js, React, Tailwind CSS.
* **Responsibilities:**
* Visualizes real-time metrics.
* Provides dashboards for both Servers and Network Devices.

---

## 4. Data Flow

### Scenario A: Server Monitoring (Push Model)

1. **Agent** collects CPU usage on a remote server.
2. **Agent** sends a JSON payload to `https://sotp.domain/api/v1/ingest`.
3. **Core API** validates the token and saves the metric to **TimescaleDB** (hypertable).
4. **Frontend** queries the API to update the live chart.

### Scenario B: Router Monitoring (Pull Model)

1. **Network Worker** receives a task from **Redis** (or internal scheduler).
2. **Worker** sends an SNMP GET request to the target Router IP.
3. **Router** responds with interface statistics.
4. **Worker** processes the data and saves it to **Core API** (or directly to DB).

---

## 5. Technology Decisions

* **Kubernetes (K3s):** Chosen for orchestration capabilities and self-healing.
* **TimescaleDB:** Chosen over standard PostgreSQL for superior performance with time-series data.
* **FastAPI:** Selected for high performance (async) and automatic documentation generation.
* **Monorepo:** Used to maintain code consistency across all services.
