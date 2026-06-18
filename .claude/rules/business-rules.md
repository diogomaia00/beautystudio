# BUSINESS RULES

Booking and scheduling requirements. The system is **time-based**, not slot-based (see `database.md`). 
These rules are enforced in the relevant app's service layer (see `ddd.md`) and covered by tests.

## Client accounts & roles

- Clients must have an **account to book**; they **self sign-up** and log in. (Roles and auth surfaces are defined in `auth.md`.)
- **Required sign-up fields:** first name, last name, birthday, email, phone number (MSISDN, E.164 — supports non-Portuguese numbers).
- The profile also stores the **preferred notification channel** (email or SMS); birthday powers the birthday message.
- Staff can also create/adjust client profiles in the BO (except personal info and contacts).

## Service catalog

- Each service is offered by exactly **one staff member** (e.g. nails/estética vs depilation laser).
- Services are grouped into **categories** (e.g. nails, depilation laser, estética, wellbeing).
- Each service has a price and a default **duration in minutes** (`duration_minutes`) — see Pricing and `database.md`.

## Staff profile & education

- Staff can record **formations** they've completed (type — formation, webinar, course, etc. — provider, date, description), shown on a **public staff page** so clients can see their experience.
- Managed by the staff member (and admin) in the BO.

## Booking limits

- Maximum appointments per client per **day**: 3.
- Maximum appointments per client per **week**: 3.
- These limits, the batch size, the booking horizon, and minimum notice are
  **configurable in `system_settings`** (see `database.md`); enforced in the
  service layer.

## Appointment batches

- Clients can create appointment batches.
- Each batch contains a maximum of 3 appointments.
- Batches still respect the per-day and per-week limits above.

## Booking confirmation

- Booking an available time within the **booking horizon** (`booking_horizon_days`, default 60) is **auto-confirmed** — no staff approval needed.
- Custom booking requests (beyond the horizon) are **not** auto-confirmed: the responsible staff member handles them in the BO (see below).
- Clients cannot book a time starting less than `minimum_notice_hours` (default 2h) from now.

## Cancellation & rescheduling

- Clients can cancel or reschedule **themselves up to 24h before** the appointment.
- Within 24h of the appointment, clients must contact the staff member directly (no self-service).
- Cancelling/rescheduling **frees that time** and triggers a waitlist notification to the responsible staff member (see Waitlist).
- **Reschedule** updates the appointment in place (new `start_at`/`end_at`, status stays `booked`); only a genuine cancellation sets `status = canceled` with a `cancel_reason` (`client`/`staff`). Reschedules are therefore never counted as cancellations in reports.

## No-shows

- Staff can mark an appointment as a **no-show** in the BO if the client didn't showed up.
- No-shows are **tracked for analytics/reporting only** — no automatic penalty or blocking in v1.

## Client attendance & blacklist

- Each client's **attendance history** is kept (made / canceled / no-show
  appointments, derived from appointment status) and surfaced in the BO client
  profile.
- There is **no striking system** — attendance never triggers an automatic
  penalty or block.
- Staff can manually **add or remove a client from a blacklist**. The client
  entity carries a `blacklisted` boolean flag (see `database.md`).
- A **blacklisted** client **cannot schedule new appointments through the app**;
  the booking service rejects their bookings with a clear message to contact the
  staff member directly (outside the app). Existing appointments are unaffected
  unless staff cancel them.
- Only **staff** can set or clear `blacklisted`.

## Staff availability

- Bookable times are **generated dynamically** from each staff member's **own weekly schedule** (`staff_schedules`) configured in the BO; nothing is stored as a fixed slot (see `database.md`).
- The calendar grid granularity is `booking_slot_minutes` (default 15).
- Staff can block **time-off / holidays** (`staff_time_off`, single days or ranges), removing that availability.
- Staff can define daily **break windows** (e.g. lunch) that are non-bookable.
- No automatic buffer/cleanup time is inserted between appointments in v1.

## Waitlist for occupied times

- Occupied times have a waitlist.
- When someone joins a waitlist, the staff member responsible for that service receives a notification in the Back Office (BO).
- The responsible staff member contacts the waitlisted person (outside the app) to decide whether to arrange a booking swap. No automatic offer in v1.

## Direct bookings and custom requests

- Clients can book directly for any available time within the **booking horizon** (`booking_horizon_days`, default 60).
- To book beyond the horizon, clients use a **custom booking request** specifying: preferred date, preferred time, desired service.
- The appointed staff member receives the custom request as a BO notification.

## Appointment duration per service and client

- Durations are measured in **minutes**; appointments are stored as a `start_at`/`end_at` timestamp range (see `database.md`).
- Each service has a default `duration_minutes`.
- In the BO the client profile can define a **per-client duration override** (in minutes) for a service, reflecting the time typically spent with that
  client; this changes the computed `end_at` when that client books.
- If the client doesn't have a custom duration in their profile, use the service default.
- **Nail services with Nail Art** automatically add extra minutes to the
  appointment duration (extending `end_at`):
  - +15 minutes (simple), or
  - +30 minutes (complex), depending on the selected Nail Art option.
  - Clients can only book nail art appointments but cant change them afterwards.
    - When trying to edit/change a pre-booked nail art appointment between simple <-> complex, a modal must appear.
      - The modal (with a close button) must have a message telling the client to talk directly with a staff member since only them can make this change.
  - Only staff can edit nail art appointments

## Pricing

- Prices and per-service durations (`duration_minutes`) are **configurable in the BO**, so they live in the database (the `services` app owns them) — not in code or `.env`.
- `prices_joao.py` and `prices_tiz.py` at the repo root are **seed data only**: 
  loaded once via a data migration / `seed_prices` command to populate the DB, after which the DB is the source of truth.
  See `docs/adr/0001-prices-in-database.md`.
- Money is stored in EUR with explicit precision (`DECIMAL(10,2)`) — never floats. 
- Durations are stored in **minutes** (`duration_minutes`).
- **Price on request.** The seed files use `-1` to mean "contactar tiz". Do NOT carry that magic number into the DB — model it explicitly with a nullable price plus an `is_quote_only` flag.
- **Price snapshot.** When an appointment is booked, copy the current price and duration onto the appointment. 
  Later BO price edits affect only future bookings and never rewrite past revenue (needed by the monthly report).
- **Seasonal discounts.** Staff/admin can set a time-bounded percentage discount on a service (BO); the effective (discounted) price is what gets snapshotted at booking time.

---

## ROADMAP (not in v1)

Items captured from planning notes; not part of the initial build.

- **Google Calendar** — connect the BO to staff Google Calendars; associate each confirmed appointment with the staff member's calendar.
- **WhatsApp notifications** — staff will MSISDN so that by 2027 it is the number used for bookings. 
  Planned message:
  - Service reminder: "Relembramos [service_friendly_name] amanhã às [service_hours]".
    - to be sent on the day before the service
  - Birthday greeting: "A equipa Beauty Studio deseja-te um feliz aniversário. Obrigado pela confiança ❤️"
    - to be sent at the client birthday at 11h
  - Christmas greeting: "A equipa Beauty Studio deseja-te um feliz natal. Com muitas prendas, sonhos e sobretudo unhas natalícias 😊"
    -  to be sent at 24th december at 16h
  - New Year greeting: "Bom [next_civil_year]! Desejamos-te um ano cheio de unhas bonitas e pele bem cuidada. Que continues a confiar em nós 🤞🏼"
    - to be sent in the first day of the year at 13h
- **MBWay payments** — nice-to-have online payment (see `payments` app in the backend roadmap).
