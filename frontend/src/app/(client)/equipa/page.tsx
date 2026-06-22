import type { Metadata } from "next";

import PageHeader from "@/components/layouts/PageHeader";
import StaffDirectory from "@/features/staff/components/StaffDirectory";

export const metadata: Metadata = {
  title: "Equipa — Beauty Studio",
};

export default function StaffPage() {
  return (
    <div>
      <PageHeader
        title="Equipa"
        subtitle="Conhece quem cuida de ti. Fotografias e apresentação — em breve."
      />
      <StaffDirectory />
    </div>
  );
}
