import type { Service } from "@/features/services/types";
import { boApiClient } from "@/lib/api";

import type {
  CreateDiscountInput,
  CreateServiceInput,
  ServiceDiscount,
  UpdateServiceInput,
} from "../types";

export function createService(input: CreateServiceInput): Promise<Service> {
  return boApiClient.post<Service>("/services/", input);
}

export function updateService(
  serviceId: string,
  input: UpdateServiceInput,
): Promise<Service> {
  return boApiClient.patch<Service>(`/services/${serviceId}/`, input);
}

export function createDiscount(
  serviceId: string,
  input: CreateDiscountInput,
): Promise<ServiceDiscount> {
  return boApiClient.post<ServiceDiscount>(
    `/services/${serviceId}/discounts/`,
    input,
  );
}

export function deleteDiscount(
  serviceId: string,
  discountId: string,
): Promise<void> {
  return boApiClient.delete<void>(
    `/services/${serviceId}/discounts/${discountId}/`,
  );
}
