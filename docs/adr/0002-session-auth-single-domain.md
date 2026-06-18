# 0002. Single session-based authentication under one domain

- Status: Accepted
- Date: 2026-06-17
- Deciders: Diogo

## Context

The client app and the back office are separate Next.js frontends talking to one
DRF API. An earlier draft used JWT for the BO and session auth for the client
app. Maintaining two mechanisms adds complexity (two code paths, CSRF for
sessions plus token refresh/rotation for JWT) with little benefit at this scale.

The deployment serves all three (client app, BO, API) behind a single nginx
reverse proxy under **one registrable domain**, and staff can **blacklist** a
client, which should block them **immediately**.

## Decision

Standardize on **Django session authentication (cookie-based) for both
surfaces**.

- DRF `SessionAuthentication`; `HttpOnly` + `Secure` + `SameSite` cookies.
- Sessions stored in **PostgreSQL** (no Redis/cache dependency).
- CSRF protection enabled; the SPA sends the CSRF token on unsafe methods.
- Authorization is role-based (admin / staff / client) via DRF permissions,
  independent of the auth mechanism.
- Django's `/admin/` remains enabled as a developer tool for the `admin` role,
  separate from the BO frontend and its API.

## Consequences

- Positive: simplest secure setup; token never exposed to JS; **instant
  revocation** for logout and blacklist; no token store; no Redis for auth.
- Negative: requires single-domain topology (first-party cookies) and CSRF
  handling in the SPAs; less natural if a **native** mobile app is added later.
- Neutral: if separate-domain frontends or native mobile become real
  requirements, revisit with a new ADR (likely JWT).

## Alternatives considered

- **JWT for both / JWT(BO) + session(client).** Rejected for v1: revocation is
  hard (signed tokens valid until expiry), which fights the blacklist/logout
  requirement and usually reintroduces a denylist store; more client code.
