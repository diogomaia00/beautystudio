# DOMAIN-DRIVEN DESIGN GUIDELINES

The backend follows a pragmatic, Django-flavored DDD. 
The goal is a clear service layer, thin views, and well-bounded apps — not heavyweight DDD ceremony. 
This complements `backend.md` (structure) and `naming-conventions.md`.

## Ubiquitous language

Use one vocabulary across code, DB, API, and UI. The canonical terms are in
`CLAUDE.md`: **admin, staff, clients**, plus **appointment, batch, service, availability, waitlist**. 
If product and code disagree on a term, fix the code — don't invent synonyms.

> A *slot* is a dynamically generated calendar unit (granularity
> `booking_slot_minutes`, default 15) and is **never stored** — see
> `database.md`.

## Bounded contexts = Django apps

Each app owns a slice of the domain and its data. Apps must stay decoupled.

- `users` — identity, roles (admin/staff/client), profiles, per-client duration override (minutes), staff-managed client `blacklisted` flag.
- `services` — services offered, categories, prices, durations (minutes), Nail Art add-on rules.
- `appointments` — bookings, batches, lifecycle (booked/made/canceled), limits.
- `availability` — staff schedules, dynamic slot generation, waitlist, custom requests.
- `notifications` — email/SMS/(WhatsApp) delivery, reminders, BO alerts.
- `analytics` — aggregated metrics that feed reporting.
- `reports` — monthly report generation for staff in the BO.

> Besides these bounded contexts there is one **infrastructure** app, `core`,
> which is *not* a domain context: it holds cross-cutting concerns (the
> `system_settings` singleton, health probes, request-id middleware). Domain apps
> read settings through `core`'s selectors, never its models. See ADR 0006.

> An app owns its models. Other apps never import those models directly — they call the owning app's `services`/`selectors` (anti-corruption boundary).

> **Pricing data is DB-owned.** Service prices/durations are configured in the
> BO and stored in the `services` app's tables (nullable price + `is_quote_only`
> for "price on request"). The `prices_*.py` files are seed data only. See
> `business-rules.md` and `docs/adr/0001-prices-in-database.md`.

## Layering

```
HTTP request
   │
   ▼
views.py        thin: auth check, deserialize (serializer), call service/selector, serialize response
   │
   ├── reads ──▶ selectors.py   pure query layer: ORM queries, no mutations, no side effects
   │
   └── writes ─▶ services.py    business logic & orchestration: validation, transactions, side effects
                     │
                     ├──▶ models.py        persistence (ORM)
                     ├──▶ tasks.py         enqueue async work (Procrastinate)
                     └──▶ integrations/    external systems (Google Calendar, WhatsApp, SMS, email)
```

### Rules

- **Views are thin.** No business rules. Validate via serializer → call one service or selector → return serialized result + correct status code.
- **Selectors = reads.** All querying lives here. No writes, no side effects. Name them `get_*` / `list_*`. Optimize joins here (`select_related`).
- **Services = writes & logic.** All mutations and business rules live here. Wrap multi-step operations in `transaction.atomic()`. 
  Enforce invariants (booking limits, batch size, no overlapping appointments, blacklisted clients cannot book) here, not in views or models.
- **Models = data + invariants.** Schema, constraints, simple computed properties, and `clean()`-style validation that is intrinsic to the entity.
  Keep cross-entity orchestration out of models.
- **Tasks = async wrappers.** Background tasks (Procrastinate) delegate to services; they don't contain business logic themselves. Make them idempotent.
- **Serializers = boundary shaping.** Input validation and output representation only — no business logic.

## Where business rules live

The rules in `business-rules.md` are enforced in the relevant app's **`services.py`**, covered by unit tests, and surfaced as clear API errors.

## Concurrency & integrity

Booking competes for the same time window. Creating and editing an appointment must run inside a transaction, re-check availability (no overlapping appointment for that staff member) under lock (e.g. `select_for_update`), and be idempotent so retries/double-submits don't double-book.

## Anti-patterns to avoid

- Fat models / fat views holding orchestration logic.
- Querying another app's tables directly across context boundaries.
- Business logic inside serializers, signals, or background-task bodies.
- Duplicated query logic outside selectors.
