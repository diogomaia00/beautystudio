"use client";

import { useState } from "react";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Input from "@/components/ui/Input";
import Modal from "@/components/ui/Modal";
import panel from "@/features/bo/shared/panel.module.css";
import { apiErrorMessage } from "@/lib/api";

import type { AppointmentActions } from "../hooks/useAppointmentActions";
import type { BoAppointment } from "../types";

/** ISO UTC → "YYYY-MM-DDTHH:MM" in the browser's local time, for datetime-local. */
function toLocalInputValue(iso: string): string {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(
    d.getHours(),
  )}:${pad(d.getMinutes())}`;
}

interface RescheduleModalProps {
  appointment: BoAppointment;
  actions: AppointmentActions;
  onClose: () => void;
}

/** Reschedule a booked appointment to a new start (server re-validates conflicts). */
export default function RescheduleModal({
  appointment,
  actions,
  onClose,
}: RescheduleModalProps) {
  const { rescheduleMutation } = actions;
  const [value, setValue] = useState(() => toLocalInputValue(appointment.start_at));
  const [error, setError] = useState<string | null>(null);

  const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    if (!value) {
      setError("Indica a nova data e hora.");
      return;
    }
    const newStartAt = new Date(value).toISOString();
    rescheduleMutation.mutate(
      { id: appointment.id, new_start_at: newStartAt },
      {
        onSuccess: onClose,
        onError: (err) =>
          setError(apiErrorMessage(err, "Não foi possível remarcar.")),
      },
    );
  };

  return (
    <Modal title="Remarcar marcação" onClose={onClose}>
      <form onSubmit={onSubmit}>
        <Field
          label="Nova data e hora"
          htmlFor="reschedule-start"
          hint="A disponibilidade é revalidada no servidor."
          error={error ?? undefined}
        >
          <Input
            id="reschedule-start"
            type="datetime-local"
            value={value}
            invalid={!!error}
            onChange={(e) => setValue(e.target.value)}
          />
        </Field>
        <div className={panel.actions}>
          <Button type="submit" disabled={rescheduleMutation.isPending}>
            {rescheduleMutation.isPending ? "A remarcar…" : "Remarcar"}
          </Button>
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
        </div>
      </form>
    </Modal>
  );
}
