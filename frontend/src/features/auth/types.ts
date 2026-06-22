export type Role = "admin" | "staff" | "client";
export type NotificationChannel = "whatsapp" | "sms" | "email";
export type OtpPurpose = "login" | "signup";

export interface CurrentUser {
  id: string;
  msisdn: string;
  role: Role;
  first_name: string;
  last_name: string;
  email: string;
  /** ISO date (YYYY-MM-DD) or null. */
  birthday: string | null;
  preferred_channel: NotificationChannel;
}

/** Extra fields required when verifying a sign-up OTP. */
export interface SignupData {
  first_name: string;
  last_name: string;
  email: string;
  /** ISO date (YYYY-MM-DD). */
  birthday: string;
}

export interface VerifyOtpInput extends Partial<SignupData> {
  msisdn: string;
  code: string;
  purpose: OtpPurpose;
}
