# 0003. Postgres-native task queue (Procrastinate) instead of Celery + Redis

- Status: Accepted
- Date: 2026-06-17
- Deciders: Diogo

## Context

Background work is limited and mostly scheduled: appointment reminders (~24h
before), birthday messages, monthly reports, plus a few event-driven
notifications (booking confirmations, BO alerts for waitlist joins / custom
requests). Volume is low (single clinic), and PostgreSQL is already the primary
datastore.

Celery requires a dedicated broker (Redis or RabbitMQ); the database-broker path
is deprecated. Sessions were also moved to Postgres (ADR 0002), so Redis would
otherwise exist only to serve Celery.

## Decision

Use **Procrastinate**, a Postgres-native task queue, and **remove Redis and
Celery** from the stack.

- Tasks and their state live in PostgreSQL; a separate **worker** process runs
  them. Periodic (cron-like) tasks cover the scheduled jobs; deferred tasks
  cover event-driven notifications.
- Per-app `tasks.py` modules delegate to the service layer (see `ddd.md`); tasks
  are idempotent with explicit retry/timeout policies.
- Compose services drop `redis`, `celery-worker`, and `celery-beat`; a single
  `worker` service replaces them.

## Consequences

- Positive: one fewer datastore/container; reuses Postgres; handles both
  scheduled and event-driven jobs with retries; simpler local setup and infra.
- Negative: smaller ecosystem/community than Celery; slightly more DB load
  (negligible at this volume); fewer ready-made integrations.
- Neutral: if job volume grows substantially, revisit (Celery + a broker, or a
  managed queue) with a new ADR.

## Alternatives considered

- **Celery + Redis (or RabbitMQ).** Rejected for v1: adds a broker/container
  whose only purpose would be Celery, for low-volume work.
- **django-q2.** Viable Postgres/ORM-broker alternative with a scheduler; a
  reasonable swap if preferred. Procrastinate chosen for its LISTEN/NOTIFY-based
  responsiveness and first-class periodic tasks.
- **Cron + management commands.** Simplest, but no built-in retries and awkward
  for event-driven notifications (inline sends or a hand-rolled outbox).
