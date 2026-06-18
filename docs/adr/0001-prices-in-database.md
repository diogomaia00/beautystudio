# 0001. Service prices and durations are stored in the database

- Status: Accepted
- Date: 2026-06-17
- Deciders: Diogo

## Context

Service prices and per-service durations (in minutes) must be **configurable by staff in
the Back Office** (staff control their own prices and services). They currently
live in `prices_joao.py` and `prices_tiz.py` at the repo root.

Three storage options were considered: code/config files, environment variables,
or the database. The deciding factor is *who* edits the value and *how often*:
prices change at runtime and are edited by non-developers through the BO.

## Decision

Store service prices and durations in **PostgreSQL**, owned by the `services`
app. The BO edits them through the `services` API (`services.py`).

- `prices_joao.py` / `prices_tiz.py` are demoted to **seed data**: loaded once
  via a data migration or a `seed_prices` management command. After seeding, the
  database is the single source of truth.
- Money is stored in EUR with explicit precision (integer cents or `Decimal`),
  never floats. Durations are stored in minutes (`duration_minutes`).
- "Price on request" (the `-1` sentinel in the seed files) is modeled explicitly
  as a **nullable price + `is_quote_only` flag** — no magic numbers in the DB.
- The current price and duration are **snapshotted onto the appointment** at
  booking time, so later price edits affect only future bookings and never
  rewrite historical revenue (required by the monthly report).

## Consequences

- Positive: staff self-serve pricing in the BO; revenue reports stay accurate;
  no redeploy to change a price; integrity enforced by DB constraints.
- Negative: needs a seed/migration step and a small admin UI; price history /
  snapshotting must be implemented deliberately.
- Neutral: the `prices_*.py` files remain in the repo purely as seed input.

## Alternatives considered

- **Config file / `.env`.** Rejected: deploy-time only, not editable by staff,
  requires a redeploy per change, and unsuitable for per-staff data.
- **Hard-coded in `prices_*.py`.** Rejected: same deploy-time limitation; cannot
  be edited from the BO.
