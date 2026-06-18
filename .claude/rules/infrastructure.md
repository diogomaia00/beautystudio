# INFRASTRUCTURE

## STRUCTURE

```
infra/
├── nginx/
│   └── nginx.conf       # reverse proxy config
├── postgres/            # init scripts / volumes config
└── scripts/             # operational/utility scripts
```

Repo root also contains: `docker-compose.yml`, `.env` (never committed), `.env.example`, `Makefile`.

## LOCAL CONTAINER RUNTIME

The stack is **runtime-agnostic** — it only needs a Docker-compatible CLI plus
Compose. Docker Desktop is **not** required; **Rancher Desktop** (dockerd/moby
backend) is the supported local runtime. Avoid Docker Desktop-only features.

## DOCKER SERVICES

- `backend` — Django + DRF (Gunicorn/Uvicorn in prod).
- `frontend` — single Next.js app (client + back office as `(client)`/`(bo)` route groups).
- `postgres` — PostgreSQL.
- `worker` — Procrastinate worker (background + scheduled jobs: reminders, birthday, monthly reports — see `background-jobs.md`).
- `nginx` — reverse proxy / TLS termination.

### Request flow

```
browser ──> nginx ──> frontend (Next.js)
                 └──> backend (Django API)
backend ──> postgres
backend ──> worker (Procrastinate) ──> postgres (task queue)
```

## ENVIRONMENT & SECRETS

- All config via environment variables; nothing secret in the codebase.
- Provide a documented `.env.example` with placeholders (see `naming-conventions.md` for variable naming).
- `.env` is git-ignored and never committed.

## MAKEFILE COMMANDS (via docker-compose)

Required targets, all executing through docker-compose:

- `run` — start the stack.
- `migrate` — apply DB migrations.
- `makemigrations` — generate migrations.
- `shell` — open a Django shell.
- `test` — run the test suite.

> Add `lint`, `logs`, and `down` as convenience targets when useful.

## OBSERVABILITY & HEALTH

- Expose health-check endpoints on the backend.
- Structured logging with request correlation IDs (see `coding-standards.md`).

## DEPLOYMENT

- Target: **single Hetzner VPS** via Docker Compose.
- Client app and back office are one Next.js app (route groups), served under one domain via NGINX (`/` → client, `/bo` → back office); see ADR 0005.
- Enforce HTTPS in all environments (TLS at NGINX).
- See `engineering:deploy-checklist` skill before shipping a release.
