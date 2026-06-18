# DATABASE ENTITIES

Authoritative entity/table reference for Beauty Studio. Follows the data-model
guidelines in [`.claude/rules/database.md`](../../.claude/rules/database.md) and
the decisions captured in [`docs/adr/`](../adr/). The system is **time-based**,
not slot-based.

> Status: **proposal for review.** SQL DDL/seed scripts are generated only after
> this document is accepted.

## Conventions

- Primary keys are `UUID` (generated app-side or via `gen_random_uuid()`).
- All timestamps are `TIMESTAMPTZ` stored in **UTC**; recurring clock times are
  `TIME`. Audit columns `created_at` / `updated_at` on every table.
- Money is `DECIMAL(10,2)` (EUR). Durations are `INTEGER` **minutes**.
- Enums are stored as `VARCHAR` + `CHECK` constraint (Django `choices` style).
- Table names follow Django's `<app>_<model>`; logical names are used below.
- `booking_slot_minutes` (15) is only the calendar grid granularity — never a
  stored unit.

## Modeling notes / assumptions (please confirm on review)

1. **`user`** is the base identity/auth table (all roles). **`client`** and
   **`staff`** are 1:1 extension tables, each with a unique `user_id` FK holding
   role-specific fields.
2. `role` is a single enum on `user` (`admin` / `staff` / `client`).
3. Per-client duration overrides live in **`client_service_duration`**.
4. Appointment overlap per staff is enforced by a Postgres `EXCLUDE` constraint
   (needs the `btree_gist` extension).
5. Nail Art is modeled as an option on the appointment (`none/simple/complex`)
   plus a `supports_nail_art` flag on the service; the +15/+30 min are applied
   when computing `end_at`.
6. Analytics has **no persistent table** in v1 (metrics are aggregated on demand
   from `appointment`); `reports` persists the monthly snapshot.
7. Sessions (`django_session`) and Procrastinate queue tables are
   **framework-managed** (see bottom), not hand-modeled.

---

## Enumerations

| Enum | Values |
|------|--------|
| `user.role` | `admin`, `staff`, `client` |
| `client.preferred_channel` | `email`, `sms` |
| `appointment.status` | `booked`, `made`, `canceled`, `no_show` |
| `appointment.nail_art_option` | `none`, `simple`, `complex` |
| `appointment.cancel_reason` | `client`, `staff` (set only when status = canceled) |
| `waitlist_entry.status` | `waiting`, `notified`, `closed` |
| `custom_appointment_request.status` | `pending`, `handled`, `declined` |
| `notification.channel` | `email`, `sms` |
| `notification.type` | `confirmation`, `reminder`, `birthday`, `festivity`, `bo_alert`, `otp` |
| `notification.status` | `pending`, `sent`, `failed` |
| `staff_education.type` | `formation`, `webinar`, `course`, `certification`, `workshop`, `other` |
| `otp_code.purpose` | `login`, `signup` |

---

## `users` app

### user
Custom user / identity for all roles. Login via **SMS OTP** to `msisdn` (all roles); a session is established on success. Django `/admin/` stays password-based for the admin superuser.

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| email | VARCHAR(254) | no | | UNIQUE; required; email channel (not login) |
| msisdn | VARCHAR(20) | no | | E.164 (intl); UNIQUE; required; login identifier |
| first_name | VARCHAR(150) | no | | required at sign-up |
| last_name | VARCHAR(150) | no | | required at sign-up |
| birthday | DATE | yes | | required for clients at sign-up; powers birthday msg |
| role | VARCHAR(10) | no | `'client'` | CHECK in enum |
| password | VARCHAR(128) | no | | Django hash; unusable for OTP-only users; real password only for the admin `/admin` superuser |
| is_active | BOOLEAN | no | `true` | controls **login access** (Django) |
| last_login | TIMESTAMPTZ | yes | | |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |

### client
1:1 with `user` where `role = client`.

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| user_id | UUID | no | | FK→user, UNIQUE, ON DELETE CASCADE |
| preferred_channel | VARCHAR(10) | no | `'sms'` | CHECK in enum |
| blacklisted | BOOLEAN | no | `false` | staff-managed; blocks booking |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |

