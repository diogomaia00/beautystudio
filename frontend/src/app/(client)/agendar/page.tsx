import type { Metadata } from "next";

import PageHeader from "@/components/layouts/PageHeader";
import SchedulingTabs from "@/features/services/components/SchedulingTabs";

export const metadata: Metadata = {
  title: "Agendar — Beauty Studio",
};

export default function SchedulingPage() {
  return (
    <div>
      <PageHeader
        title="Agendar"
        subtitle="Escolhe uma categoria para ver os serviços, preços e tempos."
      />
      <SchedulingTabs />
    </div>
  );
}
