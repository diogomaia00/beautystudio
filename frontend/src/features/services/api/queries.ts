import { apiClient } from "@/lib/api";

import type { Service, ServiceCategory } from "../types";

export function fetchCategories(): Promise<ServiceCategory[]> {
  return apiClient.get<ServiceCategory[]>("/services/categories/");
}

export function fetchServices(categoryId?: string): Promise<Service[]> {
  const query = categoryId ? `?category_id=${encodeURIComponent(categoryId)}` : "";
  return apiClient.get<Service[]>(`/services/${query}`);
}
