import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { fetchAlerts } from "../api/queries";
import { markAlertRead } from "../api/mutations";
import { alertKeys } from "../api/queryKeys";

/** In-app BO alerts, optionally limited to unread. */
export function useAlerts(unreadOnly: boolean) {
  return useQuery({
    queryKey: alertKeys.list(unreadOnly),
    queryFn: () => fetchAlerts(unreadOnly),
    staleTime: 30_000,
  });
}

/** Mark an alert as read; invalidates all alert lists. */
export function useMarkAlertRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => markAlertRead(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: alertKeys.all });
    },
  });
}
