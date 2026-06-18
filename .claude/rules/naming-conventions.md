# NAMING CONVENTIONS

Code-level naming. Branch and commit naming live in `git.md`. Domain terms
(admin, staff, clients) are defined in `CLAUDE.md` and must be used verbatim.

## Domain language (ubiquitous)

- Use **admin / staff / clients** everywhere in code, APIs, and UI copy.
- Never use customer, worker, user (in product copy), employee, etc.
- "appointment" for a single booking; "batch" for a group of appointments;
  "service" for an offered treatment. A "slot" is a dynamically generated calendar unit (granularity `booking_slot_minutes`, default 15), never stored (see `database.md`).

## Python / Django

- Modules & packages: `snake_case` (e.g. `appointment_services.py` — but prefer
  the standard per-app filenames in `backend.md`).
- Classes / Models: `PascalCase` (e.g. `Appointment`, `ServiceCategory`).
- Functions, methods, variables: `snake_case`.
- Constants & enums values: `UPPER_SNAKE_CASE`.
- Django models: singular noun (`Appointment`, not `Appointments`).
- Service functions: verb-first (`create_appointment`, `cancel_appointment`).
- Selector functions: `get_*` / `list_*` (`get_client_appointments`).
- Boolean fields/vars: `is_*` / `has_*` (`is_active`, `has_nail_art`), or a clear state adjective/past-participle where it reads naturally (`blacklisted`).
- Background tasks (Procrastinate): verb-first describing the job (`send_appointment_reminder`).

## Database (PostgreSQL)

- Tables: Django default (`<app>_<model>`, lowercase) unless overridden.
- Columns: `snake_case`.
- Foreign keys: `<entity>_id` (`staff_id`, `service_id`).
- Indexes/constraints: descriptive (`appointment_start_idx`).
- Money stored in a defined unit (EUR) with explicit precision (`DECIMAL(10,2)`) — never floats for currency.
- Timestamps: `*_at` columns are `TIMESTAMPTZ` in UTC (`start_at`, `end_at`, `created_at`, `updated_at`). Recurring clock times: `*_time` (`TIME`).
- Durations stored in **minutes** (`duration_minutes`, `INTEGER`) — never as slots. See `database.md` for the full column-type mapping.

## REST API

- Base paths versioned: client app `/v1/`, back office `/bo/v1/`.
- Resources are plural nouns: `v1/appointments/`, `v1/services/`.
- Nested where it clarifies ownership: `v1/clients/{id}/appointments/`.
- Use HTTP verbs for actions (GET/POST/PATCH/DELETE) — avoid verbs in paths.
- Query params `snake_case`; JSON body fields `snake_case` (match serializers).
- Path/identifiers: kebab-case is not used — stick to resource nouns + IDs.

## TypeScript / React / Next.js

- Components: `PascalCase`, one component per file (`AppointmentCalendar.tsx`).
- Hooks: `useCamelCase` (`useAppointments.ts`).
- Variables / functions: `camelCase`.
- Types / interfaces / enums: `PascalCase` (no `I` prefix).
- Constants: `UPPER_SNAKE_CASE`.
- Feature folders: `camelCase` or lowercase (`features/appointments/`).
- Next.js route segments (`app/`): lowercase, kebab-case if multi-word.
- API client modules: `api.ts` per feature; shared client in `lib/api.ts`.

## Files & folders

- Backend: `snake_case.py`, per-app filenames as defined in `backend.md`.
- Frontend: components `PascalCase.tsx`, hooks/utilities `camelCase.ts`.
- Docs/markdown: `kebab-case.md`.
- Tests: mirror the unit under test (`test_services.py`,
  `AppointmentForm.test.tsx`).

## Environment variables

- `UPPER_SNAKE_CASE`, grouped by concern (`POSTGRES_*`, `TWILIO_*`, `GOOGLE_CALENDAR_*`). 
- Placeholders documented in `.env.example`.
