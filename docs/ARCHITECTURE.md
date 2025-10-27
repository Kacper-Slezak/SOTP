# SOTP System Architecture

This document describes the high-level architecture of the System Observability & Telemetry Platform (SOTP).

## 1. High-Level Diagram

The system is designed as a multi-layered, service-oriented architecture, optimized for scalability and maintainability. The diagram below illustrates the flow of data and interaction between components.

```

┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│  React/Next.js Frontend + Grafana Dashboards                │
└────────────────────┬────────────────────────────────────────┘
│
┌────────────────────▼────────────────────────────────────────┐
│                   API GATEWAY LAYER                          │
│  Traefik (Load Balancer + SSL) → FastAPI (REST + WebSocket) │
└────────────────────┬────────────────────────────────────────┘
│
┌────────────────────▼────────────────────────────────────────┐
│                  APPLICATION LAYER                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Inventory  │  │  Auth/RBAC   │  │   Alerting   │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
│
┌────────────────────▼────────────────────────────────────────┐
│                   CACHE & QUEUE LAYER                        │
│  Redis (Cache + Session) + Celery (Task Queue)              │
└────────────────────┬────────────────────────────────────────┘
│
┌────────────────────▼────────────────────────────────────────┐
│                  COLLECTOR WORKERS                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │   SNMP   │ │   ICMP   │ │   SSH    │ │  Syslog  │       │
│  │ Collector│ │ Collector│ │ Collector│ │ Collector│       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└────────────────────┬────────────────────────────────────────┘
│
┌────────────────────▼────────────────────────────────────────┐
│                   DATA LAYER                                 │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  PostgreSQL     │  │  TimescaleDB    │                  │
│  │  (Inventory)    │  │  (Time-Series)  │                  │
│  └─────────────────┘  └─────────────────┘                  │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  Loki           │  │  Vault          │                  │
│  │  (Logs)         │  │  (Secrets)      │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘

```


## 2. Key Technology Choices & Rationale

* **Containerization (Docker & Docker Compose):** The entire application stack is containerized. This ensures consistency across all environments (development, testing, production) and simplifies deployment.

* **Backend (FastAPI):** A FastAPI application written in Python serves as the core API and application layer. Its asynchronous nature is ideal for handling I/O-bound tasks like network polling and database queries, ensuring high performance.

* **Frontend (Next.js):** A Next.js (React) application provides a modern, server-rendered user interface. This choice allows for excellent performance, SEO capabilities, and a rich user experience.

* **Databases:**
    * **PostgreSQL** is used for storing relational, inventory-style data (users, devices, settings). It is a robust and reliable relational database.
    * **TimescaleDB** (a PostgreSQL extension) is used for all time-series data (metrics from collectors). This provides massive performance gains for analytical queries over time, which is critical for a monitoring platform.

* **Task Queuing (Celery & Redis):** Celery, with Redis as its message broker, is used to run all data collection tasks asynchronously in the background. This prevents the API from being blocked by long-running tasks and ensures the UI remains responsive.

* **Secrets Management (HashiCorp Vault):** Vault is used as a centralized and secure store for all secrets, such as database credentials and API keys. This avoids storing sensitive information in configuration files or environment variables.
