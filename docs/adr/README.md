# Architecture Decision Records

Short records of the significant architectural decisions in SOTP: the context,
the decision, and its consequences. New ADRs start from
[`0000-template.md`](0000-template.md) and take the next free number. An accepted
ADR is never edited to change its decision — write a new one that supersedes it.

| ADR | Title | Status |
|---|---|---|
| [ADR-001](0001-monorepo.md) | Monorepo with an `apps/` layout | Accepted |
| [ADR-002](0002-postgres-timescaledb-split.md) | Separate PostgreSQL and TimescaleDB instances | Accepted |
| [ADR-003](0003-celery-for-collectors.md) | Celery + Redis for network collectors | Accepted |
| [ADR-004](0004-k3d-local-aws-terraform-plan-only.md) | K3d locally, AWS Terraform plan-only | Accepted |
| [ADR-005](0005-gitops-repo-layout.md) | GitOps repository layout | Proposed |
