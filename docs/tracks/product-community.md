# Track: Product, Design & Community

> **Status:** Proposal · open for contributors
> **Part of:** [Future Work & Contributor Tracks](../FUTURE_WORK.md) · label `track: product`

**For people into:** product management, UX/UI design, technical writing, community building.
**You will practice:** user research, prioritisation, design for operational tools, documentation as a product, and making a project understandable to newcomers.

---

## Work Packages

| ID | Package | Difficulty | Needs from core |
|---|---|---|---|
| PROD-1 | Personas & key user journeys | 🟢 Starter | — |
| PROD-2 | Backlog grooming across tracks | 🟡 Medium | — |
| PROD-3 | UX review of core screens | 🟢 Starter | P1.4 |
| PROD-4 | Design system for the frontend | 🟡 Medium | P1 |
| PROD-5 | Documentation site | 🟡 Medium | — |
| PROD-6 | Release notes & demo videos | 🟢 Starter | PLAT-5 |
| PROD-7 | Contributor onboarding & community | 🟢 Starter | — |

### PROD-1 — Personas & Key User Journeys
- Two or three personas, e.g. a network admin at a small company, a NOC operator on a night shift, a manager who reads reports.
- The top journeys for each persona, such as "add 20 devices" or "find out why the site is slow".
- **Done when:** user stories in [`USER_STORIES.md`](../USER_STORIES.md) are mapped to the personas and journeys.

### PROD-2 — Backlog Grooming Across Tracks
- Keep the track backlogs consistent: clear acceptance criteria, sizes, dependencies, and a visible "next up" per track.
- **Done when:** every open package has acceptance criteria and a size, and blocked items say what they wait for.

### PROD-3 — UX Review of Core Screens
- Heuristic review and quick usability tests (three to five people) of login, the device list, adding a device and device details.
- **Done when:** findings are ranked by severity, and the top three are filed as issues with mockups.

### PROD-4 — Design System for the Frontend
- Shared components, colours for statuses (up, degraded, down, unknown) that are readable for colour-blind users, dark mode, and empty and error states.
- **Done when:** core screens use the shared components, and status colours pass a contrast check.

### PROD-5 — Documentation Site
- Build the `docs/` folder into a site (e.g. MkDocs) with getting started, user guide, operator guide, contributor guide and ADRs.
- **Done when:** the site is published from CI on every merge to `main`.

### PROD-6 — Release Notes & Demo Videos
- Release notes written for users, not just a changelog, plus a two-minute demo video per release.
- **Done when:** every release since the first tagged one has notes and a video.

### PROD-7 — Contributor Onboarding & Community
- Contributor guide, code of conduct, a "start here" issue per track, and a monthly update posted to the community channel.
- **Done when:** a new contributor merges a first PR within a week of joining, and the time is measured for the next few newcomers.
