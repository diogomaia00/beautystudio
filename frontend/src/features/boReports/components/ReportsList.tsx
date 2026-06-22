"use client";

import Button from "@/components/ui/Button";

import { formatDateTime, formatEur, monthLabel } from "../format";
import type { MonthlyReport } from "../types";

import panel from "@/features/bo/shared/panel.module.css";

interface ReportsListProps {
  reports: MonthlyReport[];
  onView: (report: MonthlyReport) => void;
}

/** Table of generated reports with a "Ver" action per row. */
export default function ReportsList({ reports, onView }: ReportsListProps) {
  return (
    <div className={panel.tableWrap}>
      <table className={panel.table}>
        <thead>
          <tr>
            <th>Período</th>
            <th>Receita total</th>
            <th>Marcações realizadas</th>
            <th>Gerado em</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {reports.map((report) => (
            <tr key={report.id}>
              <td>
                {monthLabel(report.month)} de {report.year}
              </td>
              <td>{formatEur(report.metrics.revenue_total)}</td>
              <td>{report.metrics.appointments.made}</td>
              <td>{formatDateTime(report.generated_at)}</td>
              <td>
                <div className={panel.actions}>
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={() => onView(report)}
                  >
                    Ver
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