### staff
1:1 with `user` where `role = staff`.

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| user_id | UUID | no | | FK→user, UNIQUE, ON DELETE CASCADE |
| display_name | VARCHAR(255) | yes | | public-facing name |
| msisdn | VARCHAR(20) | yes | | **separate** business/WhatsApp number, distinct from the personal login `user.msisdn` (roadmap) |
| is_active | BOOLEAN | no | `true` | staff **bookable/visible** (services & schedule); independent of login (`user.is_active`) |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |

### staff_education
Formations/courses a staff member completed, shown on a public staff page so
clients can see their experience.

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| staff_id | UUID | no | | FK→user (staff) |
| type | VARCHAR(20) | no | | CHECK in enum (formation, webinar, …) |
| title | VARCHAR(255) | yes | | name of the formation |
| provider | VARCHAR(255) | yes | | company/service that provided it |
| description | TEXT | yes | | |
| completed_on | DATE | yes | | date of the formation |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |

### client_service_duration
Per-client duration override (minutes) for a given service.

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| client_id | UUID | no | | FK→user (client) |
| service_id | UUID | no | | FK→service |
| duration_minutes | INTEGER | no | | CHECK > 0 |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |
| | | | | UNIQUE (client_id, service_id) |

### otp_code
One-time codes for SMS OTP login/verification (all roles). Store a **hash** of
the code, never the plaintext. For **login** the code is tied to `user_id`; for
**signup** the user doesn't exist yet, so it's tied to `msisdn` (`user_id` NULL)
and resolved into a user on successful verify.

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| user_id | UUID | yes | | FK→user, ON DELETE CASCADE; NULL during signup |
| msisdn | VARCHAR(20) | no | | target number (drives signup before a user exists) |
| code_hash | VARCHAR(128) | no | | hashed OTP (never plaintext) |
| purpose | VARCHAR(20) | no | `'login'` | CHECK in enum (login, signup) |
| expires_at | TIMESTAMPTZ | no | | short TTL (e.g. 5 min) |
| consumed_at | TIMESTAMPTZ | yes | | set when the code is used |
| attempts | INTEGER | no | `0` | verify attempts (rate-limit) |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |

---

## `services` app

### service_category
| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| name | VARCHAR(255) | no | | e.g. nails, depilation laser, estética, wellbeing |
| description | TEXT | yes | | |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |

### service
Each service is offered by exactly one staff member.

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| name | VARCHAR(255) | no | | |
| description | TEXT | yes | | |
| category_id | UUID | no | | FK→service_category |
| staff_id | UUID | no | | FK→user (staff) |
| duration_minutes | INTEGER | no | | CHECK > 0 |
| price | DECIMAL(10,2) | yes | | NULL when quote-only; CHECK >= 0 |
| is_quote_only | BOOLEAN | no | `false` | "price on request" (replaces -1 sentinel) |
| supports_nail_art | BOOLEAN | no | `false` | nail services only |
| is_active | BOOLEAN | no | `true` | |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |
| | | | | CHECK (price IS NOT NULL OR is_quote_only) |

### service_discount
Seasonal percentage discount on a service's price (BO-managed by staff/admin).

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| service_id | UUID | no | | FK→service |
| percentage | INTEGER | no | | CHECK 1..100 (% off the price) |
| starts_at | TIMESTAMPTZ | yes | | validity start (NULL = immediate) |
| ends_at | TIMESTAMPTZ | yes | | validity end (NULL = open-ended) |
| is_active | BOOLEAN | no | `true` | |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |

> Effective price = `price × (1 − active_discount/100)`, computed at booking and
> captured in `appointment.price_snapshot` so later discount edits never rewrite
> past revenue.

---

## `appointments` app

### appointment_batch
Groups up to 3 appointments booked together.

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| client_id | UUID | no | | FK→user (client) |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |

