"use client";

import { useState } from "react";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Input from "@/components/ui/Input";
import { EmptyState, ErrorState, LoadingState } from "@/features/bo/shared/States";
import panel from "@/features/bo/shared/panel.module.css";
import { apiErrorMessage } from "@/lib/api";

import { useCreateTimeOff, useDeleteTimeOff, useTimeOff } from "../hooks/useTimeOff";
import { formatDateTime } from "../format";

/** Card listing and managing time-off periods (vacation, holidays, sick leave). */
export default function TimeOffManager({ staffId }: { staffId: string }) {
  const { data, isLoading, isError, error, refetch } = useTimeOff(staffId);
  const create = useCreateTimeOff(staffId);
  const remove = useDeleteTimeOff(staffId);

  const [start, setStart] = useState(""); // datetime-local "YYYY-MM-DDTHH:MM"
  const [end, setEnd] = useState("");
  const [reason, setReason] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  async function onAdd() {
    setFormError(null);
    if (!start || !end) {
      setFormError("Indica o início e o fim da ausência.");
      return;
    }
    const startDate = new Date(start);
    const endDate = new Date(end);
    if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
      setFormError("Datas inválidas.");
      return;
    }
    if (endDate <= startDate) {
      setFormError("O fim deve ser posterior ao início.");
      return;
    }
    try {
      await create.mutateAsync({
        start_at: startDate.toISOString(),
        end_at: endDate.toISOString(),
        reason,
      });
      setStart("");
      setEnd("");
      setReason("");
    } catch (err) {
      setFormError(apiErrorMessage(err, "Não foi possível adicionar a ausência."));
    }
  }

  return (
    <section className={panel.card}>
      <h2 className={panel.cardTitle}>Ausências</h2>
      <p className={panel.cardMeta}>Férias, folgas ou feriados — removem a disponibilidade.</p>

      {isLoading ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState action={<Button onClick={() => void refetch()}>Tentar novamente</Button>}>
          {apiErrorMessage(error, "Não foi possível carregar as ausências.")}
        </ErrorState>
      ) : !data || data.length === 0 ? (
        <EmptyState title="Sem ausências registadas">
          Adiciona uma ausência abaixo.
        </EmptyState>
      ) : (
        <div className={panel.tableWrap}>
          <table className={panel.table}>
            <thead>
              <tr>
                <th>Início</th>
                <th>Fim</th>
                <th>Motivo</th>
                <th aria-label="Ações" />
              </tr>
            </thead>
            <tbody>
              {data.map((to) => (
                <tr key={to.id}>
                  <td>{formatDateTime(to.start_at)}</td>
                  <td>{formatDateTime(to.end_at)}</td>
                  <td>{to.reason || "—"}</td>
                  <td>
                    <Button
                      variant="secondary"
                      size="sm"
                      disabled={remove.isPending}
                      onClick={() => void remove.mutateAsync(to.id)}
                    >
                      Remover
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className={panel.formRow}>
        <Field label="Início" htmlFor="timeoff-start">
          <Input
            id="timeoff-start"
            type="datetime-local"
            value={start}
            onChange={(e) => setStart(e.target.value)}
          />
        </Field>
        <Field label="Fim" htmlFor="timeoff-end">
          <Input
            id="timeoff-end"
            type="datetime-local"
            value={end}
            onChange={(e) => setEnd(e.target.value)}
          />
        </Field>
        <Field label="Motivo" htmlFor="timeoff-reason">
          <Input
            id="timeoff-reason"
            type="text"
            value={reason}
            placeholder="Ex.: férias"
            onChange={(e) => setReason(e.target.value)}
          />
        </Field>
        <Button onClick={() => void onAdd()} disabled={create.isPending}>
          {create.isPending ? "A adicionar…" : "Adicionar ausência"}
        </Button>
      </div>

      {formError ? (
        <p className={panel.feedbackError} role="alert">
          {formError}
        </p>
      ) : null}
    </section>
  );
}
