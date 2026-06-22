export const servicesKeys = {
  all: ["services"] as const,
  categories: () => [...servicesKeys.all, "categories"] as const,
  list: (categoryId?: string) =>
    [...servicesKeys.all, "list", categoryId ?? "all"] as const,
};
