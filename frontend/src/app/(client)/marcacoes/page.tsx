import type { Metadata } from "next";

import PageHeader from "@/components/layouts/PageHeader";
import AppointmentsList from "@/features/appointments/components/AppointmentsList";

export const metadata: Metadata = {
  title: "Marcações — Beauty Studio",
};

export default function AppointmentsPage() {
  return (
    <div>
      <PageHeader
        title="Marcações"
        subtitle="As tuas marcações. Podes cancelar ou reagendar até 24h antes."
      />
      <AppointmentsList />
    </div>
  );
}
