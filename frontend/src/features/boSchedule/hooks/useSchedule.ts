import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { fetchSchedule } from "../api/queries";
import { replaceSchedule } from "../api/mutations";
import { scheduleKeys } from "../api/queryKeys";
import type { ScheduleEntryInput } from "../types";

/** Weekly schedule for the active staff member. */
export function useSchedule(staffId: string | null) {
  return useQuery({
    queryKey: scheduleKeys.schedule(staffId ?? ""),
    queryFn: () => fetchSchedule(staffId as string),
    enabled: !!staffId,
    staleTime: 60_000,
  });
}

/** Replace the whole weekly schedule (PUT). */
export function useReplaceSchedule(staffId: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (entries: ScheduleEntryInput[]) =>
      replaceSchedule(staffId as string, entries),
    onSuccess: () => {
      if (staffId) {
        void queryClient.invalidateQueries({
          queryKey: scheduleKeys.schedule(staffId),
        });
      }
    },
  });
}
