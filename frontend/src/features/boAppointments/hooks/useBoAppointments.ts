import { useQuery } from "@tanstack/react-query";

import { fetchAppointments } from "../api/queries";
import { boAppointmentKeys } from "../api/queryKeys";
import type { BoAppointment } from "../types";

/** Build the [start, end] ISO-UTC window for a calendar day ("YYYY-MM-DD"). */
export function dayRange(date: string): { startAt: string; endAt: string } {
  return {
    startAt: new Date(`${date}T00:00:00`).toISOString(),
    endAt: new Date(`${date}T23:59:59`).toISOString(),
  };
}

/**
 * Appointments for the active staff member on the chosen day, sorted by
 * `start_at`. The query is disabled until a staff member is selected.
 */
export function useBoAppointments(staffId: string | null, date: string) {
  const { startAt, endAt } = dayRange(date);
  return useQuery({
    queryKey: boAppointmentKeys.list(staffId ?? "", date),
    queryFn: async () => {
      const items = await fetchAppointments({
        staffId: staffId as string,
        startAt,
        endAt,
      });
      return [...items].sort(
        (a, b) => new Date(a.start_at).getTime() - new Date(b.start_at).getTime(),
      ) as BoAppointment[];
    },
    enabled: !!staffId,
    staleTime: 15_000,
  });
}
