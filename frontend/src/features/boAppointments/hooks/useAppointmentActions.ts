import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  cancel,
  markMade,
  markNoShow,
  reschedule,
  setNailArt,
} from "../api/mutations";
import { boAppointmentKeys } from "../api/queryKeys";
import type { BoAppointment, NailArtOption } from "../types";

/**
 * Lifecycle + edit mutations for the agenda. Every mutation invalidates the
 * day's list so the table refreshes after a change.
 */
export function useAppointmentActions(staffId: string | null, date: string) {
  const queryClient = useQueryClient();

  const invalidate = () => {
    if (staffId) {
      void queryClient.invalidateQueries({
        queryKey: boAppointmentKeys.list(staffId, date),
      });
    }
  };

  const markMadeMutation = useMutation<BoAppointment, unknown, string>({
    mutationFn: (id: string) => markMade(id),
    onSuccess: invalidate,
  });

  const markNoShowMutation = useMutation<BoAppointment, unknown, string>({
    mutationFn: (id: string) => markNoShow(id),
    onSuccess: invalidate,
  });

  const cancelMutation = useMutation<BoAppointment, unknown, string>({
    mutationFn: (id: string) => cancel(id),
    onSuccess: invalidate,
  });

  const rescheduleMutation = useMutation<
    BoAppointment,
    unknown,
    { id: string; new_start_at: string }
  >({
    mutationFn: reschedule,
    onSuccess: invalidate,
  });

  const setNailArtMutation = useMutation<
    BoAppointment,
    unknown,
    { id: string; nail_art_option: NailArtOption }
  >({
    mutationFn: setNailArt,
    onSuccess: invalidate,
  });

  return {
    markMadeMutation,
    markNoShowMutation,
    cancelMutation,
    rescheduleMutation,
    setNailArtMutation,
  };
}

export type AppointmentActions = ReturnType<typeof useAppointmentActions>;
