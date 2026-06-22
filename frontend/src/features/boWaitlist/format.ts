/** Display helpers for the BO waitlist + custom-requests feature (pt-PT, Europe/Lisbon). */

import type { BadgeTone } from "@/features/bo/shared/Badge";

import type { CustomRequestStatus, WaitlistStatus } from "./types";

/** ISO datetime → localized "dd/mm/aaaa, hh:mm" in Europe/Lisbon. */
export function formatDateTime(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return new Intl.DateTimeFormat("pt-PT", {
    timeZone: "Europe/Lisbon",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

/** "HH:MM:SS"/"HH:MM" → "HH:MM" (or "" for null). */
function formatClock(time: string | null): string {
  if (!time) return "";
  const [h, m] = time.split(":");
  if (h === undefined || m === undefined) return time;
  return `${h.padStart(2, "0")}:${m.padStart(2, "0")}`;
}

/** "YYYY-MM-DD" → "dd/mm/aaaa". */
function formatDate(date: string): string {
  const [y, m, d] = date.split("-");
  if (!y || !m || !d) return date;
  return `${d}/${m}/${y}`;
}

/** A preferred date with optional time, e.g. "01/07/2026 às 14:30" or "01/07/2026". */
export function formatPreferred(date: string, time: string | null): string {
  const clock = formatClock(time);
  const day = formatDate(date);
  return clock ? `${day} às ${clock}` : day;
}

// ------------------------------------------------------------
// Waitlist status labels + tones
// ------------------------------------------------------------

const WAITLIST_LABELS: Record<WaitlistStatus, string> = {
  waiting: "Em espera",
  contacted: "Contactado",
  closed: "Fechado",
};

const WAITLIST_TONES: Record<WaitlistStatus, BadgeTone> = {
  waiting: "info",
  contacted: "warning",
  closed: "neutral",
};

export function waitlistStatusLabel(status: WaitlistStatus): string {
  return WAITLIST_LABELS[status];
}

export function waitlistStatusTone(status: WaitlistStatus): BadgeTone {
  return WAITLIST_TONES[status];
}

// ------------------------------------------------------------
// Custom-request status labels + tones
// ------------------------------------------------------------

const CUSTOM_REQUEST_LABELS: Record<CustomRequestStatus, string> = {
  pending: "Pendente",
  accepted: "Aceite",
  rejected: "Recusado",
  closed: "Fechado",
};

const CUSTOM_REQUEST_TONES: Record<CustomRequestStatus, BadgeTone> = {
  pending: "info",
  accepted: "success",
  rejected: "error",
  closed: "neutral",
};

export function customRequestStatusLabel(status: CustomRequestStatus): string {
  return CUSTOM_REQUEST_LABELS[status];
}

export function customRequestStatusTone(status: CustomRequestStatus): BadgeTone {
  return CUSTOM_REQUEST_TONES[status];
}
