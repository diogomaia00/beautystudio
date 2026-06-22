import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { fetchCustomRequests } from "../api/queries";
import { updateCustomRequestStatus } from "../api/mutations";
import { waitlistKeys } from "../api/queryKeys";
import type { CustomRequestStatus } from "../types";

/** Custom booking requests for the active staff member, filtered by status. */
export function useCustomRequests(staffId: string | null, status: CustomRequestStatus) {
  return useQuery({
    queryKey: waitlistKeys.customRequests(staffId ?? "", status),
    queryFn: () => fetchCustomRequests({ staffId: staffId as string, status }),
    enabled: !!staffId,
    staleTime: 30_000,
  });
}

/** Set a custom request's status; invalidates the custom-request lists for this staff. */
export function useUpdateCustomRequestStatus(staffId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: CustomRequestStatus }) =>
      updateCustomRequestStatus({ staffId: staffId as string, id, status }),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: [...waitlistKeys.all, "custom-requests", staffId ?? ""],
      });
    },
  });
}
