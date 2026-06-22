import { boApiClient } from "@/lib/api";

import type {
  CustomRequest,
  CustomRequestStatus,
  WaitlistEntry,
  WaitlistStatus,
} from "../types";

export function updateWaitlistStatus({
  staffId,
  id,
  status,
}: {
  staffId: string;
  id: string;
  status: WaitlistStatus;
}): Promise<WaitlistEntry> {
  return boApiClient.patch<WaitlistEntry>(
    `/availability/staff/${encodeURIComponent(staffId)}/waitlist/${encodeURIComponent(id)}/`,
    { status },
  );
}

export function updateCustomRequestStatus({
  staffId,
  id,
  status,
}: {
  staffId: string;
  id: string;
  status: CustomRequestStatus;
}): Promise<CustomRequest> {
  return boApiClient.patch<CustomRequest>(
    `/availability/staff/${encodeURIComponent(staffId)}/custom-requests/${encodeURIComponent(id)}/`,
    { status },
  );
}
