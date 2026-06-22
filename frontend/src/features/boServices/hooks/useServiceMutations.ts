import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createService, updateService } from "../api/mutations";
import { boServicesKeys } from "../api/queryKeys";
import type { CreateServiceInput, UpdateServiceInput } from "../types";

export function useCreateService() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateServiceInput) => createService(input),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: boServicesKeys.all }),
  });
}

export function useUpdateService(serviceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: UpdateServiceInput) => updateService(serviceId, input),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: boServicesKeys.all }),
  });
}
