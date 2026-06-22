import { useQuery } from "@tanstack/react-query";

import { fetchSlots } from "../api/queries";
import { appointmentsKeys } from "../api/queryKeys";
import type { SlotsQuery } from "../types";

/** Available slots for a service on a date. Disabled until a date is chosen. */
export function useSlots(query: SlotsQuery | null) {
  return useQuery({
    queryKey: query
      ? appointmentsKeys.slots(query)
      : [...appointmentsKeys.all, "slots", "idle"],
    queryFn: () => fetchSlots(query!),
    enabled: !!query,
    staleTime: 30_000,
  });
}
