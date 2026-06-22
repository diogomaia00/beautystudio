"use client";

import { useMemo, useState } from "react";

import Button from "@/components/ui/Button";
import { apiErrorMessage } from "@/lib/api";

import { useRescheduleAppointment } from "../hooks/useAppointments";
import { useSlots } from "../hooks/useSlots";
import { formatSlotTime } from "../format";
import type { Appointment } from "../types";
import styles from "./BookingPanel.module.css";

const BOOKING_HORIZON_DAYS = 60;

function localYMD(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export default function RescheduleControl({
  appointment,
  onDone,
}: {
  appointment: Appointment;
  onDone: () => void;
}) {
  const [date, setDate] = useState("");
  const [selected, setSelected] = useState<string | null>(null);
  const reschedule = useRescheduleAppointment();

  const { minDate, maxDate } = useMemo(() => {
    const today = new Date();
    const max = new Date();
    max.setDate(max.getDate() + BOOKING_HORIZON_DAYS);
    return { minDate: localYMD(today), maxDate: localYMD(max) };
  }, []);

  const query = date
    ? {
        staffId: appointment.staff,
        serviceId: appointment.service.id,
        date,
        nailArt: appointment.nail_art_option,
      }
    : null;
  const slots = useSlots(query);

  const onConfirm = () => {
    if (!selected) return;
    reschedule.mutate(
      { id: appointment.id, new_start_at: selected },
      { onSuccess: onDone },
    );
  };

  return (
    <div className={styles.panel}>
      <div className={styles.section}>
        <label className={styles.sectionLabel} htmlFor={`re-date-${appointment.id}`}>
          Nova data
        </label>
        <input
          id={`re-date-${appointment.id}`}
          type="date"
          className={styles.dateInput}
          min={minDate}
          max={maxDate}
          value={date}
          onChange={(e) => {
            setDate(e.target.value);
            setSelected(null);
          }}
        />
      </div>

      {date && (
        <div className={styles.section}>
          <span className={styles.sectionLabel}>Horários disponíveis</span>
          {slots.isLoading && <p className={styles.status}>A procurar horários…</p>}
          {slots.isError && (
            <p className={styles.error}>Não foi possível carregar os horários.</p>
          )}
          {slots.data && slots.data.length === 0 && (
            <p className={styles.status}>Sem horários disponíveis neste dia.</p>
          )}
          {slots.data && slots.data.length > 0 && (
            <div className={styles.slots}>
              {slots.data.map((slot) => (
                <button
                  key={slot}
                  type="button"
                  className={styles.slot}
                  data-active={selected === slot || undefined}
                  onClick={() => setSelected(slot)}
                >
                  {formatSlotTime(slot)}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      <div className={styles.confirm}>
        {reschedule.isError && (
          <p className={styles.error}>{apiErrorMessage(reschedule.error)}</p>
        )}
        <div className={styles.actionsRow}>
          <Button size="sm" onClick={onConfirm} disabled={!selected || reschedule.isPending}>
            {reschedule.isPending ? "A reagendar…" : "Confirmar nova data"}
          </Button>
          <Button size="sm" variant="secondary" onClick={onDone}>
            Cancelar
          </Button>
        </div>
      </div>
    </div>
  );
}
