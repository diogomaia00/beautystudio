import { boApiClient } from "@/lib/api";

import type { Client, ClientDuration } from "../types";

export function setBlacklist(id: string, blacklisted: boolean): Promise<Client> {
  return boApiClient.post<Client>(`/clients/${id}/blacklist/`, { blacklisted });
}

export function createDuration(
  clientId: string,
  serviceId: string,
  durationMinutes: number,
): Promise<ClientDuration> {
  return boApiClient.post<ClientDuration>(`/clients/${clientId}/durations/`, {
    service_id: serviceId,
    duration_minutes: durationMinutes,
  });
}

export function deleteDuration(
  clientId: string,
  serviceId: string,
): Promise<void> {
  // NOTE: the path uses the SERVICE id, not the duration row id.
  return boApiClient.delete<void>(`/clients/${clientId}/durations/${serviceId}/`);
}
