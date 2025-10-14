# SOTP User Stories

This document contains a list of User Stories that define the features of the SOTP application from the perspective of its users. These stories serve as the foundation for our development backlog.

## EPIC 1: Device Inventory Management

### User Stories
* **As an** administrator, **I want to** add a new network device to the system by providing its name and IP address, **so that** I can start monitoring it.
* **As an** operator, **I want to** see a list of all monitored devices with their current status (Up/Down), **so that** I can quickly assess the health of the network.
* **As an** administrator, **I want to** edit the properties of an existing device (e.g., change its name or location), **so that** the inventory data remains up-to-date.
* **As an** administrator, **I want to** delete a device from the system, **so that** decommissioned hardware is no longer monitored.
* **As an** operator, **I want to** filter and search the device list by name, IP address, or location, **so that** I can quickly find the specific device I'm looking for.

## EPIC 2: Authentication & User Management

### User Stories
* **As a** new user, **I want to** be able to register an account, **so that** I can get access to the platform.
* **As a** user, **I want to** be able to log in to the system with my credentials, **so that** I can access the monitoring dashboards.
* **As a** user, **I want to** be able to log out of the system, **so that** I can secure my session.
* **As an** administrator, **I want to** be able to see a list of all users in the system, **so that** I can manage their accounts.
* **As an** administrator, **I want to** be able to assign different roles (e.g., Admin, Operator) to users, **so that** I can control their access permissions.

## EPIC 3: Device Monitoring

### User Stories
* **As an** operator, **I want to** see the real-time latency (ping RTT) and packet loss for a device, **so that** I can diagnose network connectivity issues.
* **As an** administrator, **I want to** configure SNMP credentials for a device, **so that** the system can collect detailed metrics from it.
* **As an** operator, **I want to** view historical charts of CPU and memory utilization for a specific device, **so that** I can analyze its performance over time.
* **As an** operator, **I want to** see a chart of bandwidth usage (in/out) for a device's network interfaces, **so that** I can identify traffic bottlenecks.
* **As an** administrator, **I want to** be able to securely execute a predefined `show` command on a device via SSH from the UI, **so that** I can perform quick diagnostics without leaving the platform.

## EPIC 4: Alerting

### User Stories
* **As an** administrator, **I want to** create a new alert rule based on a metric threshold (e.g., "alert when CPU is above 90% for 5 minutes"), **so that** I can be proactively notified of problems.
* **As an** operator, **I want to** see a list of all currently active alerts, **so that** I know what issues require my immediate attention.
* **As an** operator, **I want to** receive a notification via Slack when a critical alert is triggered, **so that** I can react quickly even when not looking at the dashboard.
* **As an** operator, **I want to** be able to "acknowledge" an alert, **so that** the rest of the team knows I am working on it.