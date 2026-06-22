import { boApiClient } from "@/lib/api";

import type { Client, ClientDetail, ClientDuration } from "../types";

export function fetchClients(search = ""): Promise<Client[]> {
  const term = search.trim();
  const query = term ? `?search=${encodeURIComponent(term)}` : "";
  return boApiClient.get<Client[]>(`/clients/${query}`);
}

export function fetchClient(id: string): Promise<ClientDetail> {
  return boApiClient.get<ClientDetail>(`/clients/${id}/`);
}

export function fetchDurations(clientId: string): Promise<ClientDuration[]> {
  return boApiClient.get<ClientDuration[]>(`/clients/${clientId}/durations/`);
}
