/**
 * Country dial codes for the phone field. The user picks a country (default
 * Portugal) and types only the national number; the form composes the E.164
 * MSISDN (`+<dial><national>`). Curated list — Portugal first, then the most
 * common origins for this clinic's clients, then alphabetical.
 */

export interface Country {
  /** ISO 3166-1 alpha-2 code (stable key). */
  iso: string;
  name: string;
  /** International dialing code, digits only (no `+`). */
  dial: string;
  flag: string;
}

export const COUNTRIES: Country[] = [
  { iso: "PT", name: "Portugal", dial: "351", flag: "🇵🇹" },
  { iso: "ES", name: "Espanha", dial: "34", flag: "🇪🇸" },
  { iso: "FR", name: "França", dial: "33", flag: "🇫🇷" },
  { iso: "GB", name: "Reino Unido", dial: "44", flag: "🇬🇧" },
  { iso: "DE", name: "Alemanha", dial: "49", flag: "🇩🇪" },
  { iso: "CH", name: "Suíça", dial: "41", flag: "🇨🇭" },
  { iso: "LU", name: "Luxemburgo", dial: "352", flag: "🇱🇺" },
  { iso: "BR", name: "Brasil", dial: "55", flag: "🇧🇷" },
  { iso: "BE", name: "Bélgica", dial: "32", flag: "🇧🇪" },
  { iso: "NL", name: "Países Baixos", dial: "31", flag: "🇳🇱" },
  { iso: "IE", name: "Irlanda", dial: "353", flag: "🇮🇪" },
  { iso: "IT", name: "Itália", dial: "39", flag: "🇮🇹" },
  { iso: "US", name: "Estados Unidos", dial: "1", flag: "🇺🇸" },
  { iso: "AD", name: "Andorra", dial: "376", flag: "🇦🇩" },
  { iso: "AO", name: "Angola", dial: "244", flag: "🇦🇴" },
  { iso: "AT", name: "Áustria", dial: "43", flag: "🇦🇹" },
  { iso: "CV", name: "Cabo Verde", dial: "238", flag: "🇨🇻" },
  { iso: "CA", name: "Canadá", dial: "1", flag: "🇨🇦" },
  { iso: "DK", name: "Dinamarca", dial: "45", flag: "🇩🇰" },
  { iso: "MZ", name: "Moçambique", dial: "258", flag: "🇲🇿" },
  { iso: "NO", name: "Noruega", dial: "47", flag: "🇳🇴" },
  { iso: "PL", name: "Polónia", dial: "48", flag: "🇵🇱" },
  { iso: "SE", name: "Suécia", dial: "46", flag: "🇸🇪" },
];

export const DEFAULT_COUNTRY: Country =
  COUNTRIES.find((c) => c.iso === "PT") ?? COUNTRIES[0];

/** Keep only digits. */
export function digitsOnly(value: string): string {
  return value.replace(/\D/g, "");
}

/**
 * Best-effort split of an E.164 number into (country, national). Matches the
 * country whose dial code is the longest prefix. Falls back to the default
 * country with the raw digits as the national part.
 */
export function parseE164(value: string | undefined): {
  country: Country;
  national: string;
} {
  const digits = digitsOnly(value ?? "");
  if (!digits) return { country: DEFAULT_COUNTRY, national: "" };

  const matches = COUNTRIES.filter((c) => digits.startsWith(c.dial)).sort(
    (a, b) => b.dial.length - a.dial.length,
  );
  if (matches.length > 0) {
    const country = matches[0];
    return { country, national: digits.slice(country.dial.length) };
  }
  return { country: DEFAULT_COUNTRY, national: digits };
}

/** Compose an E.164 MSISDN from a country + national number (empty when blank). */
export function composeE164(country: Country, national: string): string {
  const nat = digitsOnly(national);
  return nat ? `+${country.dial}${nat}` : "";
}
