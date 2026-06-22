const eurFormatter = new Intl.NumberFormat("pt-PT", {
  style: "currency",
  currency: "EUR",
});

/** Decimal string price → "17,50 €"; null/quote-only → "Sob consulta". */
export function formatPrice(price: string | null, isQuoteOnly = false): string {
  if (isQuoteOnly || price === null) return "Sob consulta";
  const value = Number(price);
  if (Number.isNaN(value)) return "Sob consulta";
  return eurFormatter.format(value);
}

/** Minutes → "15 min", "1h", "1h15", "2h30". */
export function formatDuration(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours === 0) return `${mins} min`;
  if (mins === 0) return `${hours}h`;
  return `${hours}h${String(mins).padStart(2, "0")}`;
}
