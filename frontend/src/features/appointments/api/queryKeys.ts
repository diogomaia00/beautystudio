import type { SlotsQuery } from "../types";

export const appointmentsKeys = {
  all: ["appointments"] as const,
  list: (status?: string) => [...appointmentsKeys.all, "list", status ?? "all"] as const,
  slots: (q: SlotsQuery) =>
    [
      ...appointmentsKeys.all,
      "slots",
      q.staffId,
      q.serviceId,
      q.date,
      q.nailArt ?? "none",
    ] as const,
};
