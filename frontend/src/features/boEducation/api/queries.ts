import { boApiClient } from "@/lib/api";
import type { StaffEducation } from "@/features/staff/types";

/** List a staff member's education entries. */
export function fetchEducations(staffId: string): Promise<StaffEducation[]> {
  return boApiClient.get<StaffEducation[]>(`/staff/${staffId}/educations/`);
}
