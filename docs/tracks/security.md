# Track: Security

> **Status:** Proposal · open for contributors
> **Part of:** [Future Work & Contributor Tracks](../FUTURE_WORK.md) · label `track: security`

**For people into:** application security, blue team and SOC work, network security, pentesting.
**You will practice:** threat modelling, testing an API like an attacker, detection engineering, and vulnerability management on real inventory data.

SOTP is a good target for security work: it stores credentials for network devices, so a compromise of SOTP means a compromise of the network. The core roadmap (P2, P4.4) covers the supply chain and cluster policy. This track covers the rest.

---

## Work Packages

| ID | Package | Difficulty | Needs from core |
|---|---|---|---|
| SEC-1 | Security policy & disclosure process | 🟢 Starter | — |
| SEC-2 | API security test against OWASP API Top 10 | 🟡 Medium | P1 |
| SEC-3 | Device CVE matching | 🟡 Medium | — |
| SEC-4 | Rogue & unknown device detection | 🟡 Medium | NET-3 |
| SEC-5 | Runtime threat detection in the cluster | 🟠 Hard | P3 |
| SEC-6 | Audit log analytics & detections | 🟡 Medium | P7.7 (audit log) |
| SEC-7 | Device hardening benchmarks | 🟡 Medium | NET-6 |
| SEC-8 | Credential rotation for devices | 🟠 Hard | P4.1, P7.3 |

### SEC-1 — Security Policy & Disclosure Process
- `SECURITY.md` with supported versions and how to report a vulnerability, plus private vulnerability reporting enabled on GitHub.
- **Done when:** a test report goes through the process end-to-end.

### SEC-2 — API Security Test
- Test the API against the OWASP API Security Top 10: broken object-level authorization, broken authentication, excessive data exposure, missing rate limits.
- Turn every finding into a failing test first, then a fix.
- **Done when:** a report lists findings with severity and every fixed finding has a regression test.

### SEC-3 — Device CVE Matching
- Devices already store `vendor`, `model` and `os_version`. Match them against public vulnerability data (NVD, vendor advisories) using CPE identifiers.
- A per-device risk view: open CVEs, CVSS scores, and whether a known exploit exists (e.g. CISA KEV).
- **Done when:** a lab device with an old OS version shows the expected CVEs.

### SEC-4 — Rogue & Unknown Device Detection
- Compare what the network sees (ARP/LLDP tables, scans of lab subnets) with the inventory, and flag devices that are not registered.
- **Done when:** an unregistered device added to the lab is flagged within one discovery cycle.

### SEC-5 — Runtime Threat Detection
- Falco (or similar) rules for SOTP workloads: shell spawned in a container, unexpected outbound connection from a collector, read of a secrets mount.
- Alerts go to the same channel as other alerts.
- **Done when:** each rule is triggered by a scripted test and produces exactly one alert.

### SEC-6 — Audit Log Analytics & Detections
- Detections on the audit log: login brute force, privilege changes, mass device deletion, logins at unusual times.
- **Done when:** each detection has a test event, a severity and a runbook entry.

### SEC-7 — Device Hardening Benchmarks
- Check device configurations against hardening guidelines (CIS-style): management access, SNMPv3, logging, NTP, unused services.
- **Done when:** a hardening score per device is shown next to the compliance score from NET-6.

### SEC-8 — Credential Rotation for Devices
- Rotate SSH passwords and SNMP credentials on lab devices through Vault and update them in SOTP without downtime.
- **Done when:** a scheduled rotation completes and polling continues without errors.

---

## Ground Rules for This Track
- Test only the lab and your own SOTP deployment. Never scan or attack systems you do not own.
- Report vulnerabilities in SOTP privately (SEC-1), not in public issues.

## Related Roadmap Steps
- [P2 DevSecOps Pipeline](../SOTP_ROADMAP.md#phase-p2--devsecops-pipeline), [2.13 Threat model](../SOTP_ROADMAP.md#step-213--threat-model-stride), [4.4 Kyverno](../SOTP_ROADMAP.md#step-44--kyverno-policy-enforcement), [7.7 Audit log](../SOTP_ROADMAP.md#step-77--audit-log-middleware), [8.3 JWT rotation](../SOTP_ROADMAP.md#step-83--advanced-jwt-management-revocation--rotation).
