import { apiClient } from "@/lib/api";

import type { CurrentUser, OtpPurpose, VerifyOtpInput } from "../types";

export function requestOtp(input: { msisdn: string; purpose: OtpPurpose }) {
  return apiClient.post<{ detail: string }>("/auth/otp/request/", input);
}

export function verifyOtp(input: VerifyOtpInput) {
  return apiClient.post<CurrentUser>("/auth/otp/verify/", input);
}

export function logout() {
  return apiClient.post<void>("/auth/logout/");
}
