# 0004. SMS OTP login for all roles

- Status: Accepted
- Date: 2026-06-17
- Deciders: Diogo

> **Note (2026-06-20, ADR 0007):** the SMS-OTP decision stands; only the SMS
> provider changed from Twilio to **Telnyx**. Login OTP remains SMS-only — the
> WhatsApp-first cascade introduced in ADR 0007 applies to notifications, not the
> auth code.

## Context

The client app is mobile-first and every user already provides a verified
`msisdn` (E.164). We standardized on Django session auth under one domain
(ADR 0002); this ADR fixes how credentials are *verified* before a session is
created. Passwords add friction (especially on mobile) and another secret to
manage.

## Decision

All roles (client, staff, admin) log in to the **app** (client app + BO) via a
**one-time code sent over SMS** to their `msisdn`; no passwords for app login.

- Codes live in `otp_code` (see `docs/db/entities.md`): only a **hash** is
  stored, with a short TTL (~5 min), single-use (`consumed_at`), and an
  `attempts` counter.
- Flow: request code (msisdn) → Twilio sends it → verify code → on success a
  Django **session** is established. Sign-up reuses the verify step
  (`purpose = signup`) to confirm the number.
- Code requests and verify attempts are **rate-limited** per msisdn/IP.
- Django's `/admin/` is inherently password-based, so the **admin superuser**
  keeps a password used only for `/admin/`; their *app* login is still OTP.

## Consequences

- Positive: passwordless, mobile-friendly; no password storage/reset flows for
  app users; reuses the already-verified phone number.
- Negative: every login costs an SMS (Twilio) and depends on SMS delivery;
  SMS OTP is vulnerable to SIM-swap; needs rate-limiting/anti-abuse and a
  fallback path if SMS fails.
- Neutral: OTP only verifies credentials — the session/cookie model (ADR 0002)
  is unchanged.

## Alternatives considered

- **Passwords for everyone.** Rejected: more friction on mobile, password
  management/reset overhead.
- **OTP for clients, passwords for staff/admin.** Rejected in favor of a single
  uniform flow; admin still keeps a password only for Django `/admin/`.
- **Email magic links.** Rejected: email isn't the identifier here and is
  slower/less reliable on mobile than SMS.
