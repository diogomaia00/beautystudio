import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { fetchWaitlist } from "../api/queries";
import { updateWaitlistStatus } from "../api/mutations";
import { waitlistKeys } from "../api/queryKeys";
import type { WaitlistStatus } from "../types";

/** Waitlist entries for the active staff member, filtered by status. */
export function useWaitlist(staffId: string | null, status: WaitlistStatus) {
  return useQuery({
    queryKey: waitlistKeys.waitlist(staffId ?? "", status),
    queryFn: () => fetchWaitlist({ staffId: staffId as string, status }),
    enabled: !!staffId,
    staleTime: 30_000,
  });
}

/** Advance a waitlist entry's status; invalidates the waitlist lists for this staff. */
export function useUpdateWaitlistStatus(staffId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: WaitlistStatus }) =>
      updateWaitlistStatus({ staffId: staffId as string, id, status }),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: [...waitlistKeys.all, "waitlist", staffId ?? ""],
      });
    },
  });
}
