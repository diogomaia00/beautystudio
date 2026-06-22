/** A single entry in the top-3 most popular services list. */
export interface TopService {
  service: string;
  count: number;
}

/** Appointment counts by lifecycle status for the report period. */
export interface ReportAppointmentCounts {
  booked: number;
  made: number;
  canceled: number;
  no_show: number;
}

/**
 * The figures stored inside a {@link MonthlyReport}'s `metrics` JSON, computed by
 * the backend `analytics.compute_staff_monthly_metrics` selector.
 *
 * Monetary values arrive as decimal strings (EUR); use `formatEur` to display.
 */
export interface ReportMetrics {
  staff_id: string;
  year: number;
  month: number;
  /** Hours worked across `made` appointments (e.g. 12.5). */
  hours_worked: number;
  appointments: ReportAppointmentCounts;
  /** Distinct clients seen (`made` appointments). */
  distinct_clients: number;
  /** Of the distinct clients, how many were new this period. */
  new_clients: number;
  /** Up to three most popular services by `made` count. */
  top_services: TopService[];
  /** Total revenue as a decimal string, e.g. "320.00". */
  revenue_total: string;
  /** Revenue per service name, each a decimal string. */
  revenue_by_service: Record<string, string>;
  /** Revenue per hour worked (number, EUR). */
  revenue_per_hour: number;
}

/** A generated monthly report row from `GET /bo/v1/reports/`. */
export interface MonthlyReport {
  id: string;
  /** Staff member uuid. */
  staff: string;
  year: number;
  /** 1-12. */
  month: number;
  metrics: ReportMetrics;
  /** ISO datetime the report was last generated. */
  generated_at: string;
}

/** Body for `POST /bo/v1/reports/generate/`. */
export interface GenerateReportInput {
  year: number;
  /** 1-12. */
  month: number;
  /** Required for admin; omitted for staff (backend uses their own id). */
  staff_id?: string;
}
