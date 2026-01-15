# SOTP Deployment Guide

This document provides instructions for deploying the SOTP application to a production environment.

## 1. Server Requirements

Before proceeding with the deployment, ensure the server meets the following requirements:

* **Operating System:** A modern Linux distribution (e.g., Ubuntu 22.04 LTS, Debian 11).
* **CPU:** 2+ cores
* **RAM:** 8GB+
* **Storage:** 20GB+ of free space.
* **Software:**
    * **Docker Engine:** Latest stable version.
    * **Docker Compose:** Latest stable version.
    * **Git:** For cloning the repository.
    * **Make:** For using helper commands.

## 2. Initial Setup

These steps should be performed only once when setting up a new production server.

### 2.1. Clone the Repository
Clone the project repository to the server:
```bash
git clone [URL_DO_REPOZYTORIUM]
cd sotp
````

### 2.2. Configure Environment Variables

Copy the example environment file and fill it with your production values (database passwords, secret keys, etc.).

**NEVER commit the `.env` file to the repository.**

```bash
cp .env.example .env
nano .env  # Edit the file with your production secrets
```

### 2.3. Initialize Docker Swarm (Recommended)

For better management and potential scaling, it's recommended to initialize Docker Swarm, even on a single node.

```bash
docker swarm init
```

## 3\. First-Time Deployment

1.  **Pull the latest changes** from the `main` branch (or the specific release tag):

    ```bash
    git pull
    git checkout v1.0.0 # Example release tag
    ```

2.  **Build the production images:**
    This command will build all necessary Docker images based on the production configuration.

    ```bash
    make build
    ```

    *(This runs `docker-compose -f infrastructure/docker/docker-compose.prod.yml build`)*

3.  **Run the application stack:**
    This command will start all services in detached mode.

    ```bash
    make deploy
    ```

    *(This runs `docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d`)*

4.  **Verify the deployment:**
    Check the status of all running containers. All services should be in a `healthy` or `running` state.

    ```bash
    docker ps
    ```

    You should also check the logs for any potential errors during startup.

    ```bash
    docker-compose -f infrastructure/docker/docker-compose.prod.yml logs -f
    ```

## 4\. Updating the Application (New Version Deployment)

The deployment process is designed for zero-downtime updates.

1.  **Pull the latest version:**

    ```bash
    git pull
    git checkout v1.1.0 # Pull the new release tag
    ```

2.  **Re-deploy the stack:**
    Docker Compose is smart enough to only rebuild and restart the services that have changed.

    ```bash
    make deploy
    ```

3.  **Clean up old images (Optional):**
    To free up disk space, you can periodically remove old, unused Docker images.

    ```bash
    docker image prune -f
    ```
