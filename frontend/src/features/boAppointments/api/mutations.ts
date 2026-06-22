import { boApiClient } from "@/lib/api";

import type { BoAppointment, NailArtOption } from "../types";

function path(id: string, action: string): string {
  return `/appointments/${encodeURIComponent(id)}/${action}`;
}

/** Mark an appointment as attended (status → made). */
export function markMade(id: string): Promise<BoAppointment> {
  return boApiClient.post<BoAppointment>(path(id, "made/"));
}

/** Mark an appointment as a no-show. */
export function markNoShow(id: string): Promise<BoAppointment> {
  return boApiClient.post<BoAppointment>(path(id, "no-show/"));
}

/** Cancel an appointment (status → canceled, cancel_reason "staff"). */
export function cancel(id: string): Promise<BoAppointment> {
  return boApiClient.post<BoAppointment>(path(id, "cancel/"));
}

/** Reschedule an appointment to a new start (server re-validates conflicts). */
export function reschedule({
  id,
  new_start_at,
}: {
  id: string;
  new_start_at: string; // ISO UTC
}): Promise<BoAppointment> {
  return boApiClient.post<BoAppointment>(path(id, "reschedule/"), {
    new_start_at,
  });
}

/** Set/clear the nail-art option (staff-only edit). */
export function setNailArt({
  id,
  nail_art_option,
}: {
  id: string;
  nail_art_option: NailArtOption;
}): Promise<BoAppointment> {
  return boApiClient.patch<BoAppointment>(path(id, "nail-art/"), {
    nail_art_option,
  });
}
