export const boClientsKeys = {
  all: ["bo", "clients"] as const,
  list: (search = "") => [...boClientsKeys.all, "list", search] as const,
  detail: (id: string) => [...boClientsKeys.all, "detail", id] as const,
  durations: (id: string) => [...boClientsKeys.all, "durations", id] as const,
};
