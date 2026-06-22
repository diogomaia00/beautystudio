import Button from "@/components/ui/Button";
import Badge from "@/features/bo/shared/Badge";
import panel from "@/features/bo/shared/panel.module.css";

import {
  formatPrice,
  formatTimeRange,
  nailArtLabel,
  statusLabel,
  statusTone,
} from "../format";
import type { AppointmentActions } from "../hooks/useAppointmentActions";
import type { BoAppointment } from "../types";

interface AppointmentRowProps {
  appointment: BoAppointment;
  actions: AppointmentActions;
  onReschedule: (appointment: BoAppointment) => void;
  onEditNailArt: (appointment: BoAppointment) => void;
}

/** A single agenda table row: time, client, service, status and actions. */
export default function AppointmentRow({
  appointment,
  actions,
  onReschedule,
  onEditNailArt,
}: AppointmentRowProps) {
  const {
    markMadeMutation,
    markNoShowMutation,
    cancelMutation,
  } = actions;

  const isBooked = appointment.status === "booked";

  const onCancel = () => {
    if (window.confirm("Cancelar esta marcação? Esta ação não pode ser anulada.")) {
      cancelMutation.mutate(appointment.id);
    }
  };

  return (
    <tr>
      <td>{formatTimeRange(appointment.start_at, appointment.end_at)}</td>
      <td>
        <div>{appointment.client_name}</div>
        <a href={`tel:${appointment.client_msisdn}`} className={panel.cardMeta}>
          {appointment.client_msisdn}
        </a>
      </td>
      <td>
        {appointment.service.name}
        {appointment.has_nail_art ? (
          <>
            {" "}
            <Badge tone="accent">{nailArtLabel(appointment.nail_art_option)}</Badge>
          </>
        ) : null}
      </td>
      <td>
        <Badge tone={statusTone(appointment.status)}>
          {statusLabel(appointment.status)}
        </Badge>
      </td>
      <td>
        {formatPrice(
          appointment.price_snapshot,
          appointment.is_quote_only_snapshot,
        )}
      </td>
      <td>
        <div className={panel.actions}>
          {isBooked ? (
            <>
              <Button
                type="button"
                size="sm"
                onClick={() => markMadeMutation.mutate(appointment.id)}
                disabled={markMadeMutation.isPending}
              >
                Feito
              </Button>
              <Button
                type="button"
                size="sm"
                variant="secondary"
                onClick={() => markNoShowMutation.mutate(appointment.id)}
                disabled={markNoShowMutation.isPending}
              >
                Falta
              </Button>
              <Button
                type="button"
                size="sm"
                variant="secondary"
                onClick={() => onReschedule(appointment)}
              >
                Remarcar
              </Button>
              <Button
                type="button"
                size="sm"
                variant="secondary"
                onClick={onCancel}
                disabled={cancelMutation.isPending}
              >
                Cancelar
              </Button>
            </>
          ) : null}
          {appointment.service.is_nail_service ? (
            <Button
              type="button"
              size="sm"
              variant="secondary"
              onClick={() => onEditNailArt(appointment)}
            >
              Editar nail art
            </Button>
          ) : null}
        </div>
      </td>
    </tr>
  );
}
