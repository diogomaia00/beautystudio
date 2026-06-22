import type { CustomRequestStatus, WaitlistStatus } from "../types";

/** Stable query keys for the BO waitlist + custom-requests feature, scoped by staff id. */
export const waitlistKeys = {
  all: ["bo-waitlist"] as const,
  waitlist: (staffId: string, status: WaitlistStatus) =>
    [...waitlistKeys.all, "waitlist", staffId, status] as const,
  customRequests: (staffId: string, status: CustomRequestStatus) =>
    [...waitlistKeys.all, "custom-requests", staffId, status] as const,
};
