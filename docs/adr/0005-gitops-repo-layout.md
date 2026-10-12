# ADR-005: GitOps repository layout

- **Status:** Proposed
- **Date:** 2026-10-12
- **Deciders:** Kacper Ślęzak

## Context

From phase P4, SOTP is deployed by ArgoCD: the cluster state is whatever Git
says it is, and CI promotes a release by changing an image tag in Git rather
than by running `kubectl` or `helm upgrade`. That requires deciding where the
desired-state manifests live and how they are organised.

Options:

- **Separate config repository** (`sotp-gitops`): the usual recommendation for
  larger teams — clean audit trail of deployments, no CI loops, separate access
  control.
- **Same repository, dedicated directory:** everything stays in the monorepo
  ([ADR-001](0001-monorepo.md)); simpler, but CI's tag-bump commits land in the
  application repo.

## Decision

Keep the GitOps manifests **inside this repository**, in a dedicated tree, using
ArgoCD's **App-of-Apps** pattern:

```
infrastructure/
├── helm/sotp/                  # umbrella chart (how SOTP is packaged)
└── gitops/
    ├── bootstrap/
    │   └── root-app.yaml       # the single Application applied by hand
    ├── apps/                   # one ArgoCD Application per component
    │   ├── sotp.yaml           #   -> helm/sotp + environments/<env>/values.yaml
    │   ├── cloudnative-pg.yaml
    │   ├── vault.yaml
    │   ├── external-secrets.yaml
    │   ├── kyverno.yaml
    │   └── observability.yaml
    └── environments/
        └── local/              # K3d; an `aws/` sibling would mirror ADR-004
            └── values.yaml     # image tags, replicas, resources
```

- The only manual step is `kubectl apply -f bootstrap/root-app.yaml`; ArgoCD
  then reconciles everything under `apps/`.
- CI builds and pushes images, then commits the new tag to
  `environments/<env>/values.yaml`. Those commits touch only
  `infrastructure/gitops/**`, which the build pipeline ignores via path
  filters, so CI does not trigger itself.
- Secrets never appear in this tree; they are synced from Vault by External
  Secrets Operator.

## Consequences

- **+** One repository to clone and review; a feature PR can include its Helm
  value changes.
- **+** Adding an environment is a new directory under `environments/`, not a
  new repo.
- **+** Clear split: `helm/` is *how* SOTP is packaged, `gitops/` is *what*
  runs *where*.
- **−** Deployment history is interleaved with code history; auditing releases
  needs a path filter (`git log -- infrastructure/gitops`).
- **−** CI needs write access to the repository, and the path-filter guard
  against self-triggering must be kept correct.
- **−** If the team or number of environments grows, this should be revisited
  in favour of a separate config repository. The directory is self-contained,
  so it can be moved out with its history (`git filter-repo`).
