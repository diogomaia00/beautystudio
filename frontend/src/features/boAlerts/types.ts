/** Domain types for the in-app BO alerts feature. */

export type BoAlertType = "waitlist_join" | "custom_request";

/** An in-app back-office alert (e.g. a waitlist join or a custom request). */
export interface BoAlert {
  id: string;
  alert_type: BoAlertType;
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
}
