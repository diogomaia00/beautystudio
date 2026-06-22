import { boApiClient } from "@/lib/api";

import type { BoAlert } from "../types";

export function fetchAlerts(unreadOnly: boolean): Promise<BoAlert[]> {
  return boApiClient.get<BoAlert[]>(
    `/notifications/alerts/?unread_only=${unreadOnly ? "true" : "false"}`,
  );
}
