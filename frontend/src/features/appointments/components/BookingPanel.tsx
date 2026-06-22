"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import Button from "@/components/ui/Button";
import { useCurrentUser } from "@/features/auth/hooks/useCurrentUser";
import type { Service } from "@/features/services/types";
import { apiErrorMessage } from "@/lib/api";

import { useCreateAppointment } from "../hooks/useCreateAppointment";
import { useSlots } from "../hooks/useSlots";
import { formatSlotDateTime, formatSlotTime } from "../format";
import type { NailArtOption } from "../types";
import styles from "./BookingPanel.module.css";

// Mirrors system_settings.booking_horizon_days default; server is the source of truth.
const BOOKING_HORIZON_DAYS = 60;

function localYMD(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

const NAIL_ART_CHOICES: { value: NailArtOption | null; label: string }[] = [
  { value: null, label: "Sem nail art" },
  { value: "simple", label: "Simples (+15 min)" },
  { value: "complex", label: "Complexa (+30 min)" },
];

export default function BookingPanel({ service }: { service: Service }) {
  const { data: user, isLoading: userLoading } = useCurrentUser();

  const [nailArt, setNailArt] = useState<NailArtOption | null>(null);
  const [date, setDate] = useState("");
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
  const [idemKey, setIdemKey] = useState("");

  const { minDate, maxDate } = useMemo(() => {
    const today = new Date();
    const max = new Date();
    max.setDate(max.getDate() + BOOKING_HORIZON_DAYS);
    return { minDate: localYMD(today), maxDate: localYMD(max) };
  }, []);

  const slotsQuery = date
    ? { staffId: service.staff.id, serviceId: service.id, date, nailArt }
    : null;
  const slots = useSlots(slotsQuery);
  const create = useCreateAppointment();

  if (userLoading) {
    return <p className={styles.status}>A carregar…</p>;
  }

  if (!user || user.role !== "client") {
    return (
      <div className={styles.gate}>
        <p>Inicia sessão como cliente para agendar.</p>
        <Button href="/login" size="sm">
          Entrar
        </Button>
      </div>
    );
  }

  if (create.isSuccess && selectedSlot) {
    return (
      <div className={styles.success} role="status">
        <p>
          ✅ Marcação confirmada — <strong>{service.name}</strong>,{" "}
          {formatSlotDateTime(selectedSlot)}.
        </p>
        <Button
          size="sm"
          variant="secondary"
          onClick={() => {
            create.reset();
            setSelectedSlot(null);
            setDate("");
          }}
        >
          Agendar outro
        </Button>
      </div>
    );
  }

  const onPickDate = (value: string) => {
    setDate(value);
    setSelectedSlot(null);
    create.reset();
  };

  const onPickNailArt = (value: NailArtOption | null) => {
    setNailArt(value);
    setSelectedSlot(null);
    create.reset();
  };

  const onSelectSlot = (slot: string) => {
    setSelectedSlot(slot);
    setIdemKey(crypto.randomUUID());
    create.reset();
  };

  const onConfirm = () => {
    if (!selectedSlot) return;
    create.mutate({
      service_id: service.id,
      start_at: selectedSlot,
      nail_art_option: nailArt,
      idempotency_key: idemKey,
    });
  };

  return (
    <div className={styles.panel}>
      {service.is_nail_service && (
        <div className={styles.section}>
          <span className={styles.sectionLabel}>Nail art</span>
          <div className={styles.choices}>
            {NAIL_ART_CHOICES.map((choice) => (
              <button
                key={choice.label}
                type="button"
                className={styles.choice}
                data-active={nailArt === choice.value || undefined}
                onClick={() => onPickNailArt(choice.value)}
              >
                {choice.label}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className={styles.section}>
        <label className={styles.sectionLabel} htmlFor={`date-${service.id}`}>
          Data
        </label>
        <input
          id={`date-${service.id}`}
          type="date"
          className={styles.dateInput}
          min={minDate}
          max={maxDate}
          value={date}
          onChange={(e) => onPickDate(e.target.value)}
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
                  data-active={selectedSlot === slot || undefined}
                  onClick={() => onSelectSlot(slot)}
                >
                  {formatSlotTime(slot)}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {selectedSlot && (
        <div className={styles.confirm}>
          {create.isError && (
            <p className={styles.error}>{apiErrorMessage(create.error)}</p>
          )}
          <p className={styles.confirmText}>
            Confirmar <strong>{service.name}</strong> em{" "}
            {formatSlotDateTime(selectedSlot)}?
          </p>
          <Button size="md" onClick={onConfirm} disabled={create.isPending}>
            {create.isPending ? "A confirmar…" : "Confirmar agendamento"}
          </Button>
        </div>
      )}
    </div>
  );
}
