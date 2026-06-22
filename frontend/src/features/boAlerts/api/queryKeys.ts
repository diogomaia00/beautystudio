/** Stable query keys for the BO alerts feature. */
export const alertKeys = {
  all: ["bo-alerts"] as const,
  list: (unreadOnly: boolean) => [...alertKeys.all, "list", unreadOnly] as const,
};
