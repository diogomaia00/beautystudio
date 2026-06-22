import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { setBlacklist } from "../api/mutations";
import { fetchClient } from "../api/queries";
import { boClientsKeys } from "../api/queryKeys";

export function useClient(id: string | null) {
  return useQuery({
    queryKey: boClientsKeys.detail(id ?? ""),
    queryFn: () => fetchClient(id ?? ""),
    staleTime: 30_000,
    enabled: Boolean(id),
  });
}

export function useSetBlacklist(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (blacklisted: boolean) => setBlacklist(id, blacklisted),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: boClientsKeys.detail(id) });
      // The list shows the same blacklist/state badge.
      queryClient.invalidateQueries({ queryKey: boClientsKeys.all });
    },
  });
}
