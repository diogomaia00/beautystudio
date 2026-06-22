export interface BoServiceFilters {
  categoryId?: string;
  staffId?: string;
  activeOnly?: boolean;
}

export const boServicesKeys = {
  all: ["bo", "services"] as const,
  list: (filters: BoServiceFilters = {}) =>
    [
      ...boServicesKeys.all,
      "list",
      filters.categoryId ?? "all",
      filters.staffId ?? "all",
      filters.activeOnly ?? false,
    ] as const,
  discounts: (serviceId: string) =>
    [...boServicesKeys.all, "discounts", serviceId] as const,
};
