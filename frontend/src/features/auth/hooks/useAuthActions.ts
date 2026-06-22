import { useMutation, useQueryClient } from "@tanstack/react-query";

import { logout, requestOtp, verifyOtp } from "../api/mutations";
import { authKeys } from "../api/queryKeys";
import type { CurrentUser } from "../types";

export function useRequestOtp() {
  return useMutation({ mutationFn: requestOtp });
}

export function useVerifyOtp() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: verifyOtp,
    onSuccess: (user) => {
      // Seed + refresh the session user so the UI updates immediately.
      queryClient.setQueryData<CurrentUser>(authKeys.currentUser(), user);
      queryClient.invalidateQueries({ queryKey: authKeys.currentUser() });
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: logout,
    onSuccess: () => {
      queryClient.setQueryData(authKeys.currentUser(), null);
      queryClient.invalidateQueries({ queryKey: authKeys.currentUser() });
    },
  });
}
