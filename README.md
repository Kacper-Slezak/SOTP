Of course. Here is a comprehensive `README.md` file for the SOTP project, written in English. It's based on the architecture, requirements, and setup procedures found in your project's documentation.

-----

# SOTP - System Observability & Telemetry Platform

SOTP (System Observability & Telemetry Platform) is a modern, scalable solution for monitoring network devices. It provides real-time insights into device availability, performance metrics, and allows for quick diagnostics through a clean and responsive web interface.

## About The Project

This platform is designed for network administrators and operators who need a centralized system for managing and monitoring their network infrastructure. The entire application is containerized using Docker, ensuring a consistent and easy-to-deploy environment.

Key functionalities include device inventory management, multi-protocol monitoring (ICMP, SNMP), secure command execution via SSH, and a robust, rule-based alerting system.

-----

## Features

The platform is built with a rich set of features to cover the entire monitoring lifecycle:

  * **Device Management**: Full CRUD (Create, Read, Update, Delete) functionality for network devices.
  * **Comprehensive Monitoring**:
      * **ICMP**: Monitor device availability and latency using ping.
      * **SNMP**: Collect key performance metrics like CPU, memory, and interface traffic.
      * **SSH**: Execute predefined, read-only commands for quick diagnostics.
  * **Advanced Alerting**:
      * Define custom alert rules based on metric thresholds (e.g., CPU \> 90%).
      * Receive notifications through multiple channels, including Email, Slack, and Webhooks.
  * **Secure by Design**:
      * API secured with JSON Web Tokens (JWT).
      * Role-Based Access Control (RBAC) to manage user permissions.
      * Sensitive data is securely stored using HashiCorp Vault.
  * **Reporting & Auditing**:
      * Generate summary reports in CSV and PDF formats.
      * Track all critical user actions through a detailed audit log.

-----

## Technology Stack

The SOTP architecture is built on a modern, service-oriented technology stack, chosen for performance and scalability.

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend** | [Next.js](https://nextjs.org/) (React) | Provides a modern, high-performance, server-rendered user interface. |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) (Python) | Asynchronous framework ideal for high-performance, I/O-bound network and database tasks. |
| **Databases** | **PostgreSQL** & **TimescaleDB** | PostgreSQL for relational data (inventory, users) and TimescaleDB for high-performance time-series metric data. |
| **Task Queue** | [Celery](https://docs.celeryq.dev/) & **Redis** | Manages asynchronous background tasks for data collection, ensuring the API remains responsive. |
| **Containerization**| **Docker** & **Docker Compose** | Ensures consistency across all environments and simplifies deployment. |
| **Secrets Mgmt** | [HashiCorp Vault](https://www.vaultproject.io/) | Centralized and secure storage for all secrets like database credentials and API keys. |

-----

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

You need the following software installed on your machine:

  * Docker Engine
  * Docker Compose
  * Git
  * Make

### Installation & Setup

1.  **Clone the repository:**

    ```sh
    git clone https://your-repository-url/sotp.git
    cd sotp
    ```

2.  **Configure Environment Variables:**
    Copy the example environment file. This file contains all the configuration variables needed to run the application services.

    ```sh
    cp .env.example .env
    ```

    Now, open the `.env` file and review the default values. For local development, they are typically sufficient, but you can customize them if needed. **Never commit the `.env` file to Git**.

3.  **Launch the Development Environment:**
    This single command builds the Docker images and starts all services (backend, frontend, databases, etc.) in the background.

    ```sh
    make dev
    ```

You should now be able to access:

  * **Frontend Application**: `http://localhost:3000`
  * **Backend API Docs**: `http://localhost:8000/docs`

-----

## Usage

The project includes a `Makefile` with convenient commands to manage the development environment.

  * **Start all services:**

    ```sh
    make dev
    ```

  * **Stop and remove all services:**

    ```sh
    make down
    ```

  * **View logs from all running services:**

    ```sh
    make logs
    ```

  * **Open a shell inside the backend container:**

    ```sh
    make shell-backend
    ```

  * **Open a shell inside the frontend container:**

    ```sh
    make shell-frontend
    ```

  * **Run backend tests:**

    ```sh
    make test
    ```

-----

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

Please read our `docs/CONTRIBUTING.md` file for details on our code of conduct and the process for submitting pull requests to us.