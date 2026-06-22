import { useQuery } from "@tanstack/react-query";

import { fetchStaff } from "../api/queries";
import { staffKeys } from "../api/queryKeys";

export function useStaff(enabled = true) {
  return useQuery({
    queryKey: staffKeys.list(),
    queryFn: fetchStaff,
    staleTime: 5 * 60_000,
    enabled,
  });
}
