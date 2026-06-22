/** E.164-ish phone: optional +, leading non-zero digit, 7–15 digits (matches backend). */
export const MSISDN_PATTERN = /^\+?[1-9]\d{6,14}$/;

/** 6-digit OTP code (OTP_CODE_LENGTH on the backend). */
export const OTP_PATTERN = /^\d{6}$/;
