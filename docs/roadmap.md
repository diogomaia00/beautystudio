# BEAUTY STUDIO — DEVELOPMENT ROADMAP

Ordered list of tasks to bring v1 to life, derived from `.claude/rules/`.
Update each task's **Status** as work progresses.

**Status values:** `pending` → `in-progress` → `developed`

> Conventions: develop each task on a `feat/*` or `fix/*` branch off `dev`, with tests, then merge to `dev` (see `.claude/rules/git.md`). 
> Keep this file in sync with reality — flip Status to `developed` once a task is merged and tested.

---

## Phase 0 — Repo & infrastructure scaffold

| #   | Status | Task |
|-----|--------|------|
| 0.1 | developed | Monorepo skeleton (`backend/`, `frontend/`, `infra/`, root `Makefile`, `README`) |
| 0.2 | developed | `docker-compose.yml` (runtime-agnostic — Docker/Rancher Desktop) with backend, frontend, postgres, worker (Procrastinate), nginx |
| 0.3 | developed | NGINX reverse-proxy config (`infra/nginx/nginx.conf`) routing client app + BO + API |
| 0.4 | developed | `.env.example` with grouped placeholders (`POSTGRES_*`, `TWILIO_*`, `GOOGLE_CALENDAR_*`) |
| 0.5 | developed | Makefile targets: `run`, `migrate`, `makemigrations`, `shell`, `test` (+ `lint`, `logs`, `down`) |
| 0.6 | pending | CI pipeline (lint + tests on PR to `dev`/`main`) |

## Phase 1 — Backend foundation

| #   | Status | Task |
|-----|--------|------|
| 1.1 | developed | Django project bootstrap with split settings (`config/settings/{base,dev,prod}.py`) |
| 1.2 | developed | DRF setup: versioned API bases (client `/v1/`, BO `/bo/v1/`), pagination, consistent error envelope |
| 1.3 | developed | `common/` shared modules (permissions, pagination, utils, constants) |
| 1.4 | developed | Procrastinate app (`config/procrastinate.py`) + worker & periodic-task wiring |
| 1.5 | developed | Structured logging with request correlation ID |
| 1.6 | developed | Health-check endpoint(s) |
| 1.7 | developed | OpenAPI schema + docs generation |
| 1.8 | developed | `system_settings`: `booking_slot_minutes` (15), `booking_horizon_days` (60), `minimum_notice_hours` (2), `max_appointments_per_day/week/batch` (3) |
| 1.9 | developed | Bruno API collection (`.bru`) under `backend/tests/bruno/`, kept in sync with endpoints |

## Phase 2 — Auth (see `auth.md`)

| #   | Status | Task |
|-----|--------|------|
| 2.1 | pending | Custom user model + roles (admin / staff / client); `msisdn` login identifier |
| 2.2 | pending | Session auth (DRF `SessionAuthentication`, cookie-based) for both surfaces; CSRF; DB-backed sessions |
| 2.2b | pending | SMS OTP login (all roles): `otp_code` table, request/verify endpoints, Twilio send, hashed codes + TTL + rate-limit; session on success |
| 2.3 | pending | Enable Django `/admin/` (password-based) for the admin superuser; app login stays OTP |
| 2.4 | pending | Role/permission-based access control (DRF permissions in `common/`) |

## Phase 3 — Domain apps (see `backend.md`, `ddd.md`, `business-rules.md`)

