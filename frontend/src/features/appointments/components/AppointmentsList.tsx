"use client";

import { useState } from "react";

import Button from "@/components/ui/Button";
import Modal from "@/components/ui/Modal";
import { useCurrentUser } from "@/features/auth/hooks/useCurrentUser";
import { formatPrice } from "@/features/services/format";
import { apiErrorMessage } from "@/lib/api";

import { useAppointments, useCancelAppointment } from "../hooks/useAppointments";
import { formatSlotDateTime } from "../format";
import type { Appointment, AppointmentStatus } from "../types";
import RescheduleControl from "./RescheduleControl";
import styles from "./AppointmentsList.module.css";

const SELF_SERVICE_CUTOFF_HOURS = 24;

const STATUS_LABELS: Record<AppointmentStatus, string> = {
  booked: "Marcada",
  made: "Realizada",
  canceled: "Cancelada",
  no_show: "Falta",
};

function hoursUntil(iso: string): number {
  return (new Date(iso).getTime() - Date.now()) / 3_600_000;
}

function AppointmentCard({ appointment }: { appointment: Appointment }) {
  const [mode, setMode] = useState<"idle" | "confirmCancel" | "reschedule">("idle");
  const [nailArtOpen, setNailArtOpen] = useState(false);
  const cancel = useCancelAppointment();

  const isUpcoming = appointment.status === "booked" && hoursUntil(appointment.start_at) > 0;
  const withinCutoff = hoursUntil(appointment.start_at) < SELF_SERVICE_CUTOFF_HOURS;
  const canSelfManage = appointment.status === "booked" && isUpcoming && !withinCutoff;

  return (
    <li className={styles.card}>
      <div className={styles.head}>
        <div>
          <span className={styles.service}>{appointment.service.name}</span>
          <span className={styles.when}>{formatSlotDateTime(appointment.start_at)}</span>
        </div>
        <span className={styles.badge} data-status={appointment.status}>
          {STATUS_LABELS[appointment.status]}
        </span>
      </div>

      <div className={styles.meta}>
        <span className={styles.price}>
          {formatPrice(appointment.price_snapshot, appointment.is_quote_only_snapshot)}
        </span>
        {appointment.has_nail_art && (
          <span className={styles.tag}>
            Nail art {appointment.nail_art_option === "complex" ? "complexa" : "simples"}
          </span>
        )}
      </div>

      {(canSelfManage || (appointment.status === "booked" && appointment.has_nail_art)) &&
        mode === "idle" && (
          <div className={styles.actions}>
            {canSelfManage && (
              <Button size="sm" variant="secondary" onClick={() => setMode("reschedule")}>
                Reagendar
              </Button>
            )}
            {canSelfManage && (
              <Button size="sm" variant="secondary" onClick={() => setMode("confirmCancel")}>
                Cancelar
              </Button>
            )}
            {appointment.status === "booked" && appointment.has_nail_art && (
              <Button size="sm" variant="secondary" onClick={() => setNailArtOpen(true)}>
                Alterar nail art
              </Button>
            )}
          </div>
        )}

      {nailArtOpen && (
        <Modal title="Alterar nail art" onClose={() => setNailArtOpen(false)}>
          <p>
            As alterações de nail art (simples ↔ complexa) só podem ser feitas pela
            tua esteticista. Por favor, fala diretamente com ela para alterar esta
            marcação.
          </p>
          <div className={styles.modalActions}>
            <Button size="sm" onClick={() => setNailArtOpen(false)}>
              Entendido
            </Button>
          </div>
        </Modal>
      )}

      {appointment.status === "booked" && isUpcoming && withinCutoff && (
        <p className={styles.note}>
          A menos de 24h da marcação — para alterar ou cancelar, contacta o staff diretamente.
        </p>
      )}

      {mode === "confirmCancel" && (
        <div className={styles.confirm}>
          {cancel.isError && <p className={styles.error}>{apiErrorMessage(cancel.error)}</p>}
          <p className={styles.confirmText}>Cancelar esta marcação?</p>
          <div className={styles.actions}>
            <Button
              size="sm"
              onClick={() => cancel.mutate(appointment.id, { onSuccess: () => setMode("idle") })}
              disabled={cancel.isPending}
            >
              {cancel.isPending ? "A cancelar…" : "Sim, cancelar"}
            </Button>
            <Button size="sm" variant="secondary" onClick={() => setMode("idle")}>
              Voltar
            </Button>
          </div>
        </div>
      )}

      {mode === "reschedule" && (
        <RescheduleControl appointment={appointment} onDone={() => setMode("idle")} />
      )}
    </li>
  );
}

export default function AppointmentsList() {
  const { data: user, isLoading: userLoading } = useCurrentUser();
  const { data, isLoading, isError } = useAppointments();

  if (userLoading) return <p className={styles.status}>A carregar…</p>;

  if (!user || user.role !== "client") {
    return (
      <div className={styles.gate}>
        <p>Inicia sessão como cliente para veres as tuas marcações.</p>
        <Button href="/login" size="sm">
          Entrar
        </Button>
      </div>
    );
  }

  if (isLoading) return <p className={styles.status}>A carregar marcações…</p>;
  if (isError) return <p className={styles.status}>Não foi possível carregar as marcações.</p>;
  if (!data || data.length === 0)
    return (
      <div className={styles.gate}>
        <p>Ainda não tens marcações.</p>
        <Button href="/agendar" size="sm">
          Agendar
        </Button>
      </div>
    );

  const upcoming = data
    .filter((a) => a.status === "booked" && hoursUntil(a.start_at) > 0)
    .sort((a, b) => a.start_at.localeCompare(b.start_at));
  const history = data
    .filter((a) => !(a.status === "booked" && hoursUntil(a.start_at) > 0))
    .sort((a, b) => b.start_at.localeCompare(a.start_at));

  return (
    <div className={styles.sections}>
      <section>
        <h2 className={styles.sectionTitle}>Próximas</h2>
        {upcoming.length === 0 ? (
          <p className={styles.status}>Sem marcações futuras.</p>
        ) : (
          <ul className={styles.list}>
            {upcoming.map((a) => (
              <AppointmentCard key={a.id} appointment={a} />
            ))}
          </ul>
        )}
      </section>

      {history.length > 0 && (
        <section>
          <h2 className={styles.sectionTitle}>Histórico</h2>
          <ul className={styles.list}>
            {history.map((a) => (
              <AppointmentCard key={a.id} appointment={a} />
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
