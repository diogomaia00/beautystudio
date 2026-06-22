import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createDiscount, deleteDiscount } from "../api/mutations";
import { fetchDiscounts } from "../api/queries";
import { boServicesKeys } from "../api/queryKeys";
import type { CreateDiscountInput } from "../types";

export function useDiscounts(serviceId: string, enabled = true) {
  return useQuery({
    queryKey: boServicesKeys.discounts(serviceId),
    queryFn: () => fetchDiscounts(serviceId),
    staleTime: 30_000,
    enabled: enabled && Boolean(serviceId),
  });
}

export function useCreateDiscount(serviceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateDiscountInput) => createDiscount(serviceId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: boServicesKeys.discounts(serviceId),
      });
      // Effective prices may change once a discount becomes active.
      queryClient.invalidateQueries({ queryKey: boServicesKeys.all });
    },
  });
}

export function useDeleteDiscount(serviceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (discountId: string) => deleteDiscount(serviceId, discountId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: boServicesKeys.discounts(serviceId),
      });
      queryClient.invalidateQueries({ queryKey: boServicesKeys.all });
    },
  });
}
