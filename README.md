# VA Demo CI/CD Pipeline Scaffold

This repository contains an initial **GitHub Actions CI/CD pipeline scaffold** based on the proposed enterprise DevSecOps workflow tailored for a VA-focused application delivery model.

It serves as a **starting structure** for the team to build upon while application-specific details are still being defined.

---

## Purpose

This scaffold was created to advance the initial workflow despite lacking access to:

- The current application codebase
- Framework/runtime details
- Real test suites
- Build tooling
- Deployment targets
- Azure environment configuration
- Security tooling configuration
- Monitoring instrumentation

The goal is to establish a pipeline foundation that reflects the intended **delivery flow, security controls, testing stages, approval gates, deployment progression, rollback paths, and observability checkpoints**.

---

## Current Positioning

1. **Enterprise Application Factory** (Positioned for future implementation)  
   *(show speed)*

2. **Automated Compliance & Testing Pipeline** (Most Fully Represented)  
   *(show risk reduction)*

3. **Copilot Release Readiness Assistant** (Positioned for future implementation)  
   *(show innovation)*

---

## Pipeline Flow Modeled

The scaffold currently models the following general flow:

1. Pull Request Validation
2. Unit Testing
3. Security Scanning
   - CodeQL
   - Dependency security scan
   - Secret detection
   - Infrastructure as Code (IaC) security scan
4. Build and Artifact/Supply Chain Preparation
   - Build
   - Package
   - SBOM generation
   - Artifact upload
5. Deploy to DEV
6. Integration / API / DAST / Performance Validation
7. Deploy to TEST/UAT
8. Regression Testing
9. Deploy to PreProd and Production
10. Smoke Testing and Automated Rollback
11. Monitoring / Observability Validation

---

## What Is Included

This scaffold currently includes:

- GitHub Actions workflow structure
- Stage ordering and dependencies
- Pull request validation stage
- Unit testing stage placeholder
- Code coverage placeholder
- Security scanning structure with:
  - CodeQL
  - Dependency scan placeholder
  - Secret scan placeholder
  - IaC scan placeholder
- Build stage with:
  - Application build placeholder
  - Package placeholder
  - SBOM generation placeholder
  - Artifact upload structure
- Environment progression across:
  - DEV
  - UAT
  - PreProd
  - Production
- Approval gate structure for higher environments
- Azure login/OIDC structure for deployment stages
- Integration and API validation placeholders
- DAST placeholder
- Performance testing placeholder
- Regression test placeholder
- Smoke test placeholder
- Automated rollback placeholder
- Incident creation placeholder
- Operations notification placeholder
- Monitoring and observability validation placeholders
- Deployment metrics publishing placeholder

---

## What Is Not Included Yet

As this is still a scaffold, the following are **not implemented yet**:

- Real application code
- Real unit/integration/regression/smoke tests
- Real build scripts
- Dockerfile or package-specific build logic
- Real dependency scanning tooling
- Real secret scanning tooling
- Real IaC scanning tooling
- Real SBOM generation tooling
- Real artifact signing
- Real Azure deployment scripts
- Actual Azure credentials / federated identity configuration
- Real DAST tooling
- Real performance/load scripts
- Real rollback implementation
- Real incident/ticketing integration
- Real Slack/Teams/PagerDuty notifications
- Real Application Insights instrumentation and metric publishing
- Copilot-based release readiness logic
- Application Factory provisioning/templates

---

## GitHub Copilot Change Chat

The GitHub Pages console now provides a chat interface for repository change requests. This page is intentionally static and does not hold GitHub credentials. Connect it to a separately hosted GitHub App/API service by providing `window.VA_CHAT_API_URL`; the service contract and security requirements are documented in `docs/github-copilot-chat-api.md`.

All accepted changes must be delivered through pull requests. The backend must authenticate users, authorize repository access, use the Copilot integration server-side, and never write directly to `main`.

### Front-End Chat Application Features

The front end of this web application now includes a fully working GitHub Copilot chat interface supporting two distinct modes:

- **Edit Mode:** Allows users to request and receive code modifications, enabling interactive repository change requests directly through the chat.

- **Analysis Mode:** Enables users to ask questions and receive insights about the repository, facilitating understanding and review without making changes.

Users can seamlessly switch between these modes within the chat interface, enhancing productivity and collaboration.

---

## Repository Structure

```text
.
├── .github
│   └── workflows
│       └── ci-cd-pipeline.yml
├── scripts
│   ├── rollback.sh
│   └── smoke-test.sh
└── README.md
```

---

## Release Governance

This repository and its associated CI/CD pipeline scaffold adhere to a release governance framework designed to ensure quality, security, and compliance throughout the software delivery lifecycle. Key aspects include:

- **Change Control:** All changes must be introduced via pull requests with appropriate peer review and automated validation.
- **Approval Gates:** Deployment to higher environments (UAT, PreProd, Production) requires explicit approval steps to enforce compliance and risk management.
- **Security Compliance:** Integrated security scanning stages (CodeQL, dependency scanning, secret detection, IaC scanning) enforce security policies before promotion.
- **Auditability:** Pipeline execution logs, artifact provenance, and deployment records are maintained to support traceability and auditing.
- **Rollback Capability:** Automated rollback mechanisms are scaffolded to enable quick recovery from failed deployments or incidents.
- **Monitoring and Observability:** Post-deployment validation and monitoring stages ensure operational readiness and support incident response.

This governance framework is intended to evolve alongside the pipeline and application, incorporating additional controls and tooling as they become available.