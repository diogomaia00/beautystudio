import type { NotificationChannel } from "@/features/auth/types";

/** A client as listed in the back office. */
export interface Client {
  id: string;
  msisdn: string;
  first_name: string;
  last_name: string;
  email: string;
  /** ISO date (YYYY-MM-DD). */
  birthday: string;
  preferred_channel: NotificationChannel;
  blacklisted: boolean;
  is_active: boolean;
}

/** Attendance counters derived from appointment status. */
export interface Attendance {
  booked: number;
  made: number;
  canceled: number;
  no_show: number;
}

/** A client plus their attendance history. */
export interface ClientDetail extends Client {
  attendance: Attendance;
}

/** A per-client duration override for a specific service. */
export interface ClientDuration {
  id: string;
  /** Service UUID. */
  service: string;
  service_name: string;
  duration_minutes: number;
}

/** Body for toggling a client's blacklist flag. */
export interface SetBlacklistInput {
  blacklisted: boolean;
}

/** Body for creating a per-client duration override. */
export interface CreateDurationInput {
  /** Service UUID. */
  service_id: string;
  duration_minutes: number;
}
