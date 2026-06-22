"use client";

import { useState } from "react";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Input from "@/components/ui/Input";
import PageHeader from "@/components/layouts/PageHeader";
import { useActiveStaff } from "@/features/bo/shared/ActiveStaffContext";
import { EmptyState, ErrorState, LoadingState } from "@/features/bo/shared/States";
import panel from "@/features/bo/shared/panel.module.css";
import AppointmentRow from "@/features/boAppointments/components/AppointmentRow";
import NailArtModal from "@/features/boAppointments/components/NailArtModal";
import RescheduleModal from "@/features/boAppointments/components/RescheduleModal";
import { useAppointmentActions } from "@/features/boAppointments/hooks/useAppointmentActions";
import { useBoAppointments } from "@/features/boAppointments/hooks/useBoAppointments";
import type { BoAppointment } from "@/features/boAppointments/types";

/** Today's date as "YYYY-MM-DD" in local time. */
function todayDate(): string {
  const d = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

type OpenModal =
  | { kind: "reschedule"; appointment: BoAppointment }
  | { kind: "nail-art"; appointment: BoAppointment }
  | null;

export default function AgendaPage() {
  const { staffId, isAdmin, isLoading: staffLoading } = useActiveStaff();
  const [date, setDate] = useState<string>(todayDate);
  const [modal, setModal] = useState<OpenModal>(null);

  const query = useBoAppointments(staffId, date);
  const actions = useAppointmentActions(staffId, date);

  const appointments = query.data ?? [];

  return (
    <div className={panel.page}>
      <PageHeader
        title="Agenda"
        subtitle={
          isAdmin
            ? "Marcações do dia (escolhe o membro da equipa na barra lateral)."
            : "As tuas marcações do dia."
        }
      />

      <div className={panel.toolbar}>
        <Field label="Dia" htmlFor="agenda-date">
          <Input
            id="agenda-date"
            type="date"
            value={date}
            onChange={(event) => setDate(event.target.value)}
          />
        </Field>
      </div>

      {staffLoading ? (
        <LoadingState />
      ) : !staffId ? (
        <EmptyState title="Sem equipa selecionada">
          Seleciona um membro da equipa para ver a agenda.
        </EmptyState>
      ) : query.isLoading ? (
        <LoadingState label="A carregar marcações…" />
      ) : query.isError ? (
        <ErrorState
          action={
            <Button type="button" variant="secondary" onClick={() => query.refetch()}>
              Tentar novamente
            </Button>
          }
        />
      ) : appointments.length === 0 ? (
        <EmptyState title="Sem marcações neste dia" />
      ) : (
        <div className={panel.tableWrap}>
          <table className={panel.table}>
            <thead>
              <tr>
                <th>Hora</th>
                <th>Cliente</th>
                <th>Serviço</th>
                <th>Estado</th>
                <th>Preço</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {appointments.map((appointment) => (
                <AppointmentRow
                  key={appointment.id}
                  appointment={appointment}
                  actions={actions}
                  onReschedule={(a) => setModal({ kind: "reschedule", appointment: a })}
                  onEditNailArt={(a) => setModal({ kind: "nail-art", appointment: a })}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modal?.kind === "reschedule" ? (
        <RescheduleModal
          appointment={modal.appointment}
          actions={actions}
          onClose={() => setModal(null)}
        />
      ) : null}

      {modal?.kind === "nail-art" ? (
        <NailArtModal
          appointment={modal.appointment}
          actions={actions}
          onClose={() => setModal(null)}
        />
      ) : null}
    </div>
  );
}
