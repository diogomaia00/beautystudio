import { useQuery } from "@tanstack/react-query";

import { fetchCategories, fetchServices } from "../api/queries";
import { servicesKeys } from "../api/queryKeys";

export function useCategories() {
  return useQuery({
    queryKey: servicesKeys.categories(),
    queryFn: fetchCategories,
    staleTime: 5 * 60_000,
  });
}

export function useServices(categoryId?: string) {
  return useQuery({
    queryKey: servicesKeys.list(categoryId),
    queryFn: () => fetchServices(categoryId),
    enabled: !!categoryId,
    staleTime: 5 * 60_000,
  });
}
