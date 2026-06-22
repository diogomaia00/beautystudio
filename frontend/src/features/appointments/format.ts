const CLINIC_TZ = "Europe/Lisbon";

const timeFormatter = new Intl.DateTimeFormat("pt-PT", {
  hour: "2-digit",
  minute: "2-digit",
  timeZone: CLINIC_TZ,
});

const dateTimeFormatter = new Intl.DateTimeFormat("pt-PT", {
  weekday: "short",
  day: "2-digit",
  month: "long",
  hour: "2-digit",
  minute: "2-digit",
  timeZone: CLINIC_TZ,
});

/** ISO UTC → "14:30" in clinic local time. */
export function formatSlotTime(iso: string): string {
  return timeFormatter.format(new Date(iso));
}

/** ISO UTC → "qua, 02 julho, 14:30" in clinic local time. */
export function formatSlotDateTime(iso: string): string {
  return dateTimeFormatter.format(new Date(iso));
}