### appointment
A booking as an explicit time range; price/duration snapshotted at booking.
Reschedule is an **in-place update** of `start_at`/`end_at` (status stays
`booked`); the old time is freed and the waitlist notified — no cancellation row
is created.

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| batch_id | UUID | yes | | FK→appointment_batch, ON DELETE SET NULL |
| client_id | UUID | no | | FK→user (client) |
| staff_id | UUID | no | | FK→user (staff) |
| service_id | UUID | no | | FK→service |
| status | VARCHAR(10) | no | `'booked'` | CHECK in enum |
| cancel_reason | VARCHAR(10) | yes | | CHECK in enum; set only when status = canceled |
| start_at | TIMESTAMPTZ | no | | |
| end_at | TIMESTAMPTZ | no | | CHECK end_at > start_at |
| nail_art_option | VARCHAR(10) | no | `'none'` | CHECK in enum |
| price_snapshot | DECIMAL(10,2) | yes | | copied from service at booking |
| is_quote_only_snapshot | BOOLEAN | no | `false` | copied at booking |
| duration_minutes_snapshot | INTEGER | no | | service + nail-art + override |
| notes | TEXT | yes | | |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |
| | | | | EXCLUDE: no overlap per staff (see Triggers & constraints) |

---

## `availability` app

### staff_schedule
Recurring weekly working hours.

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| staff_id | UUID | no | | FK→user (staff) |
| weekday | SMALLINT | no | | CHECK 1..7 (1=Sun, 2=Mon … 7=Sat) |
| start_time | TIME | no | | |
| end_time | TIME | no | | CHECK end_time > start_time |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |

> Populated at staff setup; this **is** the bookable availability clients book against.

### staff_break
Daily non-bookable windows (e.g. lunch).

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| staff_id | UUID | no | | FK→user (staff) |
| weekday | SMALLINT | no | | CHECK 1..7 (1=Sun … 7=Sat) |
| start_time | TIME | no | | |
| end_time | TIME | no | | CHECK end_time > start_time |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |

### staff_time_off
Vacations, sick leave, holidays.

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| staff_id | UUID | no | | FK→user (staff) |
| start_at | TIMESTAMPTZ | no | | |
| end_at | TIMESTAMPTZ | no | | CHECK end_at > start_at |
| reason | VARCHAR(255) | yes | | |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |

### waitlist_entry
Interest in an occupied time.

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| client_id | UUID | no | | FK→user (client) |
| service_id | UUID | no | | FK→service |
| desired_start_at | TIMESTAMPTZ | no | | the occupied time wanted |
| status | VARCHAR(10) | no | `'waiting'` | CHECK in enum |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |

### custom_appointment_request
Booking request beyond the booking horizon.

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| client_id | UUID | no | | FK→user (client) |
| service_id | UUID | no | | FK→service |
| preferred_date | DATE | no | | |
| preferred_time | TIME | yes | | |
| status | VARCHAR(10) | no | `'pending'` | CHECK in enum |
| notes | TEXT | yes | | |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |

---

## `notifications` app

### notification
Outbox/log for email & SMS messages.

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| receiver_id | UUID | no | | FK→user |
| appointment_id | UUID | yes | | FK→appointment, ON DELETE SET NULL |
| channel | VARCHAR(10) | no | | CHECK in enum |
| type | VARCHAR(20) | no | | CHECK in enum (`festivity` = Christmas/New Year/etc. — roadmap) |
| payload | TEXT | yes | | rendered message context |
| status | VARCHAR(10) | no | `'pending'` | CHECK in enum |
| sent_at | TIMESTAMPTZ | yes | | |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |

---

## `reports` app

### monthly_report
Snapshot of the previous month's metrics per staff member.

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| staff_id | UUID | no | | FK→user (staff) |
| year | INTEGER | no | | |
| month | INTEGER | no | | CHECK 1..12 |
| hours_worked | DECIMAL(10,2) | no | `0` | |
| appointments_booked | INTEGER | no | `0` | |
| appointments_made | INTEGER | no | `0` | |
| appointments_canceled | INTEGER | no | `0` | |
| clients_served | INTEGER | no | `0` | distinct clients served |
| new_clients | INTEGER | no | `0` | |
| revenue_total | DECIMAL(10,2) | no | `0` | EUR |
| revenue_per_hour | DECIMAL(10,2) | no | `0` | |
| generated_at | TIMESTAMPTZ | no | `now()` | |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |
| | | | | UNIQUE (staff_id, year, month) |

