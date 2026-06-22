import { boApiClient } from "@/lib/api";

import type { GenerateReportInput, MonthlyReport } from "../types";

/** Generate (or regenerate) a monthly report for a period. */
export function generateReport(
  input: GenerateReportInput,
): Promise<MonthlyReport> {
  return boApiClient.post<MonthlyReport>("/reports/generate/", input);
}
