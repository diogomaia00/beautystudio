"use client";

import { useState } from "react";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";
import { EmptyState, ErrorState, LoadingState } from "@/features/bo/shared/States";
import panel from "@/features/bo/shared/panel.module.css";
import { apiErrorMessage } from "@/lib/api";

import { useBreaks, useCreateBreak, useDeleteBreak } from "../hooks/useBreaks";
import { formatTime } from "../format";
import { WEEKDAYS, weekdayLabel } from "../types";

const DEFAULT_START = "12:00";
const DEFAULT_END = "13:00";

/** Card listing and managing recurring break windows (e.g. lunch). */
export default function BreaksManager({ staffId }: { staffId: string }) {
  const { data, isLoading, isError, error, refetch } = useBreaks(staffId);
  const create = useCreateBreak(staffId);
  const remove = useDeleteBreak(staffId);

  const [weekday, setWeekday] = useState<number>(WEEKDAYS[0].value);
  const [start, setStart] = useState(DEFAULT_START);
  const [end, setEnd] = useState(DEFAULT_END);
  const [reason, setReason] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  async function onAdd() {
    setFormError(null);
    if (!start || !end) {
      setFormError("Indica as horas de início e fim.");
      return;
    }
    if (end <= start) {
      setFormError("A hora de fim deve ser posterior à de início.");
      return;
    }
    try {
      await create.mutateAsync({ weekday, start_time: start, end_time: end, reason });
      setReason("");
    } catch (err) {
      setFormError(apiErrorMessage(err, "Não foi possível adicionar a pausa."));
    }
  }

  return (
    <section className={panel.card}>
      <h2 className={panel.cardTitle}>Pausas</h2>
      <p className={panel.cardMeta}>Janelas recorrentes não reserváveis (ex.: almoço).</p>

      {isLoading ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState action={<Button onClick={() => void refetch()}>Tentar novamente</Button>}>
          {apiErrorMessage(error, "Não foi possível carregar as pausas.")}
        </ErrorState>
      ) : !data || data.length === 0 ? (
        <EmptyState title="Sem pausas definidas">
          Adiciona uma pausa abaixo.
        </EmptyState>
      ) : (
        <div className={panel.tableWrap}>
          <table className={panel.table}>
            <thead>
              <tr>
                <th>Dia</th>
                <th>Início</th>
                <th>Fim</th>
                <th>Motivo</th>
                <th aria-label="Ações" />
              </tr>
            </thead>
            <tbody>
              {data.map((brk) => (
                <tr key={brk.id}>
                  <td>{weekdayLabel(brk.weekday)}</td>
                  <td>{formatTime(brk.start_time)}</td>
                  <td>{formatTime(brk.end_time)}</td>
                  <td>{brk.reason || "—"}</td>
                  <td>
                    <Button
                      variant="secondary"
                      size="sm"
                      disabled={remove.isPending}
                      onClick={() => void remove.mutateAsync(brk.id)}
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
        <Field label="Dia" htmlFor="break-weekday">
          <Select
            id="break-weekday"
            value={weekday}
            onChange={(e) => setWeekday(Number(e.target.value))}
          >
            {WEEKDAYS.map((w) => (
              <option key={w.value} value={w.value}>
                {w.label}
              </option>
            ))}
          </Select>
        </Field>
        <Field label="Início" htmlFor="break-start">
          <Input
            id="break-start"
            type="time"
            value={start}
            onChange={(e) => setStart(e.target.value)}
          />
        </Field>
        <Field label="Fim" htmlFor="break-end">
          <Input id="break-end" type="time" value={end} onChange={(e) => setEnd(e.target.value)} />
        </Field>
        <Field label="Motivo" htmlFor="break-reason">
          <Input
            id="break-reason"
            type="text"
            value={reason}
            placeholder="Ex.: almoço"
            onChange={(e) => setReason(e.target.value)}
          />
        </Field>
        <Button onClick={() => void onAdd()} disabled={create.isPending}>
          {create.isPending ? "A adicionar…" : "Adicionar pausa"}
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
