import { boApiClient } from "@/lib/api";

import type { BoAlert } from "../types";

export function markAlertRead(id: string): Promise<BoAlert> {
  return boApiClient.post<BoAlert>(
    `/notifications/alerts/${encodeURIComponent(id)}/read/`,
  );
}
