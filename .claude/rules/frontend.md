# FRONTEND ARCHITECTURE (NEXT.JS + TYPESCRIPT)

## PURPOSE

* Next.js (App Router)
* React
* TypeScript
* TanStack Query
* FullCalendar

The frontend must be:

* Feature-based
* Responsive
* Accessible
* Maintainable
* Scalable
* Performance-oriented

---

# FRONTEND STRUCTURE

> **Topology (ADR 0005):** one Next.js app with two App-Router **route groups** —
> `(client)` for the booking app and `(bo)` for the back office. Served under one
> domain via NGINX (`/` → client, `/bo` → back office). See ADR 0005.

frontend/

src/

app/

```
(public routes)
login/
register/

(authenticated routes)
dashboard/
appointments/
services/
profile/
```

components/

```
ui/
layouts/
forms/
feedback/
```

features/

```
appointments/
services/
auth/
clients/
staff/
reports/
```

shared/

```
api/
hooks/
lib/
constants/
types/
utils/
```

styles/

public/

package.json
Dockerfile

---

# FEATURE-BASED ORGANIZATION

Organize code by business domain, not technical type.

Good:

features/

```
appointments/
services/
clients/
```

Bad:

components/
hooks/
api/
pages/

containing files from unrelated domains.

---

# FEATURE STRUCTURE

Each feature should follow:

features/appointments/

```
components/
hooks/
api/
types/
utils/

AppointmentCalendar.tsx
AppointmentForm.tsx
AppointmentList.tsx
```

Example:

features/appointments/

```
components/
    AppointmentCalendar.tsx
    AppointmentForm.tsx
    AppointmentList.tsx

hooks/
    useAppointments.ts
    useCreateAppointment.ts

api/
    queries.ts
    mutations.ts
    queryKeys.ts

types/
    appointment.types.ts
```

---

# NEXT.JS RULES

* Use App Router only.
* Prefer Server Components by default.
* Use Client Components only when interactivity is required.
* Keep client-side JavaScript minimal.
* Avoid unnecessary hydration.
* Use layouts to share UI structure.
* Use loading.tsx and error.tsx for route handling.
* Use Suspense where appropriate.
* Use dynamic imports for heavy components.
* Optimize bundle size continuously.
* Avoid duplicated data fetching.

---

# TYPESCRIPT RULES

* Enable strict mode.
* Avoid any.
* Define explicit interfaces for API contracts.
* Centralize shared types.
* Prefer type inference when obvious.
* Fail builds on TypeScript errors.
* Keep domain types strongly typed.

---

# TANSTACK QUERY RULES

TanStack Query is the source of truth for server state.

Do not duplicate server state inside:

* useState
* Context
* custom stores

Use:

* queries for reads
* mutations for writes

Requirements:

* Stable query keys
* Centralized query key definitions
* Explicit staleTime values
* Explicit cacheTime values
* Consistent loading states
* Consistent error states
* Strategic invalidation

Example:

features/appointments/api/

```
queryKeys.ts
queries.ts
mutations.ts
```

---

# STATE MANAGEMENT

Use the following hierarchy:

1. Server state → TanStack Query
2. URL state → URL/Search Params
3. Form state → React Hook Form
4. Local UI state → useState

Avoid global state unless truly necessary.

Do not introduce Redux, Zustand, or Context without justification.

---

# API ACCESS

Never perform fetch calls directly inside components.

Use:

shared/api/

or

feature/api/

layers.

Components should never know endpoint details.

Good:

AppointmentList
→ useAppointments()
→ queries.ts
→ API Client

Bad:

AppointmentList
→ fetch("/v1/appointments")

---

# FORMS

Use React Hook Form.

Requirements:

* Client validation
* Server validation
* Field-level errors
* Loading states
* Success feedback
* Error feedback
* Prevention of duplicate submissions

---

# FULLCALENDAR RULES

FullCalendar is a presentation layer only.

