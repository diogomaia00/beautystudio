import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { cancelAppointment, rescheduleAppointment } from "../api/mutations";
import { fetchAppointments } from "../api/queries";
import { appointmentsKeys } from "../api/queryKeys";

export function useAppointments(status?: string) {
  return useQuery({
    queryKey: appointmentsKeys.list(status),
    queryFn: () => fetchAppointments(status),
    staleTime: 30_000,
  });
}

export function useCancelAppointment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: cancelAppointment,
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: appointmentsKeys.all }),
  });
}

export function useRescheduleAppointment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: rescheduleAppointment,
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: appointmentsKeys.all }),
  });
}
