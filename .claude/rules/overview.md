# PROJECT OVERVIEW

Create a production-ready monorepo for a **SaaS-ready aesthetic single-clinic
booking web application** and its corresponding **back office (BO)**.

## TECH STACK

### Backend
- Django
- Django REST Framework
- PostgreSQL
- Procrastinate (Postgres-native task queue)

### Frontend
- Next.js (React + TypeScript)
- TanStack Query
- FullCalendar

### Infrastructure
- Docker / Docker Compose
- NGINX reverse proxy

> No application cache and no Redis are needed (low user volume). Background and
> scheduled jobs run on a Postgres-native task queue (Procrastinate).

## HIGH-LEVEL SYSTEM REQUIREMENTS

- Single-clinic architecture with multiple staff members.
- Handle concurrent booking by clients safely (DB transactions, idempotency).
- Scheduling and editing of services and workflows.
- Authentication roles: admin, staff, clients.
- Background jobs (staff notifications, client reminders).
- Cron jobs (monthly reports: services made and revenue).
- Client app and back office as `(client)`/`(bo)` route groups in one Next.js app, served under one domain (see ADR 0005).
- Responsive across devices (desktop, iPad, iPhone, Android).
- Containerized local development.

> IMPORTANT: domain-driven backend structure (`ddd.md`) and feature-based frontend structure (`frontend.md`).

## MONOREPO ROOT STRUCTURE

```
beautystudio/
├── backend/            # Django + DRF + Procrastinate
├── frontend/           # Next.js client app + back office
├── infra/              # NGINX, Postgres, scripts
├── docker-compose.yml
├── .env                # never committed
├── .gitignore
├── Makefile
└── README.md
```

> Source code lives inside `backend/` and `frontend/`. There is no flat `/src` directory at the repo root.

## CANONICAL DOMAIN (v1)

Backend apps (see `backend.md` for the authoritative list):
`users`, `services`, `appointments`, `availability`, `notifications`, `analytics`, `reports`.

Roadmap (not in v1): online `payments` (MBWay), WhatsApp notifications.

## SCAFFOLD DELIVERABLES

Directory structure, starter configuration files, docker-compose configuration,
Django project bootstrap, Next.js bootstrap, task-queue (Procrastinate) scaffold, NGINX
scaffold, environment variable placeholders.

> The goal is a clean, production-grade starter monorepo scaffold. If any value
> or decision is unclear, ask before implementing (see `CLAUDE.md`).
