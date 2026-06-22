import { boApiClient } from "@/lib/api";

import type { MonthlyReport } from "../types";

/**
 * List generated reports. Admins must pass `staffId`; staff omit it (the
 * backend scopes to their own id and ignores the query param).
 */
export function fetchReports(staffId?: string): Promise<MonthlyReport[]> {
  const query = staffId ? `?staff_id=${encodeURIComponent(staffId)}` : "";
  return boApiClient.get<MonthlyReport[]>(`/reports/${query}`);
}

/** Fetch a single report by id. */
export function fetchReport(id: string): Promise<MonthlyReport> {
  return boApiClient.get<MonthlyReport>(`/reports/${id}/`);
}
