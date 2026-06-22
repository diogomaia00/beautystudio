import { apiClient, type ApiError } from "@/lib/api";

import type { CurrentUser } from "../types";

/** The authenticated user, or null when not logged in (401). */
export async function fetchCurrentUser(): Promise<CurrentUser | null> {
  try {
    return await apiClient.get<CurrentUser>("/auth/me/");
  } catch (error) {
    if ((error as ApiError).status === 401 || (error as ApiError).status === 403) {
      return null;
    }
    throw error;
  }
}
