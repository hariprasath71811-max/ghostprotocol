# GhostProtocol — MVP prototype specification

**Project:** GhostProtocol — Zombie Credential & Phishing Exorcist  
**Event:** Hack-to-Ween 2026 · AWS Student Builder Group, IIT Jodhpur  
**Track:** Cloud Security & Threat Triage  
**Primary users:** developers, college labs, small DevOps teams

---

## 1. Product thesis

Small teams do not need another scanner. They need a safe way to answer three questions:

1. **What is exposed?**
2. **How bad is it if an attacker uses it?**
3. **What is the safest next action — and how do we prove it worked?**

GhostProtocol’s MVP proves the complete loop: **discover → explain → triage → remediate → verify → audit**.

The demo is intentionally narrow and deterministic. It is designed to run without a live AWS account, while every interaction maps cleanly to a production API.

---

## 2. MVP scope

### In scope

- GitHub secret exposure (mock connector + webhook contract)
- AWS IAM / Secrets Manager zombie-key signals (mock connector + contract)
- Phishing report scoring (email/URL heuristics, mock data)
- One prioritized alert queue
- Explainable risk score and blast radius
- A 4-step remediation playbook
- Status state machine with visible real-time transitions
- Append-only audit feed
- “Secret values never rendered” trust boundary
- Demo mode and reset path

### Explicitly out of scope

- Full CASB / CSPM coverage
- Automatic rotation in production without approval
- Custom SIEM / log lake
- Billing, SSO, and multi-tenant admin console
- Deep malware analysis or sandbox detonation
- Live AWS write access in the public demo

---

## 3. Screen map (single-page demo)

The dashboard is one responsive page with five regions:

1. **Sidebar** — workspace navigation, demo-tenant status, human-approval reminder.
2. **Header** — workspace name, live demo badge, sweep control.
3. **Stat strip** — active haunts, contained, peak risk, secrets shown.
4. **Main grid**
   - Alert queue with filters and selection
   - Selected-signal detail with risk, blast radius, playbook, evidence, action
5. **Bottom strip** — audit séance and connector coverage.
6. **Toast layer** — live status feedback, `aria-live="polite"`.

---

## 4. Core data model

```ts
type Severity = "specter" | "poltergeist" | "apparition";
type Status = "haunting" | "triaging" | "contained" | "sealing" | "resolved";

type Alert = {
  id: string;                 // "GP-1042"
  title: string;
  kind: "Exposed secret" | "Phishing lure" | "Zombie credential" | "Stale token";
  source: "GitHub" | "Email report" | "AWS IAM" | string;
  resource: string;           // masked reference, never a secret value
  severity: Severity;
  status: Status;
  risk: number;               // 0-100
  owner: string;
  lastSeen: string;           // demo-friendly relative time
  detail: string;
  blastRadius: string[];
  evidence: string[];         // signed evidence pointers, no secrets
  playbook: string[];
};
```

### Risk score (MVP heuristic)

```text
risk = clamp(
  exposure * 0.35 +
  privilege * 0.30 +
  reach * 0.20 +
  age * 0.15,
  0, 100
)
```

- **Exposure:** public repo, broad audience, active phishing page.
- **Privilege:** admin policy, write scope, production role.
- **Reach:** number of repos, users, buckets, or services affected.
- **Age:** days since creation / last rotation / last use.

The UI always shows a short “why” rather than only a number.

---

## 5. Status state machine

```text
HAUNTING
   │  Triage secret
   ▼
TRIAGING
   │  scope + check usage + rotation plan
   ▼
CONTAINED
   │  Seal exorcism
   ▼
SEALING
   │  signed evidence packet
   ▼
RESOLVED
```

Rules:

- `TRIAGING` and `SEALING` are transient and show a spinner.
- The playbook progress is derived from status, not separately mutated.
- Every transition appends an audit event.
- Destructive remediation requires a human click; no background auto-rotation.
- A resolved alert remains visible under the “Contained” filter for evidence.

---

## 6. API contract (production mapping)

### Read

```http
GET /api/alerts?tenant=demo
GET /api/alerts/:id
GET /api/audit?tenant=demo&limit=50
GET /api/connectors
```

### Actions

```http
POST /api/alerts/:id/triage
POST /api/alerts/:id/remediate
POST /api/alerts/:id/seal
POST /api/sweeps
```

### Webhooks

```http
POST /api/webhooks/github     # signed GitHub App webhook
POST /api/webhooks/aws        # EventBridge / Security Hub finding
POST /api/webhooks/phishing   # SES inbound / Slack report
```

### Example action response

