# Track: Internet & Edge Observability

> **Status:** Proposal · open for contributors
> **Part of:** [Future Work & Contributor Tracks](../FUTURE_WORK.md) · label `track: internet`

**For people into:** CDNs, DNS, BGP, TLS, and how traffic actually crosses the Internet.
**You will practice:** synthetic monitoring from many vantage points, measuring user-facing performance, reading public routing data, and telling local faults apart from upstream ones.

SOTP today watches devices **inside** a network. This track adds the view from **outside**: is a service reachable and fast for users in different places, and if not, where does the path break?

---

## Work Packages

| ID | Package | Difficulty | Needs from core |
|---|---|---|---|
| NETX-1 | HTTP / DNS / TLS synthetic checks | 🟢 Starter | P1 |
| NETX-2 | Distributed probe agent | 🟡 Medium | P7.11–P7.12 (agent, ingestion API) |
| NETX-3 | Regional performance dashboard | 🟢 Starter | NETX-2 |
| NETX-4 | Traceroute & path-change detection | 🟡 Medium | NETX-2 |
| NETX-5 | BGP route monitoring | 🟠 Hard | — |
| NETX-6 | Public measurement data integration | 🟡 Medium | — |
| NETX-7 | "Local or upstream?" correlation | 🟠 Hard | NETX-3, NETX-5 |

### NETX-1 — HTTP / DNS / TLS Synthetic Checks
- New check types next to ICMP: HTTP status and timing breakdown (DNS, connect, TLS, first byte), DNS resolution per resolver, TLS certificate expiry and chain validity.
- Results go to TimescaleDB alongside `ping_results`.
- **Done when:** a certificate that expires in under 14 days raises a warning in Grafana.

### NETX-2 — Distributed Probe Agent
- A small, read-only probe that runs anywhere (a VM, a Raspberry Pi, a free cloud tier), runs the NETX-1 checks, and pushes results to the ingestion API with its location.
- Each probe has its own token, rate limits and a heartbeat.
- **Done when:** probes in at least three locations report the same target, and a stopped probe is marked offline.

### NETX-3 — Regional Performance Dashboard
- Latency and availability per target and probe location: map, percentiles (p50/p95/p99), and comparison across regions.
- **Done when:** degradation in one region is visible at a glance, with percentiles rather than averages.

### NETX-4 — Traceroute & Path-Change Detection
- Periodic traceroute or MTR from each probe. Store hops and their autonomous systems (ASNs).
- Detect path changes and attach them to latency changes.
- **Done when:** a path change is shown on the same timeline as the latency change it caused.

### NETX-5 — BGP Route Monitoring
- Watch prefixes of interest using a public BGP stream (e.g. RIPE RIS Live).
- Alert on origin AS changes, more-specific announcements and withdrawals, the typical signs of hijacks and leaks.
- **Done when:** a replayed historical incident triggers the right alert.

### NETX-6 — Public Measurement Data Integration
- Pull results from public measurement platforms (e.g. RIPE Atlas) within their terms of use, to compare SOTP probes with an independent source.
- **Done when:** the same target is shown from SOTP probes and from the public source on one panel.

### NETX-7 — "Local or Upstream?" Correlation
- Combine device health (core SOTP), probe results (NETX-3) and routing events (NETX-5) into one verdict per incident: local, upstream, or unclear.
- **Done when:** the verdict is correct for three scripted scenarios, one per category.

---

## Ground Rules for This Track
- Probe only targets you own or public services with low request rates. No load generation.
- Respect the terms of use and rate limits of public data sources.
