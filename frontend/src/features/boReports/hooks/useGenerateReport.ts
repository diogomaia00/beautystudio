import { useMutation, useQueryClient } from "@tanstack/react-query";

import { generateReport } from "../api/mutations";
import { boReportsKeys } from "../api/queryKeys";
import type { GenerateReportInput } from "../types";

/** Generate a report and refresh the list it belongs to. */
export function useGenerateReport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: GenerateReportInput) => generateReport(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: boReportsKeys.all });
    },
  });
}
