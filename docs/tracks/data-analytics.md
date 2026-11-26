# Track: Data & Analytics

> **Status:** Proposal · open for contributors
> **Part of:** [Future Work & Contributor Tracks](../FUTURE_WORK.md) · label `track: data`

**For people into:** SQL, BI and dashboards, statistics, reporting.
**You will practice:** time-series modelling in TimescaleDB, defining metrics people can trust, reporting for non-technical readers, and data quality.

SOTP collects telemetry for every device at a fixed interval. This track turns that raw data into answers: how available was the network last month, what will run out of capacity next, and can we trust the numbers.

---

## Work Packages

| ID | Package | Difficulty | Needs from core |
|---|---|---|---|
| DATA-1 | Data dictionary & metric definitions | 🟢 Starter | — |
| DATA-2 | Continuous aggregates & retention | 🟡 Medium | P1 |
| DATA-3 | SLA & availability report | 🟢 Starter | DATA-2 |
| DATA-4 | Data quality checks | 🟡 Medium | P1 |
| DATA-5 | Capacity forecasting | 🟡 Medium | P7.3 (interface stats) |
| DATA-6 | Fleet health scorecard | 🟢 Starter | DATA-2 |
| DATA-7 | Public demo dataset | 🟡 Medium | DATA-4, NET-1 |

### DATA-1 — Data Dictionary & Metric Definitions
- One page that defines each table, column and metric, e.g. what exactly "availability" means: share of successful pings, or share of minutes with at least one successful ping.
- **Done when:** every number on the main dashboards links to a definition.

### DATA-2 — Continuous Aggregates & Retention
- TimescaleDB continuous aggregates per minute, hour and day, plus retention and compression policies.
- Measure dashboard query time before and after on the same data.
- **Done when:** a before/after table shows query times, and raw data older than the retention window is removed automatically.

### DATA-3 — SLA & Availability Report
- A monthly report per device and site: availability against target, number and length of outages, worst offenders. Exported as PDF/CSV.
- **Done when:** the report for a month in the demo data matches a hand calculation for at least one device.

### DATA-4 — Data Quality Checks
- Automated checks: missing samples, duplicate timestamps, impossible values (negative RTT, loss over 100%), clock skew between collectors.
- **Done when:** checks run on a schedule, and injected bad data triggers the right check.

### DATA-5 — Capacity Forecasting
- Forecast interface utilisation and storage growth, and estimate when thresholds will be crossed. Start from a linear trend and only add complexity if it reduces the error.
- **Done when:** the forecast error is measured on held-out weeks and shown with the forecast.

### DATA-6 — Fleet Health Scorecard
- One view for a manager: devices up and down, open incidents, SLA status, top risks. It links with SEC-3 and NET-6 once they exist.
- **Done when:** someone outside the project can explain the state of the fleet from the scorecard alone.

### DATA-7 — Public Demo Dataset
- A sanitised, versioned dataset from the lab (no real IPs or credentials) with a data card, so others can reproduce analyses and ML experiments.
- **Done when:** the dataset can be downloaded, loaded with one command, and is described in a data card.

---

## Related Work
- [ML-0 Dataset & data card](ml-mlops.md#ml-0--dataset--data-card) shares the export format with DATA-7.
- Roadmap: [7.5 Device details page](../SOTP_ROADMAP.md#step-75--device-details-page-with-historical-metrics), [7.9 Fleet summary dashboard](../SOTP_ROADMAP.md#step-79--home-fleet-summary-dashboard), [5.7 Dashboards as code](../SOTP_ROADMAP.md#step-57--grafana-dashboards-as-code).
