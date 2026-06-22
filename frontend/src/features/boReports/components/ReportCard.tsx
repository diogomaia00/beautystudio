"use client";

import ReportMetrics from "./ReportMetrics";
import { formatDateTime, monthLabel } from "../format";
import type { MonthlyReport } from "../types";

import panel from "@/features/bo/shared/panel.module.css";

/** A full report (period heading + metrics) shown inline or inside a modal. */
export default function ReportCard({ report }: { report: MonthlyReport }) {
  return (
    <div className={panel.card}>
      <div>
        <h3 className={panel.cardTitle}>
          {monthLabel(report.month)} de {report.year}
        </h3>
        <p className={panel.cardMeta}>
          Gerado em {formatDateTime(report.generated_at)}
        </p>
      </div>
      <ReportMetrics metrics={report.metrics} />
    </div>
  );
}
