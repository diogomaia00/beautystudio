# 0005. Single Next.js app with (client) and (bo) route groups

- Status: Accepted
- Date: 2026-06-17
- Deciders: Diogo

## Context

The client booking app and the staff/admin back office share a design system,
types, and API client, and both sit behind one NGINX domain with session auth
(ADR 0002). Earlier docs called for "independently deployable" frontends, but
that goal was never pinned to a concrete structure.

## Decision

Build **one Next.js app** with two App-Router **route groups**: `(client)` for
the booking app and `(bo)` for the back office. NGINX routes `/` to the client
surface and `/bo` to the back office. Both deploy together as a single frontend
service in v1.

## Consequences

- Positive: one codebase, shared design system/types/API client with no extra
  workspace packaging; simplest build and deploy; consistent auth/session
  handling across both surfaces.
- Negative: the two surfaces are **not** independently deployable in v1 — a BO
  change redeploys the whole frontend.
- Mitigation/follow-up: if independent deploys become necessary, split into
  **Next.js multi-zones** (or two apps sharing a package) behind the same NGINX
  domain — a reversible change captured by a future ADR.

## Alternatives considered

- **Two separate Next.js apps** (`frontend/client-app/`, `frontend/bo/`).
  Rejected for v1: enables independent deploys but adds a shared-package
  workspace and build duplication that the current scale doesn't justify.
