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
| 2.1 | developed | Custom user model + roles (admin / staff / client); `msisdn` login identifier |
| 2.2 | developed | Session auth (DRF `SessionAuthentication`, cookie-based) for both surfaces; CSRF; DB-backed sessions |
| 2.2b | developed | SMS OTP login (all roles): `otp_code` table, request/verify endpoints, Twilio send, hashed codes + TTL + rate-limit; session on success |
| 2.3 | developed | Enable Django `/admin/` (password-based) for the admin superuser; app login stays OTP |
| 2.4 | developed | Role/permission-based access control (DRF permissions in `common/`) |

## Phase 3 — Domain apps (see `backend.md`, `ddd.md`, `business-rules.md`)

| #   | Status | Task |
|-----|--------|------|
| 3.1 | developed | `users`: client self sign-up (first/last name, birthday, email, msisdn — all required); login identifier = msisdn; profile + preferred channel; per-client duration override (minutes) |
| 3.1c | developed | `users`/`staff`: staff_education table (type/provider/date/description) + CRUD |
| 3.1b | developed | `users`: client `blacklisted` flag (BOOLEAN, default false) + attendance history (derived from appointment status) |
| 3.2 | developed | `services`: categories; service → one staff; price + `duration_minutes` in DB |
| 3.2b | developed | `services`: service_discount (seasonal %); effective price flows into appointment snapshot |
| 3.3 | developed | `services`: `is_quote_only` (nullable price) for "price on request" |
| 3.4 | developed | `services`: `seed_prices` migration/command from `prices_joao.py` / `prices_tiz.py` |
| 3.5 | developed | `availability`: per-staff weekly schedule (`staff_schedules`, `TIME` start/end per weekday) |
| 3.6 | developed | `availability`: time-off / holiday blocking (`staff_time_off`, `TIMESTAMPTZ` ranges) |
| 3.7 | developed | `availability`: daily break windows (non-bookable) |
| 3.8 | developed | `availability`: **dynamic** slot generation (granularity `booking_slot_minutes`) from schedule minus time-off, breaks, and existing appointments — never stored |
| 3.9 | developed | `availability`: waitlist on occupied times + custom booking requests (beyond `booking_horizon_days`) |
| 3.10 | developed | `appointments`: booking creation as `start_at`/`end_at` (UTC `TIMESTAMPTZ`); `transaction.atomic` + `select_for_update` + idempotency; server-side conflict checks (schedule, time-off, overlap, min-notice, horizon, **blacklist**) |
| 3.11 | developed | `appointments`: per-day (3) and per-week (3) limits; batches (≤3) |
| 3.12 | developed | `appointments`: lifecycle booked / made / canceled / no-show; auto-confirm within booking horizon |
| 3.13 | developed | `appointments`: price + `duration_minutes` snapshot at booking time |
| 3.14 | developed | `appointments`: Nail Art add-on minutes (+15 simple / +30 complex, extending `end_at`); client lock + edit modal; staff-only edits |
| 3.15 | developed | `appointments`: self cancel/reschedule up to 24h before; free that time → notify waitlist |
| 3.16 | developed | `notifications`: email + SMS (Twilio); respect preferred channel; BO alerts (waitlist, custom requests) |
| 3.17 | developed | `notifications`: appointment reminder task (~24h before) via Procrastinate periodic task |
| 3.18 | developed | `notifications`: birthday SMS task |
| 3.19 | developed | `analytics`: aggregations feeding reports |
| 3.20 | developed | `reports`: monthly report generation (hours, appts booked/made/canceled, clients, top-3 services, revenue, revenue/hour) |

## Phase 4 — Client app frontend (see `frontend.md`)

| #   | Status | Task |
|-----|--------|------|
| 4.1 | developed | Next.js app bootstrap (App Router, TS strict, TanStack Query, Jost font) |
| 4.2 | developed | Design system tokens (color, spacing, radius, typography, motion) + base UI components — `tokens.css` + layout components (Navbar/Footer/PageHeader/SchedulingTabs) + UI kit in `components/ui` (`Button`, `Input`, `Field`, `Select`, `Modal`), all consuming semantic tokens |
| 4.3 | developed | Auth (session) — login / register — SMS-OTP **login** + **sign-up** (2-step: number → 6-digit code) with React Hook Form, CSRF-aware API client, session via `/auth/me`, logout, and navbar auth state. Flow: `login-otp.puml`. OTP is SMS-only via **Telnyx** (ADR 0007). ⚠️ To test OTP locally, leave `TELNYX_*` empty so the dev client logs the code |
| 4.4 | developed | Service catalog browse by category — `/agendar` tabs from `GET /v1/services/categories` + `/v1/services`; price (effective/discounted) + duration; Laser is display-only (contact João Veloso, `features/services/config.ts`) |
| 4.5 | developed | Booking flow (server-validated availability) — `/agendar` bookable services open a **mobile-first date → nail-art → slot → confirm** panel (`features/appointments`): `GET /v1/availability/slots` + `POST /v1/appointments` with idempotency key, login-gated, conflict/error handling. UI choice: date+slot list over FullCalendar (clients on mobile); **FullCalendar reserved for the BO staff calendar (Phase 5)**. Flow: `create-appointment.puml` |
| 4.6 | developed | Appointment list + self cancel/reschedule (≤24h rule) — `/marcacoes` (login-gated, navbar link for clients): próximas/histórico, status badges, price snapshot; cancel + reschedule (reuses slot picker) for booked appts >24h out, with a "contact staff" note within 24h (server-enforced too). Flows: `cancel-appointment.puml`, `reschedule-appointment.puml` |
| 4.7 | developed | Nail Art edit modal (client cannot switch simple↔complex) — "Alterar nail art" on booked nail-art appts opens an accessible `Modal` (close button) telling the client to talk to the esteticista; server still enforces 403. Flow: `edit-nail-art-blocked.puml` |
| 4.8 | developed | Client profile (birthday, preferred channel) — `/perfil` (login-gated): RHF form for name/email/birthday/preferred_channel (whatsapp/sms/email), msisdn read-only; `GET`/`PATCH /v1/profile/` (birthday added to read serializer); greeting in navbar links here. Flow: `update-profile.puml` |
| 4.9 | developed | Mobile-first responsive pass (clients are mostly on mobile) — all client pages verified at 375px: home/agendar/serviços + login/register (centered cards, full-width CTAs); marcações/perfil reuse the same responsive primitives + fluid `(client)` container |
| 4.10 | in-progress | ⏸ **DEFERRED by owner** (add later). Public staff profile page — `/equipa` already wired to `GET /v1/staff` (real formations + loading/empty/error states). **TODO when resumed:** add `bio` (text) + photo to the staff model/API (photos as static files in `frontend/public/` per owner's choice; DB holds text), surface intro + photo on `/equipa`, and supply the content (photos, intros, formations) |

> Also delivered (not tracked as rows above): welcome/home page (`/`), `(client)` shell with sticky navbar (text-link logo + nav) and footer, `/servicos` placeholder page, the footer clinic address backed by `system_settings.location` (migration `core.0002`), the TanStack Query provider (`shared/api/Providers`), a dev-only API proxy (`BACKEND_ORIGIN` rewrite in `next.config.ts` + git-ignored `frontend/.env.local`) so `npm run dev` reaches the backend without NGINX, the CSRF-aware API client (`lib/api.ts`), and the `react-hook-form` dependency.

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
