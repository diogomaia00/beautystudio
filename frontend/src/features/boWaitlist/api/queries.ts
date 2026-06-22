import { boApiClient } from "@/lib/api";

import type {
  CustomRequest,
  CustomRequestStatus,
  WaitlistEntry,
  WaitlistStatus,
} from "../types";

export function fetchWaitlist({
  staffId,
  status,
}: {
  staffId: string;
  status: WaitlistStatus;
}): Promise<WaitlistEntry[]> {
  return boApiClient.get<WaitlistEntry[]>(
    `/availability/staff/${encodeURIComponent(staffId)}/waitlist/?status=${encodeURIComponent(status)}`,
  );
}

export function fetchCustomRequests({
  staffId,
  status,
}: {
  staffId: string;
  status: CustomRequestStatus;
}): Promise<CustomRequest[]> {
  return boApiClient.get<CustomRequest[]>(
    `/availability/staff/${encodeURIComponent(staffId)}/custom-requests/?status=${encodeURIComponent(status)}`,
  );
}
