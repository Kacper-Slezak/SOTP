# Frequently Asked Questions (FAQ)

## General

### Q: What is SOTP?

A: SOTP stands for **System Observability & Telemetry Platform**. It is a modern, scalable solution for monitoring network devices, providing real-time insights into availability and performance metrics.

### Q: What technologies does the platform use?

A: The platform is built on a modern stack including **FastAPI** (Python) for the backend, **Next.js (React)** for the frontend, **PostgreSQL** for relational data, and **TimescaleDB** for high-performance time-series data.

## Monitoring & Data

### Q: What protocols are supported for monitoring?

A: SOTP currently supports:

* **ICMP** for device availability and latency (ping).
* **SNMP** for collecting key performance metrics (CPU, memory, traffic).
* **SSH** for executing predefined, read-only commands for quick diagnostics.

### Q: Why are there two databases?

A: We use a dual-database approach for performance and scalability:

* **PostgreSQL** stores slow-changing, relational data like device inventory and users.
* **TimescaleDB** is optimized for high-volume, time-series metric data, ensuring faster performance for historical charts and analytics.

## Security & Access

### Q: How are sensitive credentials secured?

A: Sensitive data, such as SNMP community strings or SSH passwords, are not stored directly in the database or environment variables. Instead, they are securely stored in **HashiCorp Vault**. The database only stores the secure path to the credential within Vault.

### Q: What are the different user roles?

A: The system supports Role-Based Access Control (RBAC) with the following roles:

* **ADMIN**: Full control, including user and system settings.
* **OPERATOR**: Manages devices and responds to alerts.
* **AUDITOR**: View-only access to audit logs and reports.
* **READONLY**: General view-only access to dashboards and device data.
