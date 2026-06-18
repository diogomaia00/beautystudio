# DATABASE & SCHEDULING DATA MODEL

> The SQL below is **illustrative**, not the final schema — entities/tables are
> not built yet. It fixes the data-modeling guidelines and the Postgres type for
> each kind of column. Code-level naming lives in `naming-conventions.md`;
> business behaviour in `business-rules.md`; layering in `ddd.md`; the pricing
> decision in `docs/adr/0001-prices-in-database.md`.

## Core principle — time-based, not slot-based

The booking system is **time-based**, not slot-based.

- Services define their duration in **minutes** (`duration_minutes`).
- Appointments store **exact start/end timestamps** (`start_at`, `end_at`).
- Calendar slots are **generated dynamically** by the application and are **never stored** as business data.

## Services

Treatments offered by the clinic. Duration is stored in minutes.

```sql
services
  id                UUID PRIMARY KEY
  name              VARCHAR(255) NOT NULL
  description       TEXT
  duration_minutes  INTEGER NOT NULL
  price             DECIMAL(10,2)        -- nullable; see is_quote_only
  created_at        TIMESTAMPTZ
  updated_at        TIMESTAMPTZ
```

Example values:

```text
Hydra Facial      duration_minutes = 60
Manicure          duration_minutes = 45
Lash Extensions   duration_minutes = 120
```

> Notes (per `business-rules.md` / ADR 0001): a real service also carries a `staff_id` (each service is offered by exactly one staff member) and a
> category, and `price` is **nullable** with an `is_quote_only` boolean for "price on request" — do not store the `-1` sentinel from the seed files.

## Appointments

A booking made by a client. Stores explicit start and end timestamps.

```sql
appointments
  id           UUID PRIMARY KEY
  client_id    UUID NOT NULL
  staff_id     UUID NOT NULL
  service_id   UUID NOT NULL
  status       VARCHAR(50) NOT NULL
  start_at     TIMESTAMPTZ NOT NULL
  end_at       TIMESTAMPTZ NOT NULL
  notes        TEXT
  created_at   TIMESTAMPTZ
  updated_at   TIMESTAMPTZ
```

Example (45-minute service):

```text
start_at = 2026-07-01 14:00:00+00
end_at   = 2026-07-01 14:45:00+00
```

> Notes: `end_at` is computed from the service duration (plus any Nail Art add-on minutes, plus any per-client duration override). 
> Per ADR 0001, the appointment also **snapshots** the price and duration at booking time so later BO edits don't rewrite historical revenue.

## Staff working schedule

Recurring weekly availability of a staff member.

```sql
staff_schedules
  id          UUID PRIMARY KEY
  staff_id    UUID NOT NULL
  weekday     SMALLINT NOT NULL     -- 1..7 (1=Sun, 2=Mon … 7=Sat)
  start_time  TIME NOT NULL
  end_time    TIME NOT NULL
  created_at  TIMESTAMPTZ
  updated_at  TIMESTAMPTZ
```

Example: `Monday  start_time = 09:00  end_time = 18:00`

> **Weekday encoding:** `1=Sun, 2=Mon … 7=Sat` (clinic convention — not ISO).
> Convert from a date with `stored = (date.isoweekday() % 7) + 1`, kept in a
> single helper so no code compares a raw `isoweekday()`/`weekday()` to the
> stored value.

## Staff time off

Vacations, sick leave, holidays, or other unavailable periods.

```sql
staff_time_off
  id          UUID PRIMARY KEY
  staff_id    UUID NOT NULL
  start_at    TIMESTAMPTZ NOT NULL
  end_at      TIMESTAMPTZ NOT NULL
  reason      VARCHAR(255)
  created_at  TIMESTAMPTZ
  updated_at  TIMESTAMPTZ
```

## System configuration

Defines scheduling behaviour (single-clinic settings, not a domain entity).

```sql
system_settings
  booking_slot_minutes   INTEGER NOT NULL   -- calendar granularity
  booking_horizon_days   INTEGER NOT NULL   -- how far ahead clients can book
  minimum_notice_hours   INTEGER NOT NULL   -- min lead time before start_at
  max_appointments_per_day    INTEGER NOT NULL   -- per-client daily limit
  max_appointments_per_week   INTEGER NOT NULL   -- per-client weekly limit
  max_appointments_per_batch  INTEGER NOT NULL   -- per-batch limit
```

Recommended values:

```text
booking_slot_minutes = 15
booking_horizon_days = 60
minimum_notice_hours = 2
max_appointments_per_day = 3
max_appointments_per_week = 3
max_appointments_per_batch = 3
```

> `booking_slot_minutes` is the **granularity of the generated calendar grid**, not a unit of stored business data.

## Timezone rules

- Always store timestamps in **UTC** using `TIMESTAMPTZ`.
- Convert to local timezone (Portugal) **only when displaying** to users.
- Never store local times inside appointment records.

## Slot generation

Slots are generated **dynamically** from staff availability and existing bookings. 
Never store `slot_count`, `slot_number`, or `slot_index` on services or appointments.

```text
Staff availability: 09:00 → 18:00
Service duration:   45 minutes
Slot granularity:   15 minutes  (booking_slot_minutes)

Generated start times: 09:00, 09:15, 09:30, 09:45, 10:00, ...
```

## Conflict detection

The backend is the source of truth; the frontend calendar must never be trusted for conflict detection. 
Before creating an appointment, on the server:
1. Validate the staff member's working schedule.
2. Validate time-off periods.
3. Validate there is no overlapping appointment for that staff member.
4. Enforce `minimum_notice_hours` and `booking_horizon_days`.
5. Execute creation inside a database transaction (lock to avoid double-booking — see `ddd.md` concurrency rules).

## Recommended Postgres types

| Type            | Used for |
|-----------------|----------|
| `UUID`          | `id`, `client_id`, `staff_id`, `service_id` (all keys) |
| `TIME`          | `start_time`, `end_time` (recurring schedules) |
| `TIMESTAMPTZ`   | `start_at`, `end_at`, `created_at`, `updated_at` |
| `INTEGER`       | `duration_minutes`, `booking_slot_minutes`, `booking_horizon_days`, `minimum_notice_hours` |
| `DECIMAL(10,2)` | `price`, `amount`, `revenue` |
| `VARCHAR`       | `name`, `status`, `reason` |
| `TEXT`          | `description`, `notes` |
| `BOOLEAN`       | flags: `blacklisted`, `is_quote_only`, `has_nail_art` |

## Column naming (canonical)

Use these names consistently across the entire application:

- Duration in minutes: `duration_minutes`
- Timestamp range: `start_at` / `end_at`
- Recurring schedule clock times: `start_time` / `end_time`
- Audit columns: `created_at` / `updated_at`

## Clients (blacklist flag)

Clients live in the `users` app. Beyond the `user` fields (first/last name,
email, msisdn, birthday), the `client` row adds the preferred channel and a
staff-managed blacklist flag:

```sql
-- illustrative, on the client/user record
  blacklisted   BOOLEAN NOT NULL DEFAULT FALSE
```

> A `blacklisted` client cannot book through the app (enforced in the
> `appointments` booking service — see `business-rules.md`). Attendance history
> is derived from appointment `status`; there is no strike counter column.
