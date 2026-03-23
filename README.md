<a id="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![project_license][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<br />
<div align="center">
  <a href="https://github.com/Kacper-Slezak/SOTP">
    <img src="apps/web_frontend/public/SOTP.png" alt="SOTP Logo" width="120" height="120">
  </a>

<h3 align="center">SOTP - System Observability & Telemetry Platform</h3>

  <p align="center">
    A modern, scalable solution for monitoring network devices with real-time insights and a clean web interface.
    <br />
    <a href="https://github.com/Kacper-Slezak/SOTP/tree/main/docs"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Kacper-Slezak/SOTP/issues/new?labels=bug&template=bug_report.md">Report Bug</a>
    &middot;
    <a href="https://github.com/Kacper-Slezak/SOTP/issues/new?labels=enhancement&template=feature_request.md">Request Feature</a>
  </p>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#features">Features</a></li>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## About The Project

SOTP (System Observability & Telemetry Platform) is a platform designed for network administrators and operators who need a centralized system for managing and monitoring their network infrastructure. 

The entire application is containerized using Docker, ensuring a consistent and easy-to-deploy environment. It features a microservices architecture, a high-performance backend, and a modern frontend UI.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Features

* **Device Management**: Full CRUD functionality for network devices.
* **Comprehensive Monitoring**: 
  * **ICMP**: Monitor device availability and latency.
  * **SNMP**: Collect key performance metrics (CPU, memory, interfaces).
  * **SSH**: Execute predefined, read-only commands for quick diagnostics.
* **Secure by Design**: API secured with JSON Web Tokens (JWT) and Role-Based Access Control (RBAC). Sensitive credentials managed by HashiCorp Vault.
* **Advanced Observability**: Pluggable metrics architecture saving time-series data into TimescaleDB.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Next][Next.js]][Next-url]
* [![React][React.js]][React-url]
* [![FastAPI][FastAPI.com]][FastAPI-url]
* [![Python][Python.org]][Python-url]
* [![PostgreSQL][PostgreSQL.org]][PostgreSQL-url]
* [![Docker][Docker.com]][Docker-url]
* [![Redis][Redis.io]][Redis-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

You need the following software installed on your machine:
* [Docker Engine](https://docs.docker.com/engine/install/)
* [Docker Compose](https://docs.docker.com/compose/install/)
* Git
* Make (optional, but highly recommended for using the provided `Makefile`)

### Installation

1. Clone the repo
   ```sh
   git clone [https://github.com/Kacper-Slezak/SOTP.git](https://github.com/Kacper-Slezak/SOTP.git)
   cd SOTP
   ```

2.  Configure Environment Variables

    ```sh
    cp .env.example .env
    ```

    *(Review the `.env` file. For local development, defaults are typically sufficient).*

3.  Launch the Development Environment

    ```sh
    make dev
    ```

You should now be able to access:

  * **Frontend Application**: `http://localhost:3000`
  * **Backend API Docs**: `http://localhost:8000/docs`

\<p align="right"\>(\<a href="\#readme-top"\>back to top\</a\>)\</p\>

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
  * **Run backend tests (in container):**
    ```sh
    make test
    ```

*For more detailed architectural documentation, please refer to the [docs/](https://www.google.com/url?sa=E&source=gmail&q=https://github.com/Kacper-Slezak/SOTP/tree/main/docs) directory.*

\<p align="right"\>(\<a href="\#readme-top"\>back to top\</a\>)\</p\>

## Roadmap

### Completed Milestones
* **Phase 0: Foundation & Core Architecture**
  * Developed the core backend using FastAPI.
  * Implemented an isolated asynchronous task worker using Celery & Redis.
  * Containerized the entire infrastructure (PostgreSQL, TimescaleDB, Vault).
  * Set up initial Device Management CRUD operations.
* **Phase 1: Security, Auth & CI/CD**
  * Integrated comprehensive JWT-based authentication.
  * Implemented Role-Based Access Control (RBAC) across all endpoints.
  * Built a robust GitHub Actions CI/CD pipeline (Linting, SAST, Pytest, Docker builds, Discord alerts).

### Current & Upcoming Phases
- [ ] **Phase 2: Vault Integration** (Secure SNMP/SSH credential storage directly in HashiCorp Vault)
- [ ] **Phase 3: Network Worker Refinement** (Advanced ICMP, SNMP, and SSH execution tasks)
- [ ] **Phase 4: Observability Stack** (Prometheus, Loki, Tempo, and Grafana Dashboards as Code)
- [ ] **Phase 5: Minimum Viable UI** (Next.js interactive Dashboard and Auth Pages)
- [ ] **Phase 6: SOTP Agent** (Standalone Python agent for push-based metric collection)
- [ ] **Phase 7: Kubernetes & GitOps** (K3d local cluster, Helm charts, and ArgoCD deployments)
- [ ] **Phase 8: Production Features** (Rule-based alerting system, Audit logs, interactive SSH console)

See the [open issues](https://github.com/Kacper-Slezak/SOTP/issues) for a full list of proposed features (and known issues). Check the detailed technical roadmap in `docs/SOTP_ROADMAP.md`.

\<p align="right"\>(\<a href="\#readme-top"\>back to top\</a\>)\</p\>

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star\! Thanks again\!

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'feat: Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

Please read our `docs/CONTRIBUTING.md` file for details on our code of conduct.

\<p align="right"\>(\<a href="\#readme-top"\>back to top\</a\>)\</p\>

## License

Distributed under the MIT License. See `LICENSE` for more information.

\<p align="right"\>(\<a href="\#readme-top"\>back to top\</a\>)\</p\>

## Contact

Kacper Slezak - [LinkedIn](https://www.google.com/search?q=https://www.linkedin.com/in/kacper-slezak)

Project Link: [https://github.com/Kacper-Slezak/SOTP](https://www.google.com/url?sa=E&source=gmail&q=https://github.com/Kacper-Slezak/SOTP)

\<p align="right"\>(\<a href="\#readme-top"\>back to top\</a\>)\</p\>
