# Future Work & Contributor Tracks

> **Status:** Proposal · open for contributors
> **Tech lead / maintainer:** [@Kacper-Slezak](https://github.com/Kacper-Slezak)
> **Relation to the main roadmap:** [`SOTP_ROADMAP.md`](SOTP_ROADMAP.md) (P0–P8) is the **core track**. Everything below runs **in parallel**, never blocks the core, and can be switched off without breaking the platform.

SOTP is a network observability platform: it discovers devices, polls them (ICMP, SNMP, SSH), stores telemetry in TimescaleDB, and runs on Kubernetes with GitOps. That covers networking, software, data, operations and security, so there is room for people with very different interests, from network engineers to analysts to helpdesk staff.

The goal is to run SOTP the way a small product team runs a real platform, with tracks, owners, reviews, on-call, postmortems and release notes, while keeping it a **non-commercial, educational open-source project**.

---

## Table of Contents

1. [What You Get Out of It](#what-you-get-out-of-it)
2. [Tracks](#tracks)
3. [Cross-Track Flagship Scenarios](#cross-track-flagship-scenarios)
4. [How the Team Works](#how-the-team-works)
5. [How to Join](#how-to-join)
6. [Ground Rules](#ground-rules)

---

## What You Get Out of It

- **Real portfolio work:** your own merged PRs, a design doc or ADR with your name on it, and a demo you can show in an interview.
- **Code review** from people working on the same system, plus a reference from the tech lead for sustained contributions.
- **Team experience:** proposals, estimates, reviews and incident handling, the things that are hard to show from solo projects.
- **No money involved:** nobody is paid and nothing is sold. Contribute as much as you want, and step back whenever you need to.

---

## Tracks

Each track has its own page with work packages. Every package has an ID, a difficulty level, the core-roadmap phase it depends on, and a definition of done.

| Track | For people into… | Example packages | Page |
|---|---|---|---|
| 🌐 **Network Engineering & Automation** | Routing & switching, CCNA/JNCIA, NetDevOps, Python for networks | Containerlab labs, config backup & diff, gNMI streaming telemetry, topology map from LLDP | [network-automation.md](tracks/network-automation.md) |
| 🛰️ **Internet & Edge Observability** | CDN, DNS, BGP, how the Internet works end-to-end | Distributed synthetic probes, TLS/DNS checks, BGP hijack alerts, path-change detection | [internet-observability.md](tracks/internet-observability.md) |
| ⚙️ **Platform, DevOps & SRE** | Kubernetes, CI/CD, IaC, reliability | Preview environments per PR, backup & DR drills, game days, FinOps, release engineering | [platform-sre.md](tracks/platform-sre.md) |
| 🛡️ **Security** | AppSec, blue team, SOC, network security | API pentest, device CVE matching, runtime detection, rogue device discovery | [security.md](tracks/security.md) |
| 📊 **Data & Analytics** | SQL, BI, statistics, reporting | SLA & availability reports, capacity forecasts, data quality checks, public demo dataset | [data-analytics.md](tracks/data-analytics.md) |
| 🤖 **ML & MLOps** | Machine learning, model deployment | Anomaly detection on telemetry and logs, model registry, signed model artifacts, drift monitoring | [ml-mlops.md](tracks/ml-mlops.md) |
| 🎧 **Support & Operations (ITSM)** | Helpdesk, service desk, IT operations, ITIL | Alert-to-ticket flow, on-call rotation, runbooks, status page, triage process, knowledge base | [support-operations.md](tracks/support-operations.md) |
| 🧭 **Product, Design & Community** | Product management, UX/UI, technical writing, community | User personas, UX of the device pages, docs site, release notes, demo videos | [product-community.md](tracks/product-community.md) |

**Where to start if you are new:** every track has at least one 🟢 *Starter* package that needs only `make dev` and a laptop.

---

## Cross-Track Flagship Scenarios

These scenarios need several tracks working together. They are the best demos of the project as a whole and the best interview stories for the people who build them.

### 1. "A link goes down at 3 a.m."
A full incident lifecycle from fault to postmortem.

| Step | Track |
|---|---|
| A link flap is injected in a Containerlab topology | Network |
| SNMP and syslog pick it up, and the anomaly detector scores it | Network, ML |
| An alert fires, burns the error budget, and opens a ticket | Platform/SRE, Support |
| The on-call person follows a runbook and posts on the status page | Support |
| A postmortem is written, with an SLA impact report | Support, Data |

### 2. "Is it us or the Internet?"
Telling a local fault apart from an upstream one.

| Step | Track |
|---|---|
| Probes in several locations measure the same HTTP/DNS targets | Internet |
| One region degrades while the others stay healthy | Internet, Data |
| BGP data shows a route change at the same moment | Internet |
| The dashboard says "upstream issue", and the ticket is routed to the "provider" | Support, Product |

### 3. "Find the vulnerable box"
From inventory to a risk-ranked patch list.

| Step | Track |
|---|---|
| Devices are discovered and their OS versions collected over SSH | Network |
| OS versions are matched against public CVE data | Security |
| A weekly risk report ranks devices by exposure | Data |
| Change requests are opened and tracked to closure | Support |

### 4. "Ship it safely"
Every change takes the same path from a PR to a signed release.

| Step | Track |
|---|---|
| A PR gets its own preview environment with seeded data | Platform/SRE |
| Security scans and policy checks gate the merge | Security |
| A release is cut with notes and a short demo | Product |

---

## How the Team Works

### Roles

| Role | Responsibility |
|---|---|
| **Tech lead / maintainer** | Architecture, integration contracts, priorities across tracks, final review and merge, onboarding |
| **Track lead** | Keeps the track's page and backlog current, reviews PRs in the track, runs the track's demo |
| **Package owner** | Takes one work package from proposal to merged PR and demo |
| **Contributor** | Smaller issues, reviews, testing and docs in any track |
| **Security champion** | Reviews changes that touch auth, secrets or the threat model (one person, rotating) |

One person can hold several roles. Until a track has a lead, the tech lead covers it.

### Decisions
- **Small changes:** issue → PR → review.
- **Medium changes** (new endpoint, new table, new dashboard): a one-page proposal in the issue before coding.
- **Large changes** (new service, new runtime dependency, new data store, new external integration): an ADR in [`docs/adr/`](adr/README.md), approved by the tech lead.
- **Integration contracts** between tracks, like the ML [`anomaly_scores`](tracks/ml-mlops.md#integration-contract) table or the probe API, change only through an ADR.

### Cadence
- **Async first:** GitHub Issues and PRs are the source of truth, chat is for quick questions.
- **Every two weeks:** a 30-minute sync covering what was merged, what is blocked, and what comes next.
- **End of each work package:** a 5–10 minute demo, recorded so absent people can watch it.
- **Monthly:** a game day in which one flagship scenario is run end-to-end.

### Labels
- **Track:** `track: network`, `track: internet`, `track: platform`, `track: security`, `track: data`, `track: ml`, `track: support`, `track: product`.
- **Entry level:** `good first issue` for starters, `help wanted` for packages without an owner.
- **Existing labels** (`area: *`, `priority: *`) stay as they are and describe the code area and urgency.

---

## How to Join

1. **Read** the [README](../README.md), run `make dev` and `make seed`, and log in.
2. **Pick a track** and read its page. Comment on a package's tracking issue, or open one titled `[Track][Package-ID] Short name`.
3. **Write a short proposal** in the issue: what you will build, what it depends on, how you will show that it works, and roughly how long it will take.
4. **Build** on a branch named `<type>/<issue-id>-<short-name>` and open a PR to `main` with green CI. See the [Working Rules](SOTP_ROADMAP.md#working-rules--workflow).
5. **Demo** the result at the next sync, or in a short screen recording.

### Definition of Done (all tracks)
- Runs from a clean `make dev` with no manual steps.
- Has a test, a check, or a documented manual verification that someone else can repeat.
- Docs are updated: a README section, a runbook, or the track page.
- No secrets in the repo, and new dependencies are justified in the PR description.
- Numbers are reported with units, sample size and spread.

---

## Ground Rules

- **Non-commercial.** SOTP is not sold, offered as a paid service, or used for client work. Contributors keep authorship of their work under the repository [license](../LICENSE).
- **Lab only.** Tests, scans and fault injection target the lab (Docker, K3d, Containerlab). Never point them at networks or systems you do not own or have permission to test.
- **Public data only.** Use public datasets and public measurement services within their terms of use. No production data from employers or clients.
- **Credentials** live in Vault or `.env`, never in the repo or in issues.
- **Be kind in reviews.** Explain the why, suggest an alternative, and assume good intent.
