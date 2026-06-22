import { useQuery } from "@tanstack/react-query";

import { fetchReports } from "../api/queries";
import { boReportsKeys } from "../api/queryKeys";

/**
 * List generated reports. For admins, pass the active `staffId` and gate via
 * `enabled`; staff omit it.
 */
export function useReports(staffId: string | undefined, enabled = true) {
  return useQuery({
    queryKey: boReportsKeys.list(staffId),
    queryFn: () => fetchReports(staffId),
    staleTime: 60_000,
    enabled,
  });
}
