"use client";

import PageHeader from "@/components/layouts/PageHeader";
import { useActiveStaff } from "@/features/bo/shared/ActiveStaffContext";
import { EmptyState, LoadingState } from "@/features/bo/shared/States";
import panel from "@/features/bo/shared/panel.module.css";
import BreaksManager from "@/features/boSchedule/components/BreaksManager";
import ScheduleEditor from "@/features/boSchedule/components/ScheduleEditor";
import TimeOffManager from "@/features/boSchedule/components/TimeOffManager";

export default function HorariosPage() {
  const { staffId, isAdmin, isLoading } = useActiveStaff();

  return (
    <div className={panel.page}>
      <PageHeader
        title="Horários"
        subtitle={
          isAdmin
            ? "Horário semanal, pausas e ausências da equipa (escolhe o membro na barra lateral)."
            : "Define o teu horário semanal, pausas e ausências."
        }
      />

      {isLoading ? (
        <LoadingState />
      ) : !staffId ? (
        <EmptyState title="Sem equipa selecionada">
          Seleciona um membro da equipa para gerir os horários.
        </EmptyState>
      ) : (
        <>
          <ScheduleEditor key={`schedule-${staffId}`} staffId={staffId} />
          <BreaksManager key={`breaks-${staffId}`} staffId={staffId} />
          <TimeOffManager key={`timeoff-${staffId}`} staffId={staffId} />
        </>
      )}
    </div>
  );
}
