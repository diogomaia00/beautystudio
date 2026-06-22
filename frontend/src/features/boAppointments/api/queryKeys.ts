/** Stable query keys for the BO appointments (Agenda) feature. */
export const boAppointmentKeys = {
  all: ["bo-appointments"] as const,
  /** Appointments for one staff member on a given calendar day ("YYYY-MM-DD"). */
  list: (staffId: string, date: string) =>
    [...boAppointmentKeys.all, "list", staffId, date] as const,
};
