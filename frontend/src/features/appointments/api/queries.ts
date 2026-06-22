import { apiClient } from "@/lib/api";

import type { Appointment, SlotsQuery } from "../types";

/** Available start times (ISO-8601 UTC) for a staff + service + date. */
export async function fetchSlots(q: SlotsQuery): Promise<string[]> {
  const params = new URLSearchParams({
    staff_id: q.staffId,
    service_id: q.serviceId,
    date: q.date,
  });
  if (q.nailArt) params.set("nail_art", q.nailArt);
  const data = await apiClient.get<{ slots: string[] }>(
    `/availability/slots/?${params.toString()}`,
  );
  return data.slots;
}

export function fetchAppointments(status?: string): Promise<Appointment[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return apiClient.get<Appointment[]>(`/appointments/${query}`);
}
