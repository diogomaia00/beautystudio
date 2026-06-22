import { boApiClient } from "@/lib/api";

import type { Break, ScheduleEntry, TimeOff } from "../types";

export function fetchSchedule(staffId: string): Promise<ScheduleEntry[]> {
  return boApiClient.get<ScheduleEntry[]>(
    `/availability/staff/${encodeURIComponent(staffId)}/schedule/`,
  );
}

export function fetchBreaks(staffId: string): Promise<Break[]> {
  return boApiClient.get<Break[]>(
    `/availability/staff/${encodeURIComponent(staffId)}/breaks/`,
  );
}

export function fetchTimeOff(staffId: string): Promise<TimeOff[]> {
  return boApiClient.get<TimeOff[]>(
    `/availability/staff/${encodeURIComponent(staffId)}/time-off/`,
  );
}
