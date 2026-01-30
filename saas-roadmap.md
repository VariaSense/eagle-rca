# SaaS Roadmap (Incident Triage + Connector-First)

This roadmap prioritizes:
1) Features, 2) Security/Compliance, 3) Reliability, 4) Product UX, 5) Revenue.

Execution order:
- Phase 1 and 2 in parallel (when mutually ready).
- Then Phase 3 and 4 (when mutually ready).
- Then re-evaluate gaps and iterate.

Success = shipable increments with clear exit criteria and re-assessment after Phase 4.

---

## Phase 1: Connector Maturity + Evidence Graph (Feature Core)

Goal: Replace SSH-only assumptions with a robust customer-side connector fleet and build the
evidence model that links incidents, infra, code, logs, and docs.

Deliverables:
- Connector lifecycle: install, enroll, heartbeat, versioning, upgrade, decommission.
- Secure transport for connectors with org-scoped auth and rotation.
- Evidence graph model: canonical "evidence" entity with provenance and links.
- Normalized ingestion pipeline for logs/metrics/incidents.
- Correlation service that ties evidence to incidents/cases.

Key work items:
- Define connector protocol versioning and upgrade strategy.
- Add connector health + fleet dashboard.
- Define evidence schema + indexing strategy.
- Add idempotent ingestion and deduplication.
- Ingest initial sources: incident tracker, logs, K8s/Docker metadata, GitHub metadata.

Exit criteria:
- New connector can be installed without SSH access.
- Evidence objects are created and linked for a real incident flow.
- End-to-end case shows linked infra + logs + incidents in one timeline.

Risks:
- Overly broad schema; mitigate by starting with a minimal evidence core.

---

## Phase 2: Workflow Automation + GitHub/CI Integration (Feature Core)

Goal: Provide an automated investigation pipeline and controlled remediation path.

Deliverables:
- Case workflow state machine (triage -> investigation -> remediation -> verification -> postmortem).
- Playbook engine with safe, auditable steps.
- GitHub integration: PR creation, branch strategy, code context retrieval.
- CI/test orchestration with results linked to case.
- Human-in-the-loop approvals for high-risk actions.

Key work items:
- Define case workflow and transition rules.
- Build playbook runner with policy checks and audit hooks.
- Add GitHub App + webhook ingestion for code context.
- Add CI result ingestion and gating logic.
- Add permission model for remediation actions.

Exit criteria:
- From incident to proposed fix workflow in a single case.
- A test run can be triggered and results attached to case.
- Manual approval gates exist for code changes.

Risks:
- Scope creep in automation; mitigate by MVP playbooks.

---

## Phase 3: Security/Compliance (SaaS Readiness)

Goal: Close enterprise security gaps and enable auditability.

Deliverables:
- Audit logging for all sensitive actions (immutable, queryable).
- MFA for users; SSO (SAML/OIDC) for enterprise.
- SCIM or team provisioning (optional depending on target users).
- Secrets management integration and rotation.
- Data retention/export/delete policies per tenant.

Key work items:
- Implement audit log model + write hooks at service layer.
- Add MFA flow + recovery.
- Add SSO (SAML/OIDC) and tenant config.
- Implement key rotation and secret storage best practices.
- Add data governance endpoints and admin controls.

Exit criteria:
- Audit log coverage for auth, data access, and admin actions.
- MFA enabled in production; SSO available for enterprise.
- Tenant retention policy enforced.

Risks:
- Complexity in identity integrations; mitigate by OIDC-first.

---

## Phase 4: Reliability + Product UX (SaaS Polish)

Goal: Production-grade operations and a focused UX for case resolution.

Deliverables:
- Backups/DR plan with automated verification.
- SLOs + alerting; load/perf test automation.
- Connector fleet monitoring and auto-recovery.
- Onboarding + guided setup flow.
- Evidence timeline UI with provenance and confidence signals.

Key work items:
- Add backup jobs and restore drills.
- Add SLO monitoring dashboards and alerting.
- Add connector canarying and rollback.
- Build onboarding wizard and system connection UX.
- Build case timeline UI with filters and evidence detail panels.

Exit criteria:
- DR tested with a successful restore.
- Onboarding allows a new tenant to connect at least one system.
- Case timeline is usable and reduces time-to-understand.

Risks:
- UX work can expand; mitigate by targeted flows and user tests.

---

## Re-evaluation (After Phase 4)

At this point, re-run a gap analysis and reprioritize. Expected next areas:
- Revenue (billing, metering, plan enforcement).
- Marketplace or integrations expansion.
- Advanced ML-assisted RCA.
- Compliance programs (SOC2/ISO) and evidence collection.

Re-evaluation output:
- Updated gap list with severity and effort.
- Revised roadmap for Phases 5+.

