# Track: Support & Operations (ITSM)

> **Status:** Proposal · open for contributors
> **Part of:** [Future Work & Contributor Tracks](../FUTURE_WORK.md) · label `track: support`

**For people into:** helpdesk and service desk work, IT operations, ITIL-style processes.
**You will practice:** incident and problem management, ticket triage, writing runbooks and knowledge-base articles, running on-call, and communicating with users during an outage.

A monitoring platform only helps if someone acts on what it shows. This track designs and runs the **people side**: what happens between "an alert fired" and "the user is told it is fixed".

---

## Work Packages

| ID | Package | Difficulty | Needs from core |
|---|---|---|---|
| OPS-1 | Issue triage process & templates | 🟢 Starter | — |
| OPS-2 | Alert-to-ticket flow | 🟡 Medium | P5.4 (alerts) |
| OPS-3 | Runbook library | 🟢 Starter | P5.8 |
| OPS-4 | On-call rotation & escalation | 🟡 Medium | OPS-2 |
| OPS-5 | Status page | 🟡 Medium | P5.4 |
| OPS-6 | Postmortem practice | 🟢 Starter | P5.8 |
| OPS-7 | Knowledge base & FAQ | 🟢 Starter | — |
| OPS-8 | Service catalogue & service levels | 🟡 Medium | DATA-1 |

### OPS-1 — Issue Triage Process & Templates
- Issue templates for bug, question, feature request and incident, plus a triage routine: labels, priority, owner, and a first response target.
- **Done when:** every new issue in a month got its first response within the target, and the result is measured.

### OPS-2 — Alert-to-Ticket Flow
- Critical alerts open an incident ticket automatically (GitHub Issues as the ticketing system, or a lab instance of an open-source ITSM tool), linked to the device and dashboard. Duplicate alerts update the same ticket instead of opening new ones.
- **Done when:** a scripted outage produces exactly one ticket with the right device, severity and links, and the ticket closes when the alert resolves.

### OPS-3 — Runbook Library
- One runbook per alert: what it means, how to check it, how to fix it, and when to escalate. Each alert links to its runbook.
- **Done when:** a person who has never seen the alert resolves it in a game day using only the runbook.

### OPS-4 — On-Call Rotation & Escalation
- A weekly rotation for contributors who opt in, escalation rules, handover notes, and limits on how often someone can be woken up.
- **Done when:** a rotation runs for a month and a short report covers alert volume and response times.

### OPS-5 — Status Page
- A public status page for the demo deployment: components, current incidents, scheduled maintenance, and history. Updated from the incident ticket.
- **Done when:** an incident in a game day is posted, updated and resolved on the status page.

### OPS-6 — Postmortem Practice
- A blameless postmortem template and a process: timeline, impact, root cause, follow-up actions with owners.
- **Done when:** every game day and real incident has a postmortem, and its follow-ups are tracked as issues.

### OPS-7 — Knowledge Base & FAQ
- User-facing articles: how to add a device, why a device shows as down, how to read the dashboards. Recurring questions from OPS-1 become articles.
- **Done when:** the articles answer the five most common questions from triage.

### OPS-8 — Service Catalogue & Service Levels
- Define the services SOTP offers its "users" (monitoring, alerting, reports), with service levels for each, measured with the definitions from DATA-1.
- **Done when:** each service has a measured service level on a dashboard.

---

## Related Roadmap Steps
- [5.4 SLOs & burn-rate alerts](../SOTP_ROADMAP.md#step-54--slos--burn-rate-alerts-to-discord), [5.8 Runbooks & postmortem template](../SOTP_ROADMAP.md#step-58--operational-runbooks--postmortem-template).
