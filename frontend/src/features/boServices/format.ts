const priceFormatter = new Intl.NumberFormat("pt-PT", {
  style: "currency",
  currency: "EUR",
});

const dateTimeFormatter = new Intl.DateTimeFormat("pt-PT", {
  timeZone: "Europe/Lisbon",
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

/** "Sob orçamento" for quote-only/null, else a localized EUR amount. */
export function formatPrice(value: string | null, isQuoteOnly: boolean): string {
  if (isQuoteOnly || value === null) return "Sob orçamento";
  const amount = Number(value);
  if (Number.isNaN(amount)) return "Sob orçamento";
  return priceFormatter.format(amount);
}

/** "45 min" / "1 h 30 min" from a duration in minutes. */
export function formatDuration(min: number): string {
  if (min < 60) return `${min} min`;
  const hours = Math.floor(min / 60);
  const minutes = min % 60;
  return minutes === 0 ? `${hours} h` : `${hours} h ${minutes} min`;
}

/** Discount window as a localized pt-PT range (Europe/Lisbon). */
export function formatDateRange(startsAt: string, endsAt: string): string {
  return `${dateTimeFormatter.format(new Date(startsAt))} – ${dateTimeFormatter.format(
    new Date(endsAt),
  )}`;
}
