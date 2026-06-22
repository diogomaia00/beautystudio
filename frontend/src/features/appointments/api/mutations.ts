import { apiClient } from "@/lib/api";

import type { Appointment, CreateAppointmentInput } from "../types";

export function createAppointment(
  input: CreateAppointmentInput,
): Promise<Appointment> {
  return apiClient.post<Appointment>("/appointments/", input);
}

export function cancelAppointment(id: string): Promise<Appointment> {
  return apiClient.post<Appointment>(`/appointments/${id}/cancel/`);
}

export function rescheduleAppointment(input: {
  id: string;
  new_start_at: string;
}): Promise<Appointment> {
  return apiClient.post<Appointment>(`/appointments/${input.id}/reschedule/`, {
    new_start_at: input.new_start_at,
  });
}
