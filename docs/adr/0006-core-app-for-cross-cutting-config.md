# 0006. A `core` app for cross-cutting configuration and infrastructure

- Status: Accepted
- Date: 2026-06-19
- Deciders: Diogo

## Context

Phase 1 introduces backend foundations that are not owned by any single domain
context:

- **`system_settings`** — a DB-backed singleton holding scheduling configuration
  (`booking_slot_minutes`, `booking_horizon_days`, `minimum_notice_hours`,
  per-day/week/batch limits). It must live in the DB so staff/admin can tune it
  from the back office without a deploy (see `database.md`), yet it is consumed
  by both `appointments` (limits, notice, horizon) and `availability` (slot
  granularity, horizon).
- **Health probes** (`/healthz/`, `/readyz/`) and a **request-id middleware**
  used for structured logging — both purely infrastructural.

Django models must live in an app. The canonical app list (`backend.md`) has no
home for these, and the standing decisions forbid a `clinics` app
(architecture.md). Placing `system_settings` inside `appointments` or
`availability` would give one domain context ownership of config the other also
depends on, leaking configuration across a bounded-context boundary and forcing
cross-context reads that the DDD rules discourage.

## Decision

Add a single **infrastructure app named `core`** that is explicitly **not a
domain bounded context**. It hosts cross-cutting concerns:

- the `system_settings` singleton (model + `selectors`/`services`, seeded with
  recommended defaults via a `post_migrate` hook);
- health-check endpoints (liveness + DB readiness);
- the correlation-id middleware and its logging filter.

Domain apps read settings through `core`'s **selectors** (e.g.
`get_system_settings`), never by importing its models — the same
anti-corruption boundary that applies between domain apps. The canonical app
list in `backend.md` is updated to include `core`, flagged as infrastructure.

## Consequences

- Positive: a single, honest home for cross-cutting infrastructure; no domain
  context owns shared config; respects the "no direct cross-app model imports"
  rule; keeps `clinics` out of the codebase.
- Negative: the app count grows from 7 to 8, and `core` is a slight deviation
  from the original "domain apps only" framing — mitigated by clearly labelling
  it as infrastructure, not a bounded context.
- Neutral: `core` is the natural place for future cross-cutting pieces (shared
  abstract base models, common mixins) if they are introduced.

## Alternatives considered

- **Put `system_settings` in `appointments`.** Rejected: `availability` also
  depends on it, so booking would own config another context reads — a
  cross-context leak.
- **Put it in `availability`.** Rejected for the symmetric reason.
- **Django settings / environment variables.** Rejected: the values must be
  editable at runtime from the back office; settings/env require a deploy.
- **A `clinics` app.** Rejected: explicitly out of scope for v1; multi-clinic is
  a future SaaS concern (architecture.md).
