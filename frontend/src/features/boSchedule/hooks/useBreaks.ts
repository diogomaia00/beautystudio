import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { fetchBreaks } from "../api/queries";
import { createBreak, deleteBreak } from "../api/mutations";
import { scheduleKeys } from "../api/queryKeys";
import type { BreakInput } from "../types";

/** Recurring break windows for the active staff member. */
export function useBreaks(staffId: string | null) {
  return useQuery({
    queryKey: scheduleKeys.breaks(staffId ?? ""),
    queryFn: () => fetchBreaks(staffId as string),
    enabled: !!staffId,
    staleTime: 60_000,
  });
}

function useInvalidateBreaks(staffId: string | null) {
  const queryClient = useQueryClient();
  return () => {
    if (staffId) {
      void queryClient.invalidateQueries({ queryKey: scheduleKeys.breaks(staffId) });
    }
  };
}

export function useCreateBreak(staffId: string | null) {
  const invalidate = useInvalidateBreaks(staffId);
  return useMutation({
    mutationFn: (input: BreakInput) => createBreak(staffId as string, input),
    onSuccess: invalidate,
  });
}

export function useDeleteBreak(staffId: string | null) {
  const invalidate = useInvalidateBreaks(staffId);
  return useMutation({
    mutationFn: (breakId: string) => deleteBreak(staffId as string, breakId),
    onSuccess: invalidate,
  });
}
