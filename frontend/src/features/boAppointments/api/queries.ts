import { boApiClient } from "@/lib/api";

import type { BoAppointment } from "../types";

interface FetchAppointmentsArgs {
  staffId: string;
  startAt: string; // ISO UTC
  endAt: string; // ISO UTC
}

/** All appointments for a staff member within a [startAt, endAt) window. */
export function fetchAppointments({
  staffId,
  startAt,
  endAt,
}: FetchAppointmentsArgs): Promise<BoAppointment[]> {
  const params = new URLSearchParams({
    staff_id: staffId,
    start_at: startAt,
    end_at: endAt,
  });
  return boApiClient.get<BoAppointment[]>(`/appointments/?${params.toString()}`);
}
