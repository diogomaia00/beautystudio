export const boReportsKeys = {
  all: ["bo", "reports"] as const,
  list: (staffId?: string) =>
    [...boReportsKeys.all, "list", staffId ?? "self"] as const,
  detail: (id: string) => [...boReportsKeys.all, "detail", id] as const,
};
