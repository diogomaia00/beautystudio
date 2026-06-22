import type { BadgeTone } from "@/features/bo/shared/Badge";

import type { AppointmentStatus, NailArtOption } from "./types";

const TIME_ZONE = "Europe/Lisbon";

const timeFormatter = new Intl.DateTimeFormat("pt-PT", {
  hour: "2-digit",
  minute: "2-digit",
  timeZone: TIME_ZONE,
});

/** "14:00–14:45" in Europe/Lisbon local time. */
export function formatTimeRange(start: string, end: string): string {
  return `${timeFormatter.format(new Date(start))}–${timeFormatter.format(
    new Date(end),
  )}`;
}

/** Human label for an appointment status. */
export function statusLabel(status: AppointmentStatus): string {
  switch (status) {
    case "booked":
      return "Marcada";
    case "made":
      return "Feita";
    case "no_show":
      return "Falta";
    case "canceled":
      return "Cancelada";
  }
}

/** Badge tone for an appointment status. */
export function statusTone(status: AppointmentStatus): BadgeTone {
  switch (status) {
    case "booked":
      return "info";
    case "made":
      return "success";
    case "no_show":
      return "warning";
    case "canceled":
      return "error";
  }
}

/** Human label for the nail-art option. */
export function nailArtLabel(option: NailArtOption): string {
  switch (option) {
    case "simple":
      return "Simples";
    case "complex":
      return "Complexa";
    default:
      return "Sem nail art";
  }
}

/** Format the snapshotted price: a "€" amount, "Sob consulta", or "—". */
export function formatPrice(
  snapshot: string | null,
  isQuoteOnly: boolean,
): string {
  if (isQuoteOnly) return "Sob consulta";
  if (snapshot === null) return "—";
  const amount = Number(snapshot);
  if (Number.isNaN(amount)) return snapshot;
  return new Intl.NumberFormat("pt-PT", {
    style: "currency",
    currency: "EUR",
  }).format(amount);
}
