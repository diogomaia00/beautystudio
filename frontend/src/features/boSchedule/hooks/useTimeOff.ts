import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { fetchTimeOff } from "../api/queries";
import { createTimeOff, deleteTimeOff } from "../api/mutations";
import { scheduleKeys } from "../api/queryKeys";
import type { TimeOffInput } from "../types";

/** Time-off periods for the active staff member. */
export function useTimeOff(staffId: string | null) {
  return useQuery({
    queryKey: scheduleKeys.timeOff(staffId ?? ""),
    queryFn: () => fetchTimeOff(staffId as string),
    enabled: !!staffId,
    staleTime: 60_000,
  });
}

function useInvalidateTimeOff(staffId: string | null) {
  const queryClient = useQueryClient();
  return () => {
    if (staffId) {
      void queryClient.invalidateQueries({ queryKey: scheduleKeys.timeOff(staffId) });
    }
  };
}

export function useCreateTimeOff(staffId: string | null) {
  const invalidate = useInvalidateTimeOff(staffId);
  return useMutation({
    mutationFn: (input: TimeOffInput) => createTimeOff(staffId as string, input),
    onSuccess: invalidate,
  });
}

export function useDeleteTimeOff(staffId: string | null) {
  const invalidate = useInvalidateTimeOff(staffId);
  return useMutation({
    mutationFn: (timeOffId: string) => deleteTimeOff(staffId as string, timeOffId),
    onSuccess: invalidate,
  });
}
