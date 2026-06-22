import { useQuery } from "@tanstack/react-query";

import { fetchClients } from "../api/queries";
import { boClientsKeys } from "../api/queryKeys";

export function useClients(search = "") {
  return useQuery({
    queryKey: boClientsKeys.list(search),
    queryFn: () => fetchClients(search),
    staleTime: 30_000,
  });
}
