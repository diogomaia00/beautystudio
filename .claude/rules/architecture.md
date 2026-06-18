# ARCHITECTURE & DECISIONS

## Architecture at a glance

```
browser ──> NGINX ──> frontend (Next.js: client app + back office)
                 └──> backend  (Django REST API)
backend  ──> PostgreSQL
backend  ──> Procrastinate worker ──> PostgreSQL (task queue + periodic jobs)
backend  ──> integrations (Google Calendar, email, SMS/Twilio)
```

- **Two frontends, one API surface.** The client app (booking) and the back office (staff/admin) live in **one Next.js app** as `(client)` and `(bo)` route groups, served under one domain via NGINX, and talk to the same Django backend (see ADR 0005). 
  The backend exposes versioned REST APIs: the client app under `/v1/...`
  and the back office under `/bo/v1/...`.
- **Domain-driven backend.** Business logic lives in a service layer, not in views (see `ddd.md`).
- **Feature-based frontend.** Code is grouped by feature, not by file type (see `frontend.md`).
- **Async work via Procrastinate.** Notifications, reminders, calendar sync, and monthly reports run as background/scheduled jobs on a Postgres-native queue (see `background-jobs.md`).

## Standing architectural decisions

These are settled for v1. Changing any of them requires a new ADR.

- **Single clinic, no `clinics` app.** Clinic-level config is settings, not a domain entity. Multi-clinic is a future SaaS concern.
- **No app cache layer and no Redis.** Low volume; background jobs run on a Postgres-native task queue (Procrastinate) — see ADR 0003.
- **Single session auth, one domain.** Both the client app and BO use Django session auth (cookie-based) under one domain via nginx; sessions stored in Postgres; instant revocation supports blacklist/logout. Credentials are verified via SMS OTP for all roles (see `auth.md`, ADR 0002 & 0004).
- **Concurrency safety.** Booking creation uses DB transactions and must be idempotent to handle concurrent clients competing for the same time.
- **Deployment target.** Single Hetzner VPS via Docker Compose (see `infrastructure.md`).
- **Payments deferred.** Online payment (MBWay) is roadmap, not v1.

## Architecture Decision Records (ADR) process

Architecture Decision Records capture *why* a non-trivial choice was made.

- Location: `docs/adr/` (per package or at repo root for cross-cutting ones).
- Filename: `NNNN-short-title.md` (e.g. `0001-jwt-for-back-office.md`), zero-padded and sequential.
- Status lifecycle: `Proposed → Accepted → (Superseded by NNNN | Deprecated)`.
- Never edit an Accepted ADR's decision — supersede it with a new one.

### When to write an ADR

Write one when a decision is costly to reverse or affects multiple parts of the system: 
  - choosing a technology
  - a data model with wide impact
  - an auth strategy
  - a cross-service contract
  - a deployment topology. 
Skip ADRs for routine, easily reversible choices.

### Template

```
# NNNN. <Title>

- Status: Proposed | Accepted | Superseded by NNNN | Deprecated
- Date: YYYY-MM-DD
- Deciders: <people>

## Context
What problem/forces are at play? What constraints apply?

## Decision
The choice we are making, stated plainly.

## Consequences
Positive, negative, and neutral results. Follow-ups and risks.

## Alternatives considered
Other options and why they were rejected.
```

> For help drafting or evaluating an ADR, the `engineering:architecture` and `engineering:system-design` skills are available.
