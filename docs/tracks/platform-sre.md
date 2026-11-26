# Track: Platform, DevOps & SRE

> **Status:** Proposal · open for contributors
> **Part of:** [Future Work & Contributor Tracks](../FUTURE_WORK.md) · label `track: platform`

**For people into:** Kubernetes, CI/CD, infrastructure as code, reliability engineering.
**You will practice:** developer experience, release engineering, disaster recovery, capacity and cost thinking, and running reliability exercises.

The core roadmap (P2–P6) already builds the platform: hardened images, K3d with Helm, ArgoCD, Vault, observability and Terraform. This track covers what comes **around** it, so it does not duplicate those phases.

---

## Work Packages

| ID | Package | Difficulty | Needs from core |
|---|---|---|---|
| PLAT-1 | Dev container & one-command onboarding | 🟢 Starter | — |
| PLAT-2 | Dependency update automation | 🟢 Starter | P2.7 |
| PLAT-3 | Preview environment per pull request | 🟠 Hard | P3, P4.2 |
| PLAT-4 | Backup, restore & DR drill | 🟡 Medium | P3.4 (CloudNativePG) |
| PLAT-5 | Release engineering | 🟡 Medium | P2.5 |
| PLAT-6 | Game days | 🟡 Medium | P5.4, P8.4 |
| PLAT-7 | Capacity & cost model | 🟡 Medium | P6 |
| PLAT-8 | Collector scaling under load | 🟠 Hard | P3.7 (KEDA) |

### PLAT-1 — Dev Container & One-Command Onboarding
- A `devcontainer.json` with all tools pinned, so a new contributor gets a working environment in minutes.
- **Done when:** a new contributor goes from a clean clone to a logged-in UI by following one page, and that page records the time it took.

### PLAT-2 — Dependency Update Automation
- Renovate or Dependabot with grouped updates, auto-merge for patch versions with green CI, and a weekly schedule.
- **Done when:** dependency PRs arrive grouped and on schedule, and a broken update is blocked by CI.

### PLAT-3 — Preview Environment per Pull Request
- Each PR gets its own namespace with seeded demo data (ArgoCD ApplicationSet), and the link is posted on the PR. The namespace is removed when the PR closes.
- **Done when:** a reviewer can click into a live environment for any open PR.

### PLAT-4 — Backup, Restore & DR Drill
- Scheduled backups of PostgreSQL and TimescaleDB, plus Kubernetes resources (e.g. Velero).
- A documented restore procedure with measured recovery time (RTO) and data-loss window (RPO).
- **Done when:** a quarterly restore drill is performed and its RTO/RPO numbers are recorded.

### PLAT-5 — Release Engineering
- Semantic versioning, automated changelog from conventional commits, release notes, and a rollback procedure.
- **Done when:** `v0.x.0` is cut from a tag with notes, signed images and a tested rollback.

### PLAT-6 — Game Days
- A monthly exercise that runs one [flagship scenario](../FUTURE_WORK.md#cross-track-flagship-scenarios): inject a failure, let on-call respond, write a postmortem.
- **Done when:** at least one game day is completed with a postmortem and follow-up issues.

### PLAT-7 — Capacity & Cost Model
- How much CPU, memory and storage does SOTP need per 100 monitored devices? Measure it and extrapolate.
- Map it to a cloud cost estimate using the Terraform from P6 (Infracost).
- **Done when:** a table shows resources and cost per scale step, with the measurement method.

### PLAT-8 — Collector Scaling Under Load
- Simulate thousands of devices and measure polling lag, queue depth and worker scaling with KEDA.
- **Done when:** a graph shows the device count at which polling falls behind, with and without autoscaling.

---

## Related Roadmap Steps
- [P2 DevSecOps Pipeline](../SOTP_ROADMAP.md#phase-p2--devsecops-pipeline), [P3 Kubernetes](../SOTP_ROADMAP.md#phase-p3--kubernetes-k3d--helm), [P4 GitOps](../SOTP_ROADMAP.md#phase-p4--gitops-secrets--policy), [P5 Observability](../SOTP_ROADMAP.md#phase-p5--observability--sre), [8.4 Chaos Mesh](../SOTP_ROADMAP.md#step-84--chaos-mesh-fault-injection-experiments), [8.5 k6](../SOTP_ROADMAP.md#step-85--performance--load-testing-with-k6).
