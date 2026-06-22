const MONTHS_PT = [
  "Janeiro",
  "Fevereiro",
  "Março",
  "Abril",
  "Maio",
  "Junho",
  "Julho",
  "Agosto",
  "Setembro",
  "Outubro",
  "Novembro",
  "Dezembro",
];

const eurFormatter = new Intl.NumberFormat("pt-PT", {
  style: "currency",
  currency: "EUR",
});

const dateTimeFormatter = new Intl.DateTimeFormat("pt-PT", {
  dateStyle: "long",
  timeStyle: "short",
});

/** pt-PT month name for a 1-12 month number. */
export function monthLabel(month: number): string {
  return MONTHS_PT[month - 1] ?? String(month);
}

/**
 * Format a EUR value (number or decimal string from the API) as pt-PT currency.
 * Non-numeric input falls back to "—".
 */
export function formatEur(value: number | string): string {
  const amount = typeof value === "string" ? Number(value) : value;
  if (!Number.isFinite(amount)) return "—";
  return eurFormatter.format(amount);
}

/** Format an ISO datetime as a pt-PT date + time. */
export function formatDateTime(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return dateTimeFormatter.format(date);
}
