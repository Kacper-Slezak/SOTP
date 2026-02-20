# Dokumentacja Schematu Bazy Danych

System SOTP wykorzystuje PostgreSQL do danych relacyjnych oraz TimescaleDB do danych telemetrycznych.

## Diagram ERD

```mermaid
erDiagram
    USER ||--o{ DEVICE : creates
    DEVICE ||--o{ DEVICE_METRIC : has

    USER {
        int id PK
        string email
        string name
        string role "ADMIN, OPERATOR"
        boolean is_active
    }

    DEVICE {
        int id PK
        string name
        string ip_address
        string device_type
        string vendor
        int created_by_id FK
    }

    DEVICE_METRIC {
        timestamp time PK
        int device_id FK
        string metric_name
        float value
    }

```

## Opis Tabel

* **users**: Przechowuje konta użytkowników wraz z ich rolami (RBAC).
* **devices**: Inwentarz urządzeń sieciowych (routery, switche, serwery).
* **device_metrics**: Tabela TimescaleDB (hypertable) przechowująca historię wydajności (CPU, RAM).