The backend scheduling engine is the source of truth.

Requirements:

* Always validate availability server-side
* Never trust frontend slot/availability validation (slots are generated dynamically server-side; appointments are start_at/end_at ranges in UTC)
* Refresh calendar after mutations
* Handle booking conflicts gracefully
* Support timezone-aware rendering
* Use lazy loading when possible

---

# BACKOFFICE FRONTEND

The back office lives in the **same Next.js app** as the client app, under a separate `(bo)` route group (the client app uses `(client)`).

Responsibilities:

* services management
* staff management
* client management
* pricing management
* schedules management
* availability management
* reporting

Both surfaces are served under one domain via NGINX (`/` → client, `/bo` → back office). See ADR 0005 for the topology decision.

---

# DESIGN SYSTEM

The frontend must follow a design system approach.
No component should introduce arbitrary values.
All styling must use design tokens in `tokens.css`.

**Tone:** Professional, Elegant, Friendly, Feminine
**Signature look:** crisp white surfaces, light-blue brand colors, soft-pink accent, and a confident **black contour** (1.5px) on interactive surfaces.
**Requirements:** clear labels and validation messages, helpful empty states, human-friendly success messages

---

# LAYOUT & GRID

Use a responsive grid system.

Breakpoints:

* Mobile: <768px
* Tablet: 768px–1024px
* Desktop: >1024px

Requirements:

* Mobile-first design
* Consistent container widths
* Predictable spacing
* Responsive layouts

Container widths & gutters:

| Breakpoint | Max width | Gutter | Columns |
|---|---|---|---|
| Mobile | fluid (100%) | 16px | 4 |
| Tablet | 720px | 24px | 8 |
| Desktop | 1120px | 32px | 12 |

> **IMPORTANT**
> Clients will use the app mainly through the mobile
> Staff will use the app mainly through iPad/tablet

---

# COLOR SYSTEM

## Brand

| Token | Role | HEX | oklch |
|---|---|---|---|
| `color/primary` | Primary | **#85CCFF** | oklch(0.82 0.085 240) |
| `color/secondary` | Secondary | **#3081B0** | oklch(0.59 0.105 245) |
| `color/accent` | Accent | **#FD86A2** | oklch(0.72 0.130 9) |

