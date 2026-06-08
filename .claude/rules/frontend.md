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
