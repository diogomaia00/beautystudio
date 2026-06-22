import { apiClient } from "@/lib/api";

import type { StaffPublic } from "../types";

/** Public list of bookable staff with their education. */
export function fetchStaff(): Promise<StaffPublic[]> {
  return apiClient.get<StaffPublic[]>("/staff/");
}
