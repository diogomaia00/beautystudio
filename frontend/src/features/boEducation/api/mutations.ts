import { boApiClient } from "@/lib/api";
import type { StaffEducation } from "@/features/staff/types";

import type { CreateEducationInput, UpdateEducationInput } from "../types";

export function createEducation(
  staffId: string,
  input: CreateEducationInput,
): Promise<StaffEducation> {
  return boApiClient.post<StaffEducation>(
    `/staff/${staffId}/educations/`,
    input,
  );
}

export function updateEducation(
  staffId: string,
  id: string,
  input: UpdateEducationInput,
): Promise<StaffEducation> {
  return boApiClient.patch<StaffEducation>(
    `/staff/${staffId}/educations/${id}/`,
    input,
  );
}

export function deleteEducation(staffId: string, id: string): Promise<void> {
  return boApiClient.delete<void>(`/staff/${staffId}/educations/${id}/`);
}
