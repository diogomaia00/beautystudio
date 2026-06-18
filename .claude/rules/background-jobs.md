# BACKGROUND & SCHEDULED JOBS

Async and scheduled work runs on **Procrastinate**, a Postgres-native task queue
(no Redis, no separate broker). Tasks are stored and coordinated in PostgreSQL;
a separate **worker** process executes them, and **periodic** (cron-like) tasks
cover the scheduled jobs. See `docs/adr/0003-postgres-task-queue.md`.

Tasks live in each app's `tasks.py` and **delegate to that app's service layer**
(see `ddd.md`); task bodies contain no business logic.

## Use cases

### Messages (`notifications` app)

#### Appointment reminders
Sent **~24h before** (the day before) the appointment, via the client's
preferred channel (email or SMS; WhatsApp is roadmap), including:
- Day and hour of the appointment
- Type of service
- Service value

#### Birthday message
Send an SMS wishing the client a happy birthday on behalf of the Beauty Studio
team.

### Reports (`reports` app)

#### Monthly report generation
On the first day of each month, generate a report about the previous month,
presented to the staff member in the BO, containing:
- Number of hours worked
- Number of appointments booked, made, and canceled
- Number of distinct clients received, and number of new clients
- Top 3 most popular services
- Revenue in EUR (total and per service type)
- Revenue per hour worked

## Job kinds

- **Periodic (scheduled)** — reminders, birthday messages, and monthly reports
  run on a cron schedule via Procrastinate periodic tasks.
- **Deferred (event-driven)** — booking confirmations and BO alerts (waitlist
  joins, custom requests) are enqueued from services when the event happens.

## Conventions

- Tasks must be **idempotent** and define explicit retry/timeout policies
  (see `coding-standards.md`).
- Tasks contain no business logic — they call services/selectors.
- Notifications respect each client's preferred channel.
- No Redis: the queue uses the existing PostgreSQL database.