### monthly_report_service
Per-service breakdown for a monthly report (one row per service). Drives both
"top 3 services" (top rows by `appointments_count`) and "revenue per service".

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | UUID | no | `gen_random_uuid()` | PK |
| report_id | UUID | no | | FK→monthly_report, ON DELETE CASCADE |
| service_id | UUID | no | | FK→service |
| appointments_count | INTEGER | no | `0` | |
| revenue | DECIMAL(10,2) | no | `0` | EUR |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |
| | | | | UNIQUE (report_id, service_id) |

---

## System configuration

### system_settings
Single-row scheduling configuration (single-clinic).

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| id | SMALLINT | no | `1` | PK; CHECK (id = 1) — guarantees a single config row |
| booking_slot_minutes | INTEGER | no | `15` | calendar grid granularity |
| booking_horizon_days | INTEGER | no | `60` | how far ahead clients can book |
| minimum_notice_hours | INTEGER | no | `2` | min lead time before start_at |
| max_appointments_per_day | INTEGER | no | `3` | per-client daily limit |
| max_appointments_per_week | INTEGER | no | `3` | per-client weekly limit |
| max_appointments_per_batch | INTEGER | no | `3` | max appointments per batch |
| created_at | TIMESTAMPTZ | no | `now()` | |
| updated_at | TIMESTAMPTZ | no | `now()` | trigger-maintained |

---

## Triggers & constraints

- **`set_updated_at()` trigger** — a shared `BEFORE UPDATE` trigger on every
  table with an `updated_at` column, setting `updated_at = now()`.
- **Appointment overlap prevention** — on `appointment`, a Postgres `EXCLUDE`
  constraint using `btree_gist`:
  `EXCLUDE USING gist (staff_id WITH =, tstzrange(start_at, end_at) WITH &&)
  WHERE (status IN ('booked','made'))`. Requires `CREATE EXTENSION btree_gist`.
- **CHECK constraints** — enum columns (`role`, `status`, `channel`, …),
  `end_at > start_at`, `end_time > start_time`, `weekday BETWEEN 1 AND 7`,
  `period_month BETWEEN 1 AND 12`, `price >= 0`, `duration_minutes > 0`,
  service price/quote rule, `system_settings.id = 1`.
- **Foreign keys** — `ON DELETE CASCADE` for profile→user; `ON DELETE SET NULL`
  for `appointment.batch_id` and `notification.appointment_id`; `RESTRICT`
  elsewhere by default.
- **Booking limits & batch size** are configured in `system_settings`
  (`max_appointments_per_day/week/batch`, default 3) and enforced — with the
  blacklist, horizon, and notice checks — in the **service layer** (`ddd.md`),
  not by DB triggers.

## Indexes (beyond PKs / uniques)

| Table | Index |
|-------|-------|
| user | UNIQUE(email); INDEX(role) |
| service | INDEX(staff_id); INDEX(category_id); INDEX(is_active) |
| appointment | INDEX(staff_id, start_at); INDEX(client_id, start_at); INDEX(status); GIST(staff_id, tstzrange) for EXCLUDE |
| staff_schedule | INDEX(staff_id, weekday) |
| staff_time_off | INDEX(staff_id, start_at, end_at) |
| waitlist_entry | INDEX(service_id, desired_start_at); INDEX(status) |
| custom_appointment_request | INDEX(service_id, status) |
| notification | INDEX(status, created_at); INDEX(receiver_id) |
| monthly_report | UNIQUE(staff_id, year, month) |
| monthly_report_service | UNIQUE(report_id, service_id) |
| service_discount | INDEX(service_id, is_active) |
| staff_education | INDEX(staff_id) |
| otp_code | INDEX(user_id, expires_at); INDEX(msisdn, expires_at) |

## Framework-managed tables (not hand-written)

- **Django**: `auth_*`/admin support tables, `django_session` (DB-backed
  sessions — see ADR 0002), `django_migrations`, content types, permissions.
- **Procrastinate**: `procrastinate_jobs`, `procrastinate_events`,
  `procrastinate_periodic_defers`, etc. — created by Procrastinate's own
  migration (see ADR 0003).
