# Track: Network Engineering & Automation

> **Status:** Proposal · open for contributors
> **Part of:** [Future Work & Contributor Tracks](../FUTURE_WORK.md) · label `track: network`

**For people into:** routing and switching, CCNA/JNCIA-level networking, NetDevOps, Python for network automation.
**You will practice:** lab topologies as code, SNMP/SSH/gNMI collection, configuration management, network source of truth, and testing a network before changing it.

---

## Work Packages

| ID | Package | Difficulty | Needs from core |
|---|---|---|---|
| NET-1 | Reference lab topology in Containerlab | 🟢 Starter | — |
| NET-2 | Config backup, versioning & diff | 🟢 Starter | P7.4 (SSH executor) |
| NET-3 | Topology discovery & map (LLDP/CDP) | 🟡 Medium | P7.3 (SNMP) |
| NET-4 | Syslog & SNMP trap receiver | 🟡 Medium | P5.2 (Loki) |
| NET-5 | Streaming telemetry (gNMI) | 🟠 Hard | NET-1 |
| NET-6 | Config compliance checks | 🟡 Medium | NET-2 |
| NET-7 | Source of truth sync (NetBox) | 🟡 Medium | — |
| NET-8 | Pre-change validation | 🟠 Hard | NET-2, NET-6 |

### NET-1 — Reference Lab Topology
- A Containerlab topology with free images (e.g. Nokia SR Linux, FRRouting) and two or three sites: core, distribution, access.
- SNMP and SSH are enabled, and the devices are seeded into SOTP automatically. Extends roadmap step [8.6](../SOTP_ROADMAP.md#step-86--containerlab-realistic-network-topology).
- Fault scripts for link down, latency and packet loss. They feed the labels in [ML-0](ml-mlops.md#ml-0--dataset--data-card).
- **Done when:** `make lab-up` brings the lab up and every lab device shows as reachable in SOTP.

### NET-2 — Config Backup, Versioning & Diff
- A scheduled Celery task pulls the running configuration over SSH and stores it versioned (Git repo or database table).
- The UI shows the diff between versions and the time of the last change.
- **Done when:** a change made on a lab device appears as a diff in SOTP within one polling interval.

### NET-3 — Topology Discovery & Map
- Read LLDP/CDP neighbour tables over SNMP and build a graph of devices and links.
- Draw the graph in the frontend and colour links by status or utilisation.
- **Done when:** the NET-1 lab topology is drawn correctly without manual input.

### NET-4 — Syslog & SNMP Trap Receiver
- A receiver for syslog (UDP/TCP 514) and SNMP traps. It forwards events to Loki with labels `device_id`, `severity`, `facility`.
- Events are linked to inventory devices by source IP.
- **Done when:** an interface shutdown in the lab shows up as an event on that device's page.

### NET-5 — Streaming Telemetry (gNMI)
- Subscribe to interface counters over gNMI (e.g. gnmic) as an alternative to SNMP polling.
- Compare data freshness and collector load against SNMP on the same devices.
- **Done when:** a short report compares gNMI and SNMP latency and load, with numbers.

### NET-6 — Config Compliance Checks
- Rules as code: e.g. "SSH v2 only", "NTP configured", "no default SNMP community".
- Per-device compliance score and a list of violations in the UI.
- **Done when:** a deliberately misconfigured lab device fails the right rules.

### NET-7 — Source of Truth Sync (NetBox)
- Two-way or one-way sync of devices, sites and IP addresses between SOTP and a NetBox instance in the lab.
- **Done when:** a device added in NetBox appears in SOTP, and the sync direction is documented.

### NET-8 — Pre-Change Validation
- Before a config change: back up, run checks, and predict the impact (e.g. with Batfish on the configs from NET-2).
- After the change: compare reachability before and after.
- **Done when:** a change that would break reachability in the lab is caught before it is applied.

---

## Related Roadmap Steps
- [7.3 SNMP collector](../SOTP_ROADMAP.md#step-73--snmp-collector-vault-credentials--interface-stats), [7.4 SSH executor](../SOTP_ROADMAP.md#step-74--ssh-command-executor-netmiko), [8.2 TextFSM parser](../SOTP_ROADMAP.md#step-82--textfsm--ntc-templates-ssh-output-parser), [8.6 Containerlab](../SOTP_ROADMAP.md#step-86--containerlab-realistic-network-topology).