> Primary is light — always pair it with **ink (#14181C) text** on filled surfaces. 
> Secondary is deep enough for **white text**. 
> Accent is for highlights/tags only — use sparingly.

## Primary scale

| Step | HEX | Usage |
|---|---|---|
| 50 | #F0F8FF | Subtle fills, hover backgrounds |
| 100 | #DCEFFF | Tinted surfaces, sticky bars |
| 200 | #B5DEFF | Focus ring, selected tint |
| **300** | **#85CCFF** | **Primary — buttons, selected states** |
| 400 | #5DB2EE | Primary hover |
| 500 | #3D97D6 | Primary active |
| **600** | **#3081B0** | **Secondary — headings, links** |
| 700 | #29688E | Text on light, deep emphasis |
| 800 | #21506D | High-contrast text |
| 900 | #18394D | Maximum contrast |

## Accent scale

| Token | HEX | Usage |
|---|---|---|
| `accent/base` | #FD86A2 | Tag borders, highlights |
| `accent/tint` | #FFE4EA | Tag / badge backgrounds |
| `accent/text` | #C03A5B | Text/icon on accent tint |

## Semantic

| Token | Base | Tint (bg) | Text-on-tint | Usage |
|---|---|---|---|---|
| Success | #82CB9D | #ECF7F0 | #2E7D55 | Confirmations, saved states |
| Warning | #F39B3D | #FDF0E0 | #9A5B12 | Non-blocking cautions |
| Error | #E94550 | #FCE9EA | #B11E28 | Validation errors, destructive |
| Info | #8CC8F5 | #EAF4FD | #1F6FA8 | Neutral tips & notices |

## Neutral

| Token | HEX | Usage |
|---|---|---|
| `neutral/white` | #FFFFFF | Base surface |
| `neutral/surface` | #F7FAFD | App background (blue-tinted white) |
| `neutral/100` | #EDF1F5 | Disabled fill, dividers (subtle) |
| `neutral/200` | #DCE3EB | Borders, dividers |
| `neutral/300` | #C2CCD6 | Disabled border |
| `neutral/400` | #9AA6B2 | Disabled text, placeholder |
| `neutral/500` | #6B7681 | Secondary / muted text |
| `neutral/600` | #4A535C | Body text (secondary) |
| `neutral/700` | #2F363D | Body text |
| `neutral/800` | #1F242A | Headings |
| `neutral/ink` | #14181C | **Contour stroke**, primary text |

Requirements:

* Sufficient contrast (body text ≥ 4.5:1, large text ≥ 3:1)
* Accessible color combinations
* Consistent semantic usage

---

# STROKE & CONTOUR

The black contour is the system's signature. Apply consistently.

| Token | Value | Usage |
|---|---|---|
| `stroke/contour` | 1.5px solid #14181C | Buttons, cards, inputs, pills, badges |
| `stroke/divider` | 1.5px solid #DCE3EB | Section dividers, list separators |
| `stroke/accent` | 1.5px solid #FD86A2 | Accent tags only |

* Every interactive container gets a contour, never a borderless fill.
* Pair contour with a radius from the scale below — never a bare rectangle.

---

# TYPOGRAPHY

Font Family: **Jost**

| Token | Size | Weight | Line height | Notes |
|---|---|---|---|---|
| H1 | 48px | Bold (700) | 1.1 | Page titles |
| H2 | 36px | SemiBold (600) | 1.15 | Section titles |
| H3 | 30px | SemiBold (600) | 1.2 | Sub-sections |
| H4 | 24px | SemiBold (600) | 1.25 | Card titles |
| H5 | 20px | Medium (500) | 1.3 | Group headings |
| H6 | 18px | Medium (500) | 1.4 | Minor headings |
| Body | 16px | Regular (400) | 1.5 | Default text |
| Caption | 14px | Regular (400) | 1.45 | Helper / meta text |
| Label | 13px | Medium (500) | 1.3 | Form labels, eyebrows (uppercase, 0.06em tracking optional) |

* Minimum body size on mobile: 16px (prevents iOS input zoom).
* Use `text-wrap: pretty` / `balance` for headings.

---

# SPACING SCALE

Use only:

4px · 8px · 12px · 16px · 24px · 32px · 48px

Apply consistently to:

* Padding
* Margins
* Gaps
* Layout spacing

---

# SIZING & TOUCH TARGETS

| Token | Value | Usage |
|---|---|---|
| `target/min-mobile` | 44 × 44px | Minimum tap target (clients on mobile) |
| `target/min-tablet` | 48 × 48px | Staff on iPad |
| `control/height-sm` | 36px | Compact buttons / inputs |
| `control/height-md` | 44px | Default buttons / inputs |
| `control/height-lg` | 56px | Primary CTAs (e.g. CONTINUAR) |
| `icon/sm` `md` `lg` | 16 / 20 / 24px | Icon sizes |

---

# BORDER RADIUS

| Token | Value | Usage |
|---|---|---|
| Small | 4px | Badges, small tags |
| Medium | 8px | Buttons, inputs |
| Large | 16px | Cards, sheets |
| Pill | 999px | Chips, segmented toggles, "ENTRAR" pill |

Avoid arbitrary radius values.

---

# ELEVATION & SHADOW

Contours do most of the separation work; shadows stay subtle.

| Token | Value | Usage |
|---|---|---|
| `shadow/none` | none | Flat, on-surface elements |
| `shadow/sm` | 0 1px 2px rgba(20,24,28,0.08) | Resting cards |
| `shadow/md` | 0 4px 12px rgba(20,24,28,0.10) | Raised cards, dropdowns |
| `shadow/lg` | 0 12px 32px rgba(20,24,28,0.14) | Modals, sheets |
| `overlay/scrim` | rgba(20,24,28,0.50) | Behind modals |

---

# ICONS

Library: **Material Design Icons**

Requirements:

* Prefer outline variants
* Keep icon sizing consistent:
    - small: 16px
    - medium: 20px
    - large: 24px
* Use icons to support content, not replace it

---

# INTERACTION STATES

All interactive elements must define:

* Default
* Hover
* Focus
* Active
* Disabled
* Loading

Reference values (primary button):

| State | Fill | Text | Notes |
|---|---|---|---|
| Default | #85CCFF | #14181C | + contour |
| Hover | #5DB2EE | #14181C | |
| Focus | #85CCFF | #14181C | + focus ring |
| Active | #3D97D6 | #FFFFFF | |
| Disabled | #EDF1F5 | #9AA6B2 | contour #C2CCD6, opacity tokens below |
| Loading | #85CCFF | #14181C | spinner, controls disabled |

Token references:

* `focus/ring` → 0 0 0 3px #B5DEFF (offset by the contour)
* `opacity/disabled` → 0.45
* `opacity/hover-scrim` → 0.06 (overlay on subtle hovers)

No component should omit interaction states.

---

# MOTION & ANIMATION

Durations:

* Fast → 150ms (hover, small state changes)
* Standard → 250ms (most transitions)
* Slow → 400ms (sheets, page transitions)

Easing:

* `ease/standard` → cubic-bezier(0.2, 0, 0, 1)
* `ease/decelerate` → cubic-bezier(0, 0, 0, 1) (entering)
* `ease/accelerate` → cubic-bezier(0.3, 0, 1, 1) (exiting)

Requirements:

* Use subtle animations
* Avoid distracting effects
* Maintain responsiveness
* Respect `prefers-reduced-motion`

---

# Z-INDEX / LAYERING

| Token | Value |
|---|---|
| base | 0 |
| dropdown | 1000 |
| sticky (headers, bottom bars) | 1100 |
| overlay / scrim | 1200 |
| modal / sheet | 1300 |
| toast | 1400 |

---

# TOKEN NAMING

Use `category/role[-modifier]`, kebab-case:

* `color/primary`, `color/secondary`, `color/accent`
* `color/primary-300`, `neutral/500`
* `space/16`, `radius/large`, `shadow/md`, `text/h2`

Components reference semantic tokens, never raw hex.

---

# ACCESSIBILITY

Follow WCAG guidelines.

Requirements:

* Keyboard navigation
* Screen reader support
* Focus indicators
* Semantic HTML
* Accessible labels
* Sufficient color contrast
* Minimum touch targets

Accessibility is mandatory.

---

# PERFORMANCE

Requirements:

* Minimize client-side JavaScript
* Optimize images
* Optimize fonts
* Lazy-load heavy modules
* Avoid unnecessary re-renders
* Avoid waterfall requests
* Monitor Core Web Vitals

---

# SECURITY

* Never trust client validation
* Never expose secrets
* Protect authenticated routes
* Validate backend responses
* Sanitize user-generated content
* Enforce authorization server-side

---

# TESTING

Implement:

* Unit tests
* Component tests
* Integration tests
* End-to-end tests

Critical flows:

* Login
* Booking creation
* Booking cancellation
* Booking rescheduling
* Staff management
* Role permissions

---

# BOOKING-SYSTEM SPECIFIC RULES

* Backend is always the source of truth.
* Availability must always be revalidated.
* Handle concurrent booking conflicts gracefully.
* Use UTC internally.
* Convert dates only for display (Portugal timezone).
* Refresh affected schedules after mutations.
* Provide meaningful conflict messages.
* Prevent duplicate bookings whenever possible.
