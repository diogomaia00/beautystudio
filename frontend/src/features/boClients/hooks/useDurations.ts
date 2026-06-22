import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createDuration, deleteDuration } from "../api/mutations";
import { fetchDurations } from "../api/queries";
import { boClientsKeys } from "../api/queryKeys";

export function useDurations(clientId: string | null) {
  return useQuery({
    queryKey: boClientsKeys.durations(clientId ?? ""),
    queryFn: () => fetchDurations(clientId ?? ""),
    staleTime: 30_000,
    enabled: Boolean(clientId),
  });
}

export function useCreateDuration(clientId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { service_id: string; duration_minutes: number }) =>
      createDuration(clientId, input.service_id, input.duration_minutes),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: boClientsKeys.durations(clientId),
      }),
  });
}

export function useDeleteDuration(clientId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (serviceId: string) => deleteDuration(clientId, serviceId),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: boClientsKeys.durations(clientId),
      }),
  });
}
