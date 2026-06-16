FRONTEND STRUCTURE (NEXT.JS FEATURE-BASED)

frontend/

src/

app/

```
dashboard/
appointments/
services/
login/
```

components/

features/

```
appointments/
services/
auth/
```

lib/

```
api.ts
auth.ts
```

hooks/

styles/

public/

package.json
Dockerfile

---

FRONTEND FEATURE STRUCTURE RULES

Each feature folder should contain:

components
hooks
api client logic
UI containers

Example:

features/appointments/

AppointmentForm.tsx
AppointmentCalendar.tsx
AppointmentList.tsx
useAppointments.ts
api.ts

---

## Back Office Frontend

* Backoffice in a separated FE connected to the bo api to manage: 
    - services
    - clients
    - staff
    - prices
    - schedules
    - reports

---

## SYSTEM DESIGN

The frontend must follow a system design approach to maximize a cohesive appearance.

### System design components
#### layout & grid
    - Container widths
    - Grid system (12-column is common)
    - Breakpoints
    - Responsive behavior
        Example:
        - Mobile: <768px
        - Tablet: 768–1024px
        - Desktop: >1024px

#### sizing & scaling
    - consistent dimensions for components:
        - Buttons
        - Inputs
        - Cards
        - Icons
        - Avatars

#### typography
    - Font family - use Jost font 
    - Font sizes
    - Font weights
    - Line heights
    - Letter spacing
    - Text hierarchy (H1–H6, body, captions, labels)
        Example:
        - H1: 48px / Bold
        - H2: 36px / Semi-bold
        - Body: 16px / Regular

#### colors
    - Primary color
    - Secondary/accent colors
    - Neutral/grayscale palette
    - Semantic colors (success, warning, error, info)
    - Background colors
    - Text colors
        Example:
        - Primary: #2563EB
        - Success: #16A34A
        - Error: #DC2626

#### spacing
    4px
    8px
    12px
    16px
    24px
    32px
    48px
    Use these everywhere:
    - Padding
    - Margins
    - Gaps
    - Layout spacing

#### border radius
    Values:
    - Small: 4px
    - Medium: 8px
    - Large: 16px

#### icons
    - icon library: [material design icons](https://www.shadcn.io/icons/mdi)
    - prefer outline icons instead of filled icons

#### interaction states
    - Default
    - Hover
    - Focus
    - Active
    - Disabled
    - Loading

#### motion & animation
    - durations
    - easing curves
    - transition styles
    Values:
        - Fast: 150ms
        - Standard: 250ms
        - Slow: 400ms

#### content & language
    - feminine tone
    - button labels
    - error messages
    - empty states
    - success messages

#### accessibility
    - Contrast ratios
    - Keyboard navigation
    - Focus indicators
    - Screen reader support
    - Touch target sizes

