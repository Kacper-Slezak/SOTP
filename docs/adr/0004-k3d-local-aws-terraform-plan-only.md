# ADR-004: K3d locally, AWS Terraform plan-only

- **Status:** Accepted
- **Date:** 2026-10-12
- **Deciders:** Kacper Ślęzak

## Context

SOTP should demonstrate a realistic path to production: Kubernetes, Helm,
GitOps, and cloud infrastructure as code. At the same time it is a personal
project with a budget of zero — a running EKS cluster with RDS and NAT gateways
costs well over $100/month, and leaving it running for demos is not viable.

For local Kubernetes the options were Minikube, kind, Docker Desktop's built-in
cluster, and K3d. For the cloud side the options were to deploy for real (and
pay), deploy briefly and destroy (cost and credential risk in CI), or write the
infrastructure without applying it.

## Decision

- **Local runtime: K3d** (K3s inside Docker). It starts in seconds, supports
  multi-node clusters, ships with Traefik and a local-path storage class, and
  can attach a local image registry. The same tool runs ephemeral clusters in
  GitHub Actions for Helm smoke tests. Scripted via `scripts/k3d-cluster.sh`
  and `make k3d-up` / `make k3d-down`.
- **Cloud: AWS Terraform, plan-only.** `infrastructure/terraform/` defines the
  production target — multi-AZ VPC, EKS, RDS PostgreSQL, ECR, IAM roles for
  service accounts, Secrets Manager — as real, reviewable modules. CI runs
  `terraform fmt -check`, `validate`, `tflint`, Checkov/Trivy and Infracost on
  every PR. **Nothing is ever applied.**

The same Helm chart is meant to deploy to both K3d and EKS; only values differ.

## Consequences

- **+** $0 cloud spend and no long-lived AWS credentials in CI.
- **+** The full deployment story (Helm, ArgoCD, operators, policies) is
  exercised for real on K3d, not just described.
- **+** Terraform is still validated, linted, security-scanned and costed, so
  it is more than a sketch.
- **−** The Terraform is never proven against a real AWS account; issues that
  only surface on `apply` (quotas, IAM edge cases, provider bugs) stay hidden.
- **−** K3d differs from EKS: Traefik instead of the AWS Load Balancer
  Controller, local-path instead of EBS, no IAM integration. These gaps must be
  documented (`docs/AWS_ARCHITECTURE.md`) rather than assumed away.
- **−** The local cluster needs a reasonably powerful machine once databases,
  Vault, ArgoCD and the observability stack all run on it.
