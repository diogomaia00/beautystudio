import { useQuery } from "@tanstack/react-query";

import { fetchBoServices } from "../api/queries";
import type { BoServiceFilters } from "../api/queryKeys";
import { boServicesKeys } from "../api/queryKeys";

export function useBoServices(filters: BoServiceFilters = {}) {
  return useQuery({
    queryKey: boServicesKeys.list(filters),
    queryFn: () => fetchBoServices(filters),
    staleTime: 30_000,
  });
}
