import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createAppointment } from "../api/mutations";
import { appointmentsKeys } from "../api/queryKeys";

export function useCreateAppointment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createAppointment,
    onSuccess: () => {
      // The booked time is no longer available, and the client's list changed.
      queryClient.invalidateQueries({ queryKey: appointmentsKeys.all });
    },
  });
}
