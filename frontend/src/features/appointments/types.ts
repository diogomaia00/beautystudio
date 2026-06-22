export type NailArtOption = "simple" | "complex";

export type AppointmentStatus = "booked" | "made" | "canceled" | "no_show";

export interface Appointment {
  id: string;
  batch: string | null;
  client: string;
  staff: string;
  service: { id: string; name: string; is_nail_service: boolean };
  status: AppointmentStatus;
  start_at: string;
  end_at: string;
  notes: string;
  nail_art_option: NailArtOption | null;
  has_nail_art: boolean;
  price_snapshot: string | null;
  is_quote_only_snapshot: boolean;
  duration_minutes_snapshot: number;
  cancel_reason: string | null;
  created_at: string;
}

export interface CreateAppointmentInput {
  service_id: string;
  /** ISO-8601 UTC start time (from an available slot). */
  start_at: string;
  nail_art_option?: NailArtOption | null;
  notes?: string;
  idempotency_key?: string;
}

export interface SlotsQuery {
  staffId: string;
  serviceId: string;
  /** YYYY-MM-DD (local date). */
  date: string;
  nailArt?: NailArtOption | null;
}