| #   | Status | Task |
|-----|--------|------|
| 3.1 | pending | `users`: client self sign-up (first/last name, birthday, email, msisdn — all required); login identifier = msisdn; profile + preferred channel; per-client duration override (minutes) |
| 3.1c | pending | `users`/`staff`: staff_education table (type/provider/date/description) + CRUD |
| 3.1b | pending | `users`: client `blacklisted` flag (BOOLEAN, default false) + attendance history (derived from appointment status) |
| 3.2 | pending | `services`: categories; service → one staff; price + `duration_minutes` in DB |
| 3.2b | pending | `services`: service_discount (seasonal %); effective price flows into appointment snapshot |
| 3.3 | pending | `services`: `is_quote_only` (nullable price) for "price on request" |
| 3.4 | pending | `services`: `seed_prices` migration/command from `prices_joao.py` / `prices_tiz.py` |
| 3.5 | pending | `availability`: per-staff weekly schedule (`staff_schedules`, `TIME` start/end per weekday) |
| 3.6 | pending | `availability`: time-off / holiday blocking (`staff_time_off`, `TIMESTAMPTZ` ranges) |
| 3.7 | pending | `availability`: daily break windows (non-bookable) |
| 3.8 | pending | `availability`: **dynamic** slot generation (granularity `booking_slot_minutes`) from schedule minus time-off, breaks, and existing appointments — never stored |
| 3.9 | pending | `availability`: waitlist on occupied times + custom booking requests (beyond `booking_horizon_days`) |
| 3.10 | pending | `appointments`: booking creation as `start_at`/`end_at` (UTC `TIMESTAMPTZ`); `transaction.atomic` + `select_for_update` + idempotency; server-side conflict checks (schedule, time-off, overlap, min-notice, horizon, **blacklist**) |
| 3.11 | pending | `appointments`: per-day (3) and per-week (3) limits; batches (≤3) |
| 3.12 | pending | `appointments`: lifecycle booked / made / canceled / no-show; auto-confirm within booking horizon |
| 3.13 | pending | `appointments`: price + `duration_minutes` snapshot at booking time |
| 3.14 | pending | `appointments`: Nail Art add-on minutes (+15 simple / +30 complex, extending `end_at`); client lock + edit modal; staff-only edits |
| 3.15 | pending | `appointments`: self cancel/reschedule up to 24h before; free that time → notify waitlist |
| 3.16 | pending | `notifications`: email + SMS (Twilio); respect preferred channel; BO alerts (waitlist, custom requests) |
| 3.17 | pending | `notifications`: appointment reminder task (~24h before) via Procrastinate periodic task |
| 3.18 | pending | `notifications`: birthday SMS task |
| 3.19 | pending | `analytics`: aggregations feeding reports |
| 3.20 | pending | `reports`: monthly report generation (hours, appts booked/made/canceled, clients, top-3 services, revenue, revenue/hour) |

## Phase 4 — Client app frontend (see `frontend.md`)

| #   | Status | Task |
|-----|--------|------|
| 4.1 | pending | Next.js app bootstrap (App Router, TS strict, TanStack Query, Jost font) |
| 4.2 | pending | Design system tokens (color, spacing, radius, typography, motion) + base UI components |
| 4.3 | pending | Auth (session) — login / register |
| 4.4 | pending | Service catalog browse by category |
| 4.5 | pending | Booking flow with FullCalendar (server-validated availability) |
| 4.6 | pending | Appointment list + self cancel/reschedule (≤24h rule) |
| 4.7 | pending | Nail Art edit modal (client cannot switch simple↔complex) |
| 4.8 | pending | Client profile (birthday, preferred channel) |
| 4.9 | pending | Mobile-first responsive pass (clients are mostly on mobile) |
| 4.10 | pending | Public staff profile page (education/experience) |

## Phase 5 — Back office frontend (`(bo)` route group, same Next.js app)

| #   | Status | Task |
|-----|--------|------|
| 5.1 | pending | BO app bootstrap + session auth (see ADR 0002) |
| 5.2 | pending | Services & pricing management (incl. `is_quote_only`) |
| 5.2b | pending | BO: manage seasonal discounts + staff education |
| 5.3 | pending | Staff schedule / time-off / break-window management |
| 5.4 | pending | Client management + per-client duration override (minutes) |
| 5.4b | pending | BO: staff add/remove client blacklist; view client attendance history |
| 5.5 | pending | Waitlist + custom-request handling |
| 5.6 | pending | Mark appointment made / no-show; edit Nail Art appointments |
| 5.7 | pending | Monthly reports view |
| 5.8 | pending | Tablet-first responsive pass (staff are mostly on iPad) |

## Phase 6 — Cross-cutting & hardening

| #   | Status | Task |
|-----|--------|------|
| 6.1 | pending | Test suites: unit (services/selectors), integration (endpoints), frontend component/e2e |
| 6.2 | pending | Rate limiting / throttling |
| 6.3 | pending | HTTPS / TLS at NGINX; deployment to Hetzner VPS |
| 6.4 | pending | Seed/fixtures for local dev |

---

## Roadmap (post-v1, not scheduled)

| #   | Status | Task |
|-----|--------|------|
| R.1 | pending | `payments` app — MBWay online payments |
| R.2 | pending | WhatsApp notifications (reminders, birthday, loyalty, Christmas, New Year) |
| R.3 | pending | Google Calendar sync of confirmed appointments to staff calendars |
| R.4 | pending | Waitlist auto-offer (time-boxed claim) instead of manual staff contact |
| R.5 | pending | No-show penalty / strike system |