```json
{
  "alertId": "GP-1042",
  "status": "contained",
  "auditEventId": "evt_01J...",
  "evidenceUri": "s3://ghostprotocol-evidence/demo/GP-1042.json",
  "secretValueReturned": false
}
```

The mock UI’s `setTimeout` transitions map to these API calls. In production, the UI should use optimistic updates plus server-confirmed status.

---

## 7. AWS implementation map

| Layer | MVP | Production path |
|---|---|---|
| Frontend | Next.js app, local mock data | Next.js on AWS Amplify Hosting |
| Auth | Demo mode | Amazon Cognito, tenant claims, RBAC |
| API | Local component state | API Gateway + Node/Python Lambda |
| Scheduling | “Sweep now” button | EventBridge Scheduler, per-tenant fan-out |
| Queue/buffer | None | SQS + DLQ for bursty scans |
| Findings | In-memory mock | DynamoDB, tenant-partitioned keys |
| Evidence | Mock strings | S3 + KMS, signed manifests |
| Secrets | Never rendered | Secrets Manager + IAM, metadata only |
| Alerts | Toast + audit feed | SNS / SES / Slack webhook |
| Explanation | Template copy | Optional Amazon Bedrock, metadata-only prompts |
| Observability | Browser console | CloudWatch + X-Ray + structured audit logs |

### Suggested DynamoDB keys

```text
PK = TENANT#<tenantId>
SK = ALERT#<alertId>
GSI1PK = TENANT#<tenantId>#STATUS#<status>
GSI1SK = RISK#<zero-padded-risk>
```

This supports the main queue query (by tenant/status, sorted by risk) without a scan.

---

## 8. Security invariants

1. **No secret values in the browser.** The API returns masked identifiers and evidence pointers only.
2. **No secret values in logs or LLM prompts.** Analyzers receive metadata, hashes, and redacted context.
3. **Least privilege.** Each connector gets a scoped role; remediation uses a separate, approval-gated role.
4. **Human approval for destructive actions.** Rotation/revocation is explicit and auditable.
5. **Immutable evidence.** Every state change writes an append-only audit event with actor, timestamp, and result.
6. **Tenant isolation.** Every record and query is scoped by `tenantId`.
7. **Fail closed.** If verification fails, the alert stays `CONTAINED`, never `RESOLVED`.
8. **Accessibility.** Color is never the only signal; icon + label + text; reduced-motion support.

---

## 9. Demo acceptance criteria

The MVP is demo-ready when all of these are true:

- [ ] Dashboard loads with 4 active alerts and no console errors.
- [ ] Selecting an alert updates the detail panel.
- [ ] “Triage secret” moves `HAUNTING → TRIAGING → CONTAINED`.
- [ ] The playbook progress advances and the status chip changes.
- [ ] A toast appears and the audit feed gains an event.
- [ ] “Seal exorcism” moves `CONTAINED → SEALING → RESOLVED`.
- [ ] Stats update (`Active haunts` decreases, `Contained` increases).
- [ ] “Sweep now” resets the sync timer and appends an audit event.
- [ ] No secret value is rendered anywhere in the UI.
- [ ] Layout works at 1440 px and at a narrow mobile width.

---

## 10. 60-second judge demo

1. Open `http://localhost:3000`.
2. Point to `prod-deploy-key`, risk `96`, and the blast radius.
3. Say: “The UI never receives the key — only metadata and evidence pointers.”
4. Click **Triage secret**. Show `TRIAGING`, then `CONTAINED`.
5. Show the toast and the new audit event.
6. Click **Seal exorcism**. Show `SEALING`, then `RESOLVED`.
7. Close: “One account. Ten minutes. We find the first zombie and prove the fix.”

---

## 11. Build plan (hackathon weekend)

| Workstream | Owner | Output |
|---|---|---|
| Frontend cockpit | Frontend | Single-page dashboard, mock data, state machine |
| Detection contracts | Backend | Lambda handler stubs, risk scoring, webhook schemas |
| Demo + evidence | Product | Seed data, audit events, 60-second script |
| Deck + pitch | All | 8 slides, architecture, rehearsal |

### Must-have cut line

If time runs short, keep: alert queue, detail panel, triage transition, audit feed, and the “no secret values” message. Cut: real connectors, Bedrock, PDF export, and auth.

---

## 12. Next steps after the hackathon

1. Convert mock state actions to real API calls.
2. Add a GitHub App with least-privilege metadata scopes.
3. Add an AWS onboarding CloudFormation stack with a read-only role.
4. Persist findings and audit events in DynamoDB.
5. Add signed S3 evidence packets and a PDF export.
6. Run a 5-lab design-partner pilot and measure time-to-triage.
