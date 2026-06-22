import { useMutation, useQueryClient } from "@tanstack/react-query";

import { authKeys } from "@/features/auth/api/queryKeys";
import type { CurrentUser } from "@/features/auth/types";

import { updateProfile } from "../api/mutations";

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateProfile,
    onSuccess: (user) => {
      queryClient.setQueryData<CurrentUser>(authKeys.currentUser(), user);
    },
  });
}
