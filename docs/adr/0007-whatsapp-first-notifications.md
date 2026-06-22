# 0007. WhatsApp-first multi-channel notifications (retire Twilio)

- Status: Accepted
- Date: 2026-06-20
- Deciders: diogo

## Context

The app sends low-volume client notifications — appointment reminders (~24h
before), birthday messages, and seasonal campaigns — across PT, FR, CH, and (low
volume) BR. Expected volume is ~1.4k messages/year initially, ~8.5k at growth.

Twilio (the previous SMS/OTP provider — see ADR 0004) is built for high-volume,
omnichannel, bidirectional scenarios the app does not need. With WhatsApp planned
as the primary channel, Twilio would only be an intermediary in front of Meta's
infrastructure. The WhatsApp Cloud API lets us talk to Meta directly: lower cost,
fewer dependencies, less lock-in (templates live in our Meta account), and an
architecture matched to the real volume.

## Decision

Adopt a **channel cascade**: **WhatsApp (primary) → SMS (fallback) → email
(complementary)**, each on a best-fit provider:

- **WhatsApp Cloud API (Meta)** — primary. `integrations/whatsapp/`.
- **Telnyx** — SMS fallback **and** the login OTP transport. `integrations/telnyx/`.
- **Resend** — transactional email. `integrations/resend/`.

Twilio is removed (`integrations/twilio/` deleted, dependency dropped).

Delivery is implemented in `apps/notifications/services.py`: `_deliver()` walks
the cascade (a client's `preferred_channel` first, then
`NOTIFICATION_CHANNEL_PRIORITY`), attempts each provider, and on a real failure
falls back to the next channel. `NotificationLog.channel` records the channel
actually used.

**Login OTP stays SMS-only** (via Telnyx) — ADR 0004 is unchanged except for the
provider swap; the WhatsApp-first cascade applies to *notifications*, not the
auth code.

Each provider client keeps the existing **dev fallback**: when its credentials
are unset, it logs the message instead of sending, so OTP and notification flows
stay testable locally without any provider account.

**Scope of this change:** the architecture, routing, ADR, rules, and provider
*stubs* land now. Real provider wiring (HTTP calls / SDKs) is deferred until the
Meta WhatsApp Business account + approved templates, Telnyx, and Resend accounts
exist. The WhatsApp stub raises so delivery falls back to SMS until implemented.

## Consequences

- **Positive:** lower operational cost; fewer third-party margins; templates and
  send logic owned by us; easy to swap the SMS provider later without touching
  WhatsApp; architecture sized to actual volume.
- **Negative / risks:**
  - WhatsApp business-initiated messages require **pre-approved templates** in
    Meta Business Manager (reminders, birthday, campaigns) — an operational
    dependency with lead time, separate from the code.
  - Meta does not reliably indicate up front whether a number has WhatsApp;
    v1 fallback triggers on **send failure** (synchronous). Delivery-status
    webhooks for accurate fallback are roadmap.
  - Three integrations to operate instead of one all-in-one platform.
- **Neutral:** `preferred_channel` now defaults to `whatsapp` and may be any of
  whatsapp/sms/email; when set it is tried first, then the default cascade.

## Alternatives considered

- **Keep Twilio** (SMS + Twilio's WhatsApp): simplest, but pays platform margin
  for unused capabilities and keeps Meta behind an intermediary — rejected on
  cost/lock-in for this volume.
- **WhatsApp for OTP too:** viable via Meta's authentication template, but adds
  template-approval coupling to the login path for little benefit at this scale —
  deferred; OTP stays on SMS.
- **Single provider for all channels:** simpler ops, but no single low-cost
  provider fits WhatsApp + SMS + email well at this volume.

## Follow-ups

- Create + get approval for WhatsApp templates (reminder, birthday, campaign).
- Implement real sends in the three provider clients; add `telnyx` / `resend`
  SDKs (and HTTP for WhatsApp) to `requirements/`.
- Roadmap: WhatsApp delivery-status webhooks to drive accurate fallback.
