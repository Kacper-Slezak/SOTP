# Monitoring Setup (Prometheus and Grafana)

This document describes how to access the monitoring tools set up for the development environment.

## Access Details

| Service | Access URL | Default Credentials | Purpose |
| :--- | :--- | :--- | :--- |
| **Prometheus UI** | [http://localhost:9090](http://localhost:9090) | N/A | Time-series data collection and querying. |
| **Grafana UI** | [http://localhost:3001](http://localhost:3001) | `admin`/`admin` | Visualization and analysis of monitoring data. |

## Grafana Configuration Notes

The Grafana instance is configured with automatic provisioning on startup:

* **Datasource**: A datasource named **Prometheus** is automatically configured, pointing to the `prometheus:9090` service within the Docker network.
* **Dashboards**: Dashboards (like the example `Prometheus Self-Monitoring`) are automatically imported into the folder named **Prometheus Self-Monitoring**.

To log in to Grafana, use the default credentials: **admin** / **admin**. You will be prompted to change the password upon first login.
