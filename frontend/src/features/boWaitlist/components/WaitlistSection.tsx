"use client";

import { useState } from "react";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Select from "@/components/ui/Select";
import Badge from "@/features/bo/shared/Badge";
import { EmptyState, ErrorState, LoadingState } from "@/features/bo/shared/States";
import panel from "@/features/bo/shared/panel.module.css";
import { apiErrorMessage } from "@/lib/api";

import { useUpdateWaitlistStatus, useWaitlist } from "../hooks/useWaitlist";
import {
  formatDateTime,
  waitlistStatusLabel,
  waitlistStatusTone,
} from "../format";
import type { WaitlistEntry, WaitlistStatus } from "../types";

const FILTERS: { value: WaitlistStatus; label: string }[] = [
  { value: "waiting", label: "Em espera" },
  { value: "contacted", label: "Contactado" },
  { value: "closed", label: "Fechado" },
];

/** The status this entry can advance to (waiting → contacted → closed). */
function nextStatus(status: WaitlistStatus): WaitlistStatus | null {
  if (status === "waiting") return "contacted";
  if (status === "contacted") return "closed";
  return null;
}

function advanceLabel(status: WaitlistStatus): string {
  if (status === "waiting") return "Marcar contactado";
  if (status === "contacted") return "Fechar";
  return "";
}

/** Waitlist for occupied times of the active staff member. */
export default function WaitlistSection({ staffId }: { staffId: string }) {
  const [status, setStatus] = useState<WaitlistStatus>("waiting");
  const { data, isLoading, isError, error, refetch } = useWaitlist(staffId, status);
  const update = useUpdateWaitlistStatus(staffId);
  const [actionError, setActionError] = useState<string | null>(null);

  async function advance(entry: WaitlistEntry) {
    const next = nextStatus(entry.status);
    if (!next) return;
    setActionError(null);
    try {
      await update.mutateAsync({ id: entry.id, status: next });
    } catch (err) {
      setActionError(apiErrorMessage(err, "Não foi possível atualizar a entrada."));
    }
  }

  return (
    <section className={panel.card}>
      <h2 className={panel.cardTitle}>Lista de espera</h2>
      <p className={panel.cardMeta}>
        Contacta o cliente <strong>fora da aplicação</strong> para combinar uma
        eventual troca. Não há oferta automática.
      </p>

      <div className={panel.toolbar}>
        <Field label="Estado" htmlFor="waitlist-status">
          <Select
            id="waitlist-status"
            value={status}
            onChange={(e) => setStatus(e.target.value as WaitlistStatus)}
          >
            {FILTERS.map((f) => (
              <option key={f.value} value={f.value}>
                {f.label}
              </option>
            ))}
          </Select>
        </Field>
      </div>

      {isLoading ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState
          action={<Button onClick={() => void refetch()}>Tentar novamente</Button>}
        >
          {apiErrorMessage(error, "Não foi possível carregar a lista de espera.")}
        </ErrorState>
      ) : !data || data.length === 0 ? (
        <EmptyState title="Sem entradas na lista de espera">
          Não há entradas com este estado.
        </EmptyState>
      ) : (
        <div className={panel.tableWrap}>
          <table className={panel.table}>
            <thead>
              <tr>
                <th>Cliente</th>
                <th>Serviço</th>
                <th>Pretendido</th>
                <th>Estado</th>
                <th>Nota</th>
                <th aria-label="Ações" />
              </tr>
            </thead>
            <tbody>
              {data.map((entry) => {
                const label = advanceLabel(entry.status);
                return (
                  <tr key={entry.id}>
                    <td>{entry.client_msisdn}</td>
                    <td>{entry.service_name}</td>
                    <td>{formatDateTime(entry.desired_start_at)}</td>
                    <td>
                      <Badge tone={waitlistStatusTone(entry.status)}>
                        {waitlistStatusLabel(entry.status)}
                      </Badge>
                    </td>
                    <td>{entry.note || "—"}</td>
                    <td>
                      {label ? (
                        <Button
                          variant="secondary"
                          size="sm"
                          disabled={update.isPending}
                          onClick={() => void advance(entry)}
                        >
                          {label}
                        </Button>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {actionError ? (
        <p className={panel.feedbackError} role="alert">
          {actionError}
        </p>
      ) : null}
    </section>
  );
}
