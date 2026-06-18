# AUTHENTICATION

Both surfaces — the client app and the back office (BO) — use **Django session authentication** (cookie-based). 
The project standardized on a single auth mechanism (see `docs/adr/0002-session-auth-single-domain.md`). Credentials are verified by **SMS OTP** for all roles; a successful code check establishes the session (see `docs/adr/0004-sms-otp-login.md`).

## Why one mechanism

- **Single domain:** nginx serves the client app, the BO, and the API under one registrable domain, so session cookies are first-party (no cross-origin cookie juggling).
- Cookies are `HttpOnly` + `Secure` + `SameSite` — the session id never reaches JavaScript, so XSS can't steal it.
- **Instant revocation:** logout and staff **blacklisting** take effect immediately by invalidating the server-side session (a JWT would stay valid until expiry). See `business-rules.md`.
- Sessions are stored in **PostgreSQL** (DB-backed) — no Redis/cache needed.

## Requirements

- DRF `SessionAuthentication` on the API.
- CSRF protection enabled; the SPA sends the CSRF token on unsafe methods.
- Enforce HTTPS so `Secure` cookies work in every environment.

## Login (SMS OTP)

All roles authenticate by a **one-time code sent via SMS** to their `msisdn` — no
passwords for app login.

1. User submits `msisdn`; the backend issues a short-lived code, stores only its
   **hash** in `otp_code` (TTL ~5 min), and sends the code via Twilio.
2. User submits the code; the backend verifies the hash, checks expiry and the
   attempts cap, marks it consumed, and **establishes the Django session**.
3. Sign-up uses the same verify step (`purpose = signup`): the code is tied to
   the submitted `msisdn` (no user yet — `otp_code.user_id` is NULL); on success
   the account is created/activated.

Security: codes are hashed at rest, single-use, short-TTL; code requests and
verify attempts are rate-limited per msisdn/IP to resist brute-force and
SMS-bombing. See `docs/adr/0004-sms-otp-login.md`.

## Django admin

Django's built-in `/admin/` site stays enabled as a low-level data tool for the **admin** role (the developer). It is **not** the BO API, and it is not used by the client app or the staff BO frontend. 
App login is OTP for all roles, but `/admin/` itself is password-based, so the admin superuser keeps a password used only there.

---

# AUTHORIZATION

Authorization is separate from authentication and enforced server-side.

- **Custom user model** with a `role` (admin / staff / client).
- Role/permission-based access control via DRF permission classes in `common/permissions.py`.
- Staff/admin-only actions (manage services, pricing, schedules, reports, no-show, blacklist) are gated by permissions regardless of how endpoints are routed.
- A **blacklisted** client is blocked from booking in the `appointments` service (see `business-rules.md`).
- `user.is_active` gates **login**; `staff.is_active` gates whether a staff member is **bookable/visible**. They're independent: a staff member can be hidden from booking while still able to log in, but if `user.is_active = false` they cannot log in at all.
- Endpoint routing: the client app uses `/v1/...`; the back office uses `/bo/v1/...` (see `backend.md`). Django's `/admin/` is separate.
