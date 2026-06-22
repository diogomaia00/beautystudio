/** Back-office "Agenda" domain types (appointments for a staff member on a day). */

export type AppointmentStatus = "booked" | "made" | "canceled" | "no_show";

export type NailArtOption = "simple" | "complex" | null;

/** Minimal service info embedded in a BO appointment payload. */
export interface BoAppointmentService {
  id: string;
  name: string;
  is_nail_service: boolean;
}

/** A back-office appointment, including who the client is. */
export interface BoAppointment {
  id: string;
  batch: string | null;
  client: string;
  /** Client's display name (full name, or msisdn if unnamed). */
  client_name: string;
  /** Client's phone number, so staff can reach them. */
  client_msisdn: string;
  staff: string;
  service: BoAppointmentService;
  status: AppointmentStatus;
  start_at: string; // ISO UTC
  end_at: string; // ISO UTC
  notes: string;
  nail_art_option: NailArtOption;
  has_nail_art: boolean;
  price_snapshot: string | null;
  is_quote_only_snapshot: boolean;
  duration_minutes_snapshot: number;
  cancel_reason: "client" | "staff" | null;
  created_at: string; // ISO UTC
}
