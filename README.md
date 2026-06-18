# BEAUTY STUDIO

Beauty Studio is a booking web app + a back office for an aesthetic clinic, built as a SaaS monorepo. 

### Built for who?
It serves three kinds of people: 
  - **clients**, who self sign-up and book appointments for a service at a specific date and time
  - **staff**, who provide the services and manage their own prices, services, and schedules
  - **admin** (dev), with total control over the app.

### High-level explanation of important features
- The clinic offers services grouped into categories (nails, depilation laser, aesthetics, wellbeing), each owned by a single staff member. 
- Booking is **time-based**: services define a duration in minutes and the bookable calendar is generated dynamically from each staff member's weekly schedule. 
- The system enforces daily adn weekly booking limits, batches, a waitlist for occupied times, custom requests beyond the booking horizon, and a staff-managed client blacklist. 
- Background work — appointment reminders, birthday messages, and monthly reports — runs as scheduled jobs.

## Documentation

- Detailed rules live in [`.claude/rules/`](.claude/rules/); 
- Architecture decisions are recorded in [`docs/adr/`](docs/adr/); 
- Development task list is in [`docs/roadmap.md`](docs/roadmap.md).

## Tech Stack

**Backend**
- Django + Django REST Framework
- PostgreSQL
- Procrastinate (Postgres-native task queue — no Redis)

**Frontend**
- Next.js (React + TypeScript)
- TanStack Query
- FullCalendar

**Infrastructure**
- Docker / Docker Compose
- NGINX reverse proxy

**Auth**
- Django session authentication (cookie-based) for both FE and BE surfaces

> No application cache and no Redis are needed at this volume; 
> Background and scheduled jobs use the existing PostgreSQL via Procrastinate.


### Versions

Target versions (verified June 2026). Pin the exact patch in `requirements/*.txt`
and `package.json` at scaffold time.

| Area | Tool | Version |
|------|------|---------|
| Language | Python | 3.14 |
| Backend | Django | 5.2 LTS |
| Backend | Django REST Framework | 3.17 |
| Backend | Procrastinate | 3.8.x |
| Database | PostgreSQL | 18 |
| Frontend | Node.js | 22 LTS or newer |
| Frontend | Next.js | 16 (App Router) |
| Frontend | React | 19 |
| Frontend | TypeScript | 5.x |
| Frontend | TanStack Query | v5 |
| Frontend | FullCalendar | 6 |
| Infra | NGINX | 1.27 (stable) |
| Infra | Docker Compose | 5.1.4 |
| Tooling | Bruno | latest |

## Architecture

The repository is a **monorepo** with `backend/`, `frontend/`, and `infra/` packages.

```
browser ──> NGINX ──> frontend (Next.js: client app + back office)
                 └──> backend  (Django REST API)
backend  ──> PostgreSQL
backend  ──> Procrastinate worker ──> PostgreSQL (task queue + periodic jobs)
backend  ──> integrations (Google Calendar, email, SMS/Twilio)
```

- **Two frontends, one API.** 
  The client app (booking) and the back office (staff/admin) live in one Next.js app as `(client)`/`(bo)` route groups, served under one domain via NGINX, and talk to the same Django backend. 
  The client app uses `/v1/...` and the back office uses `/bo/v1/...`.

- **Single session auth under one domain.** 
  NGINX serves the client app, the BO, and the API under one registrable domain, so cookies are first-party;
  Sessions are stored in PostgreSQL, giving instant revocation for logout and blacklisting. 
  Authorization is role-based (admin / staff / client).

- **Domain-driven backend.** Each Django app owns a slice of the domain; business logic lives in a service layer (`services.py` for writes, `selectors.py` for reads), keeping views thin.

- **Feature-based frontend.** Code is grouped by feature, not by file type.

- **Postgres-native async.** Notifications, reminders, calendar sync, and monthly reports run as background/scheduled jobs on Procrastinate — no separate broker.

- **Concurrency-safe booking.** Appointment creation runs in a transaction, re-checks availability under lock, and is idempotent to prevent double-booking.

### Example flow — booking an appointment

```
   ┌───────────────────────┐
   │ Client app (Next.js)  │   POST /v1/appointments
   └───────────┬───────────┘
               │
               ▼
   ┌───────────────────────┐
   │ NGINX (reverse proxy) │
   └───────────┬───────────┘
               │
               ▼
   ┌───────────────────────────────────────────────────────┐
   │ Django REST API                                       │
   │                                                       │
   │  views.py     ── validate input (serializer)          │
   │     │                                                 │
   │     ▼                                                 │
   │  services.py  ── atomic txn · lock · business rules   │
   │     │                                                 │
   │     ├─▶ selectors.py  check availability / conflicts  │
   │     ├─▶ models.py     save appointment ───────────────┼──▶ PostgreSQL
   │     └─▶ tasks.py      enqueue confirmation ───────────┼──▶ Procrastinate (Postgres queue)
   │     │                                                 │ 
   │     ▼                                                 │
   │  201 Created (serialized appointment)                 │
   └───────────┬────────────────────────────────────────── ┘
               │
               ▼
   ┌──────────────────────┐
   │ Procrastinate worker │ ──▶ email / SMS (Twilio)
   └──────────────────────┘
```

See [`.claude/rules/architecture.md`](.claude/rules/architecture.md) for the full rationale and the ADR process.
