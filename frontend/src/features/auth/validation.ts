/** E.164-ish phone: optional +, leading non-zero digit, 7–15 digits (matches backend). */
export const MSISDN_PATTERN = /^\+?[1-9]\d{6,14}$/;

/** 6-digit OTP code (OTP_CODE_LENGTH on the backend). */
export const OTP_PATTERN = /^\d{6}$/;

/** Minimum age to create an account (mirrors MIN_SIGNUP_AGE_YEARS on the backend). */
export const MIN_SIGNUP_AGE_YEARS = 12;

/** Today as YYYY-MM-DD (local) — used as the `max` on the birthday date input. */
export function todayISO(): string {
  const now = new Date();
  const offsetMs = now.getTimezoneOffset() * 60_000;
  return new Date(now.getTime() - offsetMs).toISOString().slice(0, 10);
}

/**
 * Validate a birthday (YYYY-MM-DD): not in the future and at least
 * `MIN_SIGNUP_AGE_YEARS` old. Returns `true` when valid, else an error message
 * (shape expected by react-hook-form's `validate`).
 */
export function validateBirthday(value: string): true | string {
  if (!value) return "Indica a tua data de nascimento.";
  const birthday = new Date(`${value}T00:00:00`);
  if (Number.isNaN(birthday.getTime())) return "Data inválida.";

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  if (birthday > today) return "A data de nascimento não pode ser no futuro.";

  let age = today.getFullYear() - birthday.getFullYear();
  const monthDay =
    today.getMonth() - birthday.getMonth() || today.getDate() - birthday.getDate();
  if (monthDay < 0) age -= 1;
  if (age < MIN_SIGNUP_AGE_YEARS) {
    return `É necessário ter pelo menos ${MIN_SIGNUP_AGE_YEARS} anos para criar conta.`;
  }
  return true;
}
