import { useQuery } from "@tanstack/react-query";

import { fetchReport } from "../api/queries";
import { boReportsKeys } from "../api/queryKeys";

/** Fetch a single report's detail. Disabled while `id` is null. */
export function useReport(id: string | null) {
  return useQuery({
    queryKey: boReportsKeys.detail(id ?? ""),
    queryFn: () => fetchReport(id ?? ""),
    staleTime: 60_000,
    enabled: !!id,
  });
}
