"use client";

import PageHeader from "@/components/layouts/PageHeader";
import { useActiveStaff } from "@/features/bo/shared/ActiveStaffContext";
import { EmptyState, LoadingState } from "@/features/bo/shared/States";
import panel from "@/features/bo/shared/panel.module.css";
import CustomRequestsSection from "@/features/boWaitlist/components/CustomRequestsSection";
import WaitlistSection from "@/features/boWaitlist/components/WaitlistSection";

export default function ListaEsperaPage() {
  const { staffId, isAdmin, isLoading } = useActiveStaff();

  return (
    <div className={panel.page}>
      <PageHeader
        title="Lista de espera"
        subtitle={
          isAdmin
            ? "Lista de espera e pedidos personalizados da equipa (escolhe o membro na barra lateral)."
            : "Lista de espera e pedidos personalizados dos teus serviços."
        }
      />

      {isLoading ? (
        <LoadingState />
      ) : !staffId ? (
        <EmptyState title="Sem equipa selecionada">
          Seleciona um membro da equipa para ver a lista de espera.
        </EmptyState>
      ) : (
        <>
          <WaitlistSection key={`waitlist-${staffId}`} staffId={staffId} />
          <CustomRequestsSection key={`custom-${staffId}`} staffId={staffId} />
        </>
      )}
    </div>
  );
}
