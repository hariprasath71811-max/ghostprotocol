# GhostProtocol — Cloud Threat Triage Cockpit

**Find the undead. Break the lure. Prove the fix.**

GhostProtocol is a Halloween-themed security cockpit for the credentials nobody owns: stale deploy keys, forgotten IAM users, personal access tokens in old repos, and phishing lures forwarded to a shared inbox. It ranks every finding by blast radius and walks one alert at a time through a human-approved response, writing an append-only proof trail as it goes.

- **Live demo:** https://hariprasath71811-max.github.io/ghostprotocol/
- **Demo video:** https://hariprasath71811-max.github.io/ghostprotocol/demo.webm
- **Pitch deck:** [`deck/GhostProtocol_HackToWeen_2026.pptx`](deck/GhostProtocol_HackToWeen_2026.pptx)

Built by **Team NullVoid** for NexHack 3.0 — Open Innovation track.

---

## The problem

A single leaked key can pivot from a test repository into production. Small teams and college labs have no 24/7 SOC, no asset inventory for credentials, and no way to prove that a suspected leak was actually handled. The result is a graveyard of undead credentials: still valid, still unowned, still one `git push` away from an incident.

Existing tools either dump hundreds of raw findings with no owner, or lock triage behind an enterprise SOC contract.

## The solution

A triage cockpit, not another scanner.

1. **Signal in** — secret-exposure findings, IAM posture drift, and phishing reports arrive as normalized alerts.
2. **Rank by blast radius** — severity tiers (`SPECTER`, `POLTERGEIST`, `APPARITION`) with risk score, resource, and owner.
3. **Human-approved response** — every alert moves through an explicit state machine:

   ```
   HAUNTING → TRIAGING → CONTAINED → SEALING → RESOLVED
   ```

4. **Proof out** — each action appends to an immutable audit feed, so the fix is defensible later.

No secret values are ever rendered — only metadata and the proof trail.

---

## What works today

The running MVP is a Next.js client that ships with four realistic alerts and a fully interactive flow:

- Blast-radius ranked alert queue with severity, risk score, resource, and exposure age
- Alert selection, filters (`All` / `Active` / `Contained`), and connector coverage
- **Triage secret** — `HAUNTING → TRIAGING → CONTAINED` with toast + audit entry
- **Seal exorcism** — `CONTAINED → SEALING → RESOLVED` with toast + audit entry
- **Sweep now** — simulated ingestion of new signals
- Live counters, filtered queue, and an append-only audit timeline
- Dark Halloween UI, 1440×900 and mobile responsive

The dashboard is intentionally front-end only: it uses deterministic mock data so judges can exercise the triage flow with zero setup, zero credentials, and zero cloud spend.

## Target AWS architecture

The production design is serverless and event-driven, aligned with the AWS Well-Architected pillars of reliability and cost:

| Layer | Service | Responsibility |
|---|---|---|
| Edge | API Gateway + Node Lambda | signed webhooks, auth, rate limiting |
| Schedule | EventBridge Scheduler | daily sweeps, tenant fan-out |
| Analysis | Python analyzers on Lambda | exposure, privilege, phishing scoring |
| Storage | DynamoDB | findings, owners, audit log (tenant-partitioned, on-demand) |
| Evidence | S3 + KMS | encrypted evidence packets |
| Identity | Cognito | auth + tenant RBAC |
| Notify | SNS / SES | digests and critical alerts |
| Explain (optional) | Amazon Bedrock | plain-English "why does this matter" — metadata only, never secret values |

Destructive actions always require human approval; the model never receives secret material.

## Tech stack

- **Next.js 16** (App Router, static export)
- **React 19**
- **TypeScript**
- **Tailwind CSS 4**
- **lucide-react** icons
- **GitHub Pages** for the static demo
- **AWS** (target runtime): Lambda, API Gateway, EventBridge, DynamoDB, S3, KMS, Cognito, Bedrock

## Run locally

```bash
cd dashboard
npm install
npm run dev
```

Open <http://localhost:3000>.

Production build (static):

```bash
npm run build   # emits dashboard/out
```

## Repository layout

```
ghostprotocol/
├─ dashboard/            # Next.js app (source of the live demo)
│  ├─ app/
│  ├─ components/GhostProtocolDashboard.tsx
│  └─ public/demo.webm   # recorded walkthrough
├─ deck/                 # 8-slide pitch deck (PPTX + PDF) and its python-pptx generator
├─ MVP_SPEC.md           # technical prototype specification
└─ README.md
```

## Design principles

- **Human in the loop** — no automated destructive action, ever.
- **Proof over promises** — every state change is auditable.
- **Metadata only** — secret values are never stored or displayed.
- **Boring where it counts** — managed AWS services over custom infrastructure.

## Team NullVoid

Hariprasath

## License

MIT — see [LICENSE](LICENSE).
