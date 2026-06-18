# BACKEND

## TECH STACK

- Django
- Django REST Framework (DRF)
- PostgreSQL
- Procrastinate (Postgres-native task queue, incl. periodic/scheduled jobs)

> NOTE: no application cache layer is required — the app has low user volume.
> There is **no Redis**: background jobs use the existing PostgreSQL via
> Procrastinate (see `background-jobs.md`).

---

## CANONICAL APP LIST (v1)

These are the only Django apps for v1. Do not add, rename, or split apps
without updating this list first.

- `users`
- `services`
- `appointments`
- `availability`
- `notifications`
- `analytics`
- `reports`

### Roadmap (NOT in v1 — do not scaffold yet)

- `payments` — online payments to staff/clinic (MBWay, etc.)
- MBWay integration under `integrations/`

> There is intentionally **no `clinics` app**: this is a single-clinic system,
> so clinic-level configuration is settings/config, not a domain app.

---

## DIRECTORY STRUCTURE

```
backend/
├── config/
│   ├── settings/
│   │   ├── base.py          # shared settings
│   │   ├── dev.py           # local/dev overrides
│   │   └── prod.py          # production overrides
│   ├── urls.py              # root URL conf
│   ├── procrastinate.py     # Procrastinate app definition
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   ├── users/
│   ├── services/
│   ├── appointments/
│   ├── availability/
│   ├── notifications/
│   ├── analytics/
│   └── reports/
│
├── integrations/
│   └── google_calendar/     # sync appointments with staff Google Calendar
│
├── common/
│   ├── permissions.py       # shared DRF permission classes
│   ├── pagination.py        # shared pagination classes
│   ├── utils.py             # shared helpers
│   └── constants.py         # shared enums/constants
│
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
│
├── manage.py
└── Dockerfile
```

> Settings are split per environment under `config/settings/`. The active
> module is selected via `DJANGO_SETTINGS_MODULE` (e.g. `config.settings.dev`).

---

## BACKEND DOMAIN STRUCTURE RULES

Each Django app under `apps/` must follow this layout (file → purpose):

```
apps/<app>/
├── models.py        # database schema (Django ORM)
├── serializers.py   # DRF serializers (input/output shaping + validation)
├── views.py         # API endpoints (thin — no business logic)
├── urls.py          # app-level URL routing
├── selectors.py     # read layer: database queries / fetching
├── services.py      # write layer: business logic / orchestration
├── tasks.py         # background jobs (Procrastinate)
├── admin.py         # Django admin registration
├── apps.py          # app config
├── migrations/      # DB migrations
└── tests/           # unit + integration tests (see testing-strategy)
```

Layering rules (see `ddd.md` for the full rationale):

- Views never contain business logic — they validate input via serializers,
  call a service or selector, and serialize the result.
- All reads go through `selectors.py`; all writes/mutations through `services.py`.
- Background tasks in `tasks.py` are thin wrappers that delegate to services.
- Cross-app calls go through the target app's `services`/`selectors`, never
  by importing another app's models directly.

---

## INTEGRATIONS

- **Notifications**
  - Email via an email provider
  - SMS via Twilio
  - WhatsApp is a roadmap channel (see `business-rules.md`)
- **Google Calendar** — use the Google Calendar API to sync confirmed
  appointments with the responsible staff member's Google Calendar.

> Integration clients live under `integrations/<provider>/` and are invoked
> from app `services.py` / `tasks.py`, never directly from views.

---

## REST API GOOD PRACTICES

Conventions for resources, HTTP semantics, versioning, status codes,
pagination, filtering, validation, idempotency, and the service layer.

> Code-level naming (routes, serializers, fields) lives in `naming-conventions.md`. 
> General coding standards (logging, error handling, testing) live in `coding-standards.md`. 

This section is API-design specific:
- Design APIs around resources and nouns.
- Use HTTP methods according to their intended semantics.
- Version the API from the beginning: client app `/v1/...`, back office `/bo/v1/...`.
- Return appropriate HTTP status codes.
- Implement pagination for all collection endpoints.
- Support filtering, sorting, and searching on collections.
- Maintain a consistent request and response structure.
- Validate all incoming data (in serializers).
- Separate authentication from authorization.
- Protect sensitive data and internal implementation details.
- Ensure idempotency where applicable (especially booking creation).
- Prevent N+1 database query issues (select_related / prefetch_related).
- Use database indexes appropriately.
- Implement structured logging.
- Include a request correlation ID across the entire workflow.
- Apply rate limiting and throttling.
- Generate and maintain OpenAPI documentation.
- Keep business logic out of views — use the service layer.
- Apply repository/selector data-access abstractions.
- Use background workers (Procrastinate) for long-running tasks.
- Implement health check endpoints.
- Use database transactions for critical operations (booking, batches).
- Handle errors consistently with standard error codes and messages.
- Enforce HTTPS in all environments.
- Store secrets outside the codebase.
- Follow the principle of least privilege.
- Implement role/permission-based access control (admin, staff, client).
- Monitor performance, errors, and latency; implement observability.
- Write automated unit, integration, and end-to-end tests.
- Maintain backward compatibility; deprecate features via a documented process.
- Define clear timeout and retry strategies; make operations resilient.
- Document breaking changes before release.
- Use configuration management for environment-specific settings.
- Audit and keep dependencies updated.
- Design endpoints to be predictable, discoverable, and simple.
- Measure, monitor, and continuously improve API reliability.

---

## API TESTING (Bruno)

API endpoints are exercised with **Bruno** collections (plain-text `.bru` files,
version-controlled — open-source, no Docker Desktop dependency).

- Location: `backend/tests/bruno/` — one folder per app/resource, mirroring the
  versioned routes (`/v1/...` and `/bo/v1/...`).
- Keep the collection **in sync with the endpoints**: every new or changed
  endpoint ships with its `.bru` request(s) in the same PR.
- Use Bruno environments for `local` / `dev` (base URL, auth tokens). Never
  commit secrets — reference environment variables.
- Bruno complements, not replaces, automated tests: DRF unit/integration tests
  remain the source of truth in CI (see `coding-standards.md`).
