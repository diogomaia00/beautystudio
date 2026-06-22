"use client";

import { EmptyState } from "@/features/bo/shared/States";

import { formatEur } from "../format";
import type { ReportMetrics as ReportMetricsData } from "../types";

import panel from "@/features/bo/shared/panel.module.css";
import styles from "./reportMetrics.module.css";

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className={styles.stat}>
      <span className={styles.statLabel}>{label}</span>
      <span className={styles.statValue}>{value}</span>
    </div>
  );
}

/** Renders a single report's `metrics` as labelled stat blocks and breakdowns. */
export default function ReportMetrics({
  metrics,
}: {
  metrics: ReportMetricsData;
}) {
  const revenueEntries = Object.entries(metrics.revenue_by_service);

  return (
    <div className={panel.grid}>
      {/* Headline figures */}
      <div className={`${panel.grid} ${panel.grid3}`}>
        <Stat label="Horas trabalhadas" value={metrics.hours_worked} />
        <Stat
          label="Receita total"
          value={formatEur(metrics.revenue_total)}
        />
        <Stat
          label="Receita por hora"
          value={formatEur(metrics.revenue_per_hour)}
        />
      </div>

      {/* Appointment counts */}
      <div className={`${panel.grid} ${panel.grid2}`}>
        <Stat label="Marcações agendadas" value={metrics.appointments.booked} />
        <Stat label="Marcações realizadas" value={metrics.appointments.made} />
        <Stat label="Marcações canceladas" value={metrics.appointments.canceled} />
        <Stat label="Faltas (no-show)" value={metrics.appointments.no_show} />
        <Stat label="Clientes distintos" value={metrics.distinct_clients} />
        <Stat label="Clientes novos" value={metrics.new_clients} />
      </div>

      {/* Top services */}
      <section>
        <h4 className={styles.sectionTitle}>Serviços mais populares</h4>
        {metrics.top_services.length === 0 ? (
          <EmptyState title="Sem serviços realizados">
            Não há marcações realizadas neste período.
          </EmptyState>
        ) : (
          <ol className={styles.topList}>
            {metrics.top_services.map((item, index) => (
              <li key={item.service} className={styles.topItem}>
                <span className={styles.rank}>{index + 1}.</span>
                <span className={styles.topName}>{item.service}</span>
                <span className={styles.topCount}>
                  {item.count} {item.count === 1 ? "marcação" : "marcações"}
                </span>
              </li>
            ))}
          </ol>
        )}
      </section>

      {/* Revenue per service */}
      <section>
        <h4 className={styles.sectionTitle}>Receita por serviço</h4>
        {revenueEntries.length === 0 ? (
          <EmptyState title="Sem receita registada">
            Não há receita para este período.
          </EmptyState>
        ) : (
          <div className={panel.tableWrap}>
            <table className={panel.table}>
              <thead>
                <tr>
                  <th>Serviço</th>
                  <th>Receita</th>
                </tr>
              </thead>
              <tbody>
                {revenueEntries.map(([service, amount]) => (
                  <tr key={service}>
                    <td>{service}</td>
                    <td>{formatEur(amount)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
