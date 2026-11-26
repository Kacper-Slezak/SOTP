# Track: ML & MLOps

> **Status:** Proposal · open for contributors
> **Part of:** [Future Work & Contributor Tracks](../FUTURE_WORK.md) · label `track: ml`
> **Relation to the main roadmap:** a **parallel track**. It never blocks phases P0–P8 in [`SOTP_ROADMAP.md`](../SOTP_ROADMAP.md), and the core platform must keep working with the whole track switched off.

SOTP already collects time-series data about network devices (ICMP reachability, RTT, packet loss, and later SNMP counters and syslog). That makes it a good testbed for **anomaly detection on real infrastructure telemetry** and for doing ML the way production teams do it: versioned data, reproducible training, signed model artifacts, shadow deployment, and drift monitoring.

This document is for people who want to work on ML or MLOps without learning the whole platform first. Each work package has a clear input, a clear output, and a definition of done, so several people can work on it at the same time.

---

## Table of Contents

1. [Guiding Principles](#guiding-principles)
2. [Integration Contract](#integration-contract)
3. [Work Packages — ML](#work-packages--ml)
4. [Work Packages — MLOps](#work-packages--mlops)
5. [Dependency Map](#dependency-map)
6. [How to Join](#how-to-join)
7. [Prior Work & References](#prior-work--references)

---

## Guiding Principles

1. **Data first.** Every package starts with a short data report: sample rows, ranges, missing values, counts per device, one histogram. No model gets trained before the report exists.
2. **Baseline before model.** A learned model is merged only if it beats the statistical baseline (ML-1) on the same evaluation set.
3. **Ground truth comes from fault injection.** Telemetry does not come labeled, so faults are injected on purpose (Chaos Mesh, Containerlab link impairments, `tc netem`) and the injection log provides the labels. Chaos experiments then double as an ML dataset generator.
4. **Honest metrics.** Report precision, recall, and detection delay with the number of incidents and the spread across runs or devices. Train/test splits are made **by time and by device**, never randomly by row, to avoid leakage.
5. **Safe artifacts.** Never load untrusted `pickle`/`joblib` files. Ship models as ONNX, `safetensors`, or `skops`, scan them, and sign them like container images (see MLOPS-2).
6. **Small and replaceable.** Plain scripts over notebooks in `main`. Each new dependency is justified in the PR description.

---

## Integration Contract

The ML track talks to the platform only through this contract. Anything behind it is the contributor's choice.

```
TimescaleDB (ping_results, snmp_*)      Loki (syslog, P5)
              │  read-only SQL                │  LogQL
              ▼                               ▼
        ┌──────────────────────────────────────────┐
        │  apps/ml_worker  (Celery task / K8s Job) │
        │  feature build → score → threshold       │
        └───────────────┬──────────────────────────┘
                        │ write
                        ▼
          TimescaleDB: anomaly_scores (hypertable)
          Prometheus:  sotp_ml_* metrics
                        │
                        ▼
          Grafana panel · alert rules · device page in UI
```

**Input (exists today):** `ping_results` hypertable with `timestamp`, `device_id`, `ip_address`, `is_alive`, `rtt_avg_ms`, `packet_loss_percent`.

**Output (to be added in ML-0):** `anomaly_scores` hypertable:

| Column | Type | Meaning |
|---|---|---|
| `timestamp` | timestamptz | Scored window end |
| `device_id` | int | FK to `devices.id` |
| `signal` | text | `icmp.rtt`, `icmp.loss`, `snmp.if_errors`, `syslog`, … |
| `score` | float | Higher means more anomalous |
| `is_anomaly` | bool | `score >= threshold` |
| `model_name` / `model_version` | text | Which artifact produced the score |
| `mode` | text | `shadow` or `active` |

**Feature flag:** `ML_ENABLED=false` by default. With the flag off, nothing in `core_backend` or `network_worker` changes.

---

## Work Packages — ML

| ID | Package | Difficulty | Needs from core |
|---|---|---|---|
| ML-0 | Dataset export, data card, fault-injection labels | 🟢 Starter | P1 (pings flowing) |
| ML-1 | Statistical baseline for RTT / loss anomalies | 🟢 Starter | ML-0 |
| ML-2 | Learned detector on metrics | 🟡 Medium | ML-1 |
| ML-3 | Log anomaly detection on syslog | 🟠 Hard | P5.2 (Loki) |
| ML-4 | Explainability for each alert | 🟡 Medium | ML-2 or ML-3 |
| ML-5 | Flow-based traffic classification (research) | 🔴 Research | Flow export (not planned yet) |

### ML-0 — Dataset & Data Card
- Export `ping_results` (and SNMP tables once they exist) to Parquet with a fixed schema and a version tag.
- Fault-injection runbook: inject latency, loss, and device down events against the demo devices, and log each injection as `(device_id, start, end, fault_type)`.
- `DATA_CARD.md`: collection period, number of devices, sampling interval, missing-data rate, label coverage, known biases.
- **Done when:** one command reproduces the dataset, and the data card includes per-device counts and one histogram per signal.

### ML-1 — Statistical Baseline
- Per-device rolling baselines: EWMA with robust z-score (median/MAD), optionally with daily seasonality.
- Evaluation script: precision, recall, F1 and mean detection delay against the ML-0 labels, reported per device and overall.
- **Done when:** scores are written to `anomaly_scores` in `shadow` mode and appear on a Grafana panel next to the raw RTT.

### ML-2 — Learned Detector on Metrics
- Candidates in order of complexity: Isolation Forest → small MLP autoencoder → sequence model. Stop at the first one that beats ML-1 by a margin larger than the run-to-run spread.
- Multivariate input per device (RTT, loss, later SNMP interface errors and CPU).
- **Done when:** a comparison table against ML-1 on the same split is in the PR, and the model is exported in a safe format (MLOPS-5).

### ML-3 — Log Anomaly Detection (Syslog)
- Pipeline: syslog → Loki → template mining with [Drain3](https://github.com/logpai/Drain3) → event sequences per device and time window → anomaly score from next-event prediction loss or reconstruction error.
- Start with an MLP autoencoder. Try a small transformer only if it measurably beats the MLP.
- Labels come from the ML-0 runbook (link flaps, interface shutdowns, auth failures generated on purpose in Containerlab).
- **Done when:** the template vocabulary is versioned, unseen templates map to `[UNK]` and are counted as a drift signal, and the scores reach `anomaly_scores` with `signal = 'syslog'`.

### ML-4 — Explainability
- For each anomaly: top contributing features (metrics) or the events that triggered it (logs), via SHAP or Captum.
- Show the explanation on the device details page (P7.5) and in the alert payload.
- **Done when:** an operator can answer "why did this fire?" without opening a notebook.

### ML-5 — Traffic Classification (Research, Optional)
- Classify traffic per application from flow statistics (packet sizes, inter-arrival times, burstiness).
- **Blocked:** SOTP does not see packets or flows today. It requires an IPFIX/sFlow collector or packet capture in `sotp_agent` first, plus a dataset that is not tied to a single host.
- Start with a written proposal (ADR) before any code.

---

## Work Packages — MLOps

| ID | Package | Difficulty | Needs from core |
|---|---|---|---|
| MLOPS-1 | Experiment tracking & model registry | 🟢 Starter | — |
| MLOPS-2 | Models as signed OCI artifacts | 🟡 Medium | P2.5–P2.6 (GHCR, Cosign) |
| MLOPS-3 | Training & scoring on Kubernetes | 🟡 Medium | P3 (K3d + Helm), P4.2 (ArgoCD) |
| MLOPS-4 | Shadow → active rollout | 🟡 Medium | MLOPS-3 |
| MLOPS-5 | Model supply-chain security | 🟡 Medium | P2 |
| MLOPS-6 | Drift & model performance monitoring | 🟡 Medium | P5.3 (Prometheus Operator) |

### MLOPS-1 — Experiment Tracking & Registry
- MLflow (or an equally simple alternative): params, metrics, dataset version, and git SHA for every training run.
- **Done when:** every number in an ML PR links to a run.

### MLOPS-2 — Models as Signed OCI Artifacts
- Push model artifacts to GHCR with ORAS next to the service images, sign them with Cosign, and attach a model card (dataset version, metrics, intended use).
- `ml_worker` verifies the signature before loading.
- **Done when:** an unsigned or tampered model is refused at startup.

### MLOPS-3 — Training & Scoring on Kubernetes
- Retraining as a Kubernetes `CronJob`, scoring as a Celery task or `Deployment`. Both are part of the Helm chart and synced by ArgoCD.
- **Done when:** `helm upgrade` with a new `model.version` value rolls the scorer without manual steps.

### MLOPS-4 — Shadow → Active Rollout
- A new model runs in `shadow` mode next to the current one, and both write to `anomaly_scores`. Promotion to `active` is a reviewed Git change.
- **Done when:** a Grafana dashboard compares the shadow and active models on the same time range.

### MLOPS-5 — Model Supply-Chain Security
- Forbid pickle-based formats in CI. Scan artifacts (e.g. ModelScan) and include ML dependencies in the SBOM and `pip-audit` runs.
- Fits the [STRIDE threat model](../SOTP_ROADMAP.md#step-213--threat-model-stride) as a new trust boundary.

### MLOPS-6 — Drift & Performance Monitoring
- Export `sotp_ml_score_bucket`, the anomaly rate, the share of unseen log templates, and feature distribution statistics to Prometheus.
- Alert when the anomaly rate or input distribution leaves its normal band, and treat the alert as a retraining trigger.

---

## Dependency Map

```
P1 ─► ML-0 ─► ML-1 ─► ML-2 ─► ML-4
                │
P5.2 (Loki) ────┴──────► ML-3 ─► ML-4
P8.4 Chaos Mesh / P8.6 Containerlab ─► labels for ML-0 / ML-3

MLOPS-1 (anytime)
P2 ─► MLOPS-2, MLOPS-5
P3 + P4.2 ─► MLOPS-3 ─► MLOPS-4
P5.3 ─► MLOPS-6
```

**Good starting points that don't wait on the core roadmap:** ML-0 (on data from `make dev` + `make seed`), ML-1, and MLOPS-1.

---

## How to Join

General roles, process and Definition of Done are in the [hub](../FUTURE_WORK.md#how-to-join). On top of that, every ML proposal states:

- **Data:** which tables or exports, which time range, how many devices.
- **Baseline:** what the method is compared against (ML-1 at minimum).
- **Metric:** precision, recall and detection delay, with n and spread.
- **Split:** by time and by device, never randomly by row.

---

## Prior Work & References

**Related student projects (reuse code only with the authors' permission):**
- *Anomaly detection in HDFS logs with transformers*: Drain templates, a light transformer vs. an MLP autoencoder, Captum explainability. The direct inspiration for ML-3.
- [Online ML-based packet classification](https://github.com/Martynka123-code/Online-machine-learning-based-packet-classification-project): flow-statistics Random Forest vs. byte-level CNN. The inspiration for ML-5.

**Papers**
- P. He et al., *Drain: An Online Log Parsing Approach with Fixed Depth Tree*, ICWS 2017.
- M. Du et al., *DeepLog: Anomaly Detection and Diagnosis from System Logs through Deep Learning*, CCS 2017.
- F. T. Liu et al., *Isolation Forest*, ICDM 2008.
- D. Sculley et al., *Hidden Technical Debt in Machine Learning Systems*, NeurIPS 2015.
- M. Lotfollahi et al., *Deep Packet: A Novel Approach for Encrypted Traffic Classification Using Deep Learning*, Soft Computing 2020.
