"use client";

import { useState } from "react";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Select from "@/components/ui/Select";
import Badge from "@/features/bo/shared/Badge";
import { EmptyState, ErrorState, LoadingState } from "@/features/bo/shared/States";
import panel from "@/features/bo/shared/panel.module.css";
import { apiErrorMessage } from "@/lib/api";

import {
  useCustomRequests,
  useUpdateCustomRequestStatus,
} from "../hooks/useCustomRequests";
import {
  customRequestStatusLabel,
  customRequestStatusTone,
  formatPreferred,
} from "../format";
import type { CustomRequest, CustomRequestStatus } from "../types";

const FILTERS: { value: CustomRequestStatus; label: string }[] = [
  { value: "pending", label: "Pendente" },
  { value: "accepted", label: "Aceite" },
  { value: "rejected", label: "Recusado" },
  { value: "closed", label: "Fechado" },
];

/** Status changes available for a custom request from the actions cell. */
const SET_OPTIONS: { value: CustomRequestStatus; label: string }[] = [
  { value: "accepted", label: "Aceitar" },
  { value: "rejected", label: "Recusar" },
  { value: "closed", label: "Fechar" },
];

/** Custom booking requests (beyond the booking horizon) for the active staff member. */
export default function CustomRequestsSection({ staffId }: { staffId: string }) {
  const [status, setStatus] = useState<CustomRequestStatus>("pending");
  const { data, isLoading, isError, error, refetch } = useCustomRequests(
    staffId,
    status,
  );
  const update = useUpdateCustomRequestStatus(staffId);
  const [actionError, setActionError] = useState<string | null>(null);

  async function setStatusFor(request: CustomRequest, next: CustomRequestStatus) {
    setActionError(null);
    try {
      await update.mutateAsync({ id: request.id, status: next });
    } catch (err) {
      setActionError(apiErrorMessage(err, "Não foi possível atualizar o pedido."));
    }
  }

  return (
    <section className={panel.card}>
      <h2 className={panel.cardTitle}>Pedidos personalizados</h2>
      <p className={panel.cardMeta}>
        Pedidos de marcação além do horizonte de reservas — combina os detalhes
        diretamente com o cliente.
      </p>

      <div className={panel.toolbar}>
        <Field label="Estado" htmlFor="custom-request-status">
          <Select
            id="custom-request-status"
            value={status}
            onChange={(e) => setStatus(e.target.value as CustomRequestStatus)}
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
          {apiErrorMessage(error, "Não foi possível carregar os pedidos.")}
        </ErrorState>
      ) : !data || data.length === 0 ? (
        <EmptyState title="Sem pedidos personalizados">
          Não há pedidos com este estado.
        </EmptyState>
      ) : (
        <div className={panel.tableWrap}>
          <table className={panel.table}>
            <thead>
              <tr>
                <th>Cliente</th>
                <th>Serviço</th>
                <th>Preferência</th>
                <th>Estado</th>
                <th>Nota</th>
                <th aria-label="Ações" />
              </tr>
            </thead>
            <tbody>
              {data.map((request) => (
                <tr key={request.id}>
                  <td>{request.client_msisdn}</td>
                  <td>{request.service_name}</td>
                  <td>
                    {formatPreferred(request.preferred_date, request.preferred_time)}
                  </td>
                  <td>
                    <Badge tone={customRequestStatusTone(request.status)}>
                      {customRequestStatusLabel(request.status)}
                    </Badge>
                  </td>
                  <td>{request.note || "—"}</td>
                  <td>
                    <div className={panel.actions}>
                      {SET_OPTIONS.filter((o) => o.value !== request.status).map(
                        (o) => (
                          <Button
                            key={o.value}
                            variant="secondary"
                            size="sm"
                            disabled={update.isPending}
                            onClick={() => void setStatusFor(request, o.value)}
                          >
                            {o.label}
                          </Button>
                        ),
                      )}
                    </div>
                  </td>
                </tr>
              ))}
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
