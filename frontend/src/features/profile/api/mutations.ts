import type { CurrentUser, NotificationChannel } from "@/features/auth/types";
import { apiClient } from "@/lib/api";

export interface UpdateProfileInput {
  first_name: string;
  last_name: string;
  email: string;
  birthday: string;
  preferred_channel: NotificationChannel;
}

export function updateProfile(input: UpdateProfileInput): Promise<CurrentUser> {
  return apiClient.patch<CurrentUser>("/profile/", input);
}
