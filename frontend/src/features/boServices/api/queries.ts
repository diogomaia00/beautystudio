import type { Service } from "@/features/services/types";
import { boApiClient } from "@/lib/api";

import type { ServiceDiscount } from "../types";
import type { BoServiceFilters } from "./queryKeys";

export function fetchBoServices(filters: BoServiceFilters = {}): Promise<Service[]> {
  const params = new URLSearchParams();
  if (filters.categoryId) params.set("category_id", filters.categoryId);
  if (filters.staffId) params.set("staff_id", filters.staffId);
  if (filters.activeOnly) params.set("active_only", "true");
  const query = params.toString();
  return boApiClient.get<Service[]>(`/services/${query ? `?${query}` : ""}`);
}

export function fetchDiscounts(serviceId: string): Promise<ServiceDiscount[]> {
  return boApiClient.get<ServiceDiscount[]>(`/services/${serviceId}/discounts/`);
}
