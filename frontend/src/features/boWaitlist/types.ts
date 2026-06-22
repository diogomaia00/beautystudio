/** Domain types for the BO waitlist + custom-requests feature. */

export type WaitlistStatus = "waiting" | "contacted" | "closed";

/** A client waiting for an occupied time of a given service. */
export interface WaitlistEntry {
  id: string;
  client: string;
  client_msisdn: string;
  service: string;
  service_name: string;
  desired_start_at: string;
  status: WaitlistStatus;
  note: string;
  created_at: string;
}

export type CustomRequestStatus = "pending" | "accepted" | "rejected" | "closed";

/** A client request to book a service beyond the booking horizon. */
export interface CustomRequest {
  id: string;
  client: string;
  client_msisdn: string;
  service: string;
  service_name: string;
  preferred_date: string;
  preferred_time: string | null;
  status: CustomRequestStatus;
  note: string;
  created_at: string;
}
