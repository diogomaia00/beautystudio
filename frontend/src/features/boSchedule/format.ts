/** Display formatters for the BO schedule feature (pt-PT, Europe/Lisbon). */

/** "HH:MM:SS" or "HH:MM" → "HH:MM". */
export function formatTime(t: string): string {
  const [h, m] = t.split(":");
  if (h === undefined || m === undefined) return t;
  return `${h.padStart(2, "0")}:${m.padStart(2, "0")}`;
}

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
