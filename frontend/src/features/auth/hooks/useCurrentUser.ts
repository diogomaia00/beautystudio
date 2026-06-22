import { useQuery } from "@tanstack/react-query";

import { fetchCurrentUser } from "../api/queries";
import { authKeys } from "../api/queryKeys";

/** Reads the current session user (null when logged out). */
export function useCurrentUser() {
  return useQuery({
    queryKey: authKeys.currentUser(),
    queryFn: fetchCurrentUser,
    staleTime: 60_000,
    retry: false,
  });
}
