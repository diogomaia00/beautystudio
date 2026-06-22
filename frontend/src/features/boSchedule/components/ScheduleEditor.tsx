"use client";

import { useEffect, useState } from "react";

import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import { ErrorState, LoadingState } from "@/features/bo/shared/States";
import panel from "@/features/bo/shared/panel.module.css";
import { apiErrorMessage } from "@/lib/api";

import { useReplaceSchedule, useSchedule } from "../hooks/useSchedule";
import { formatTime } from "../format";
import { WEEKDAYS } from "../types";
import type { ScheduleEntry, ScheduleEntryInput } from "../types";

interface DayState {
  open: boolean;
  start: string; // "HH:MM"
  end: string;
}

const DEFAULT_START = "09:00";
const DEFAULT_END = "18:00";

function buildState(entries: ScheduleEntry[]): Record<number, DayState> {
  const byDay = new Map<number, ScheduleEntry>();
  for (const e of entries) byDay.set(e.weekday, e);

  const result: Record<number, DayState> = {};
  for (const { value } of WEEKDAYS) {
    const entry = byDay.get(value);
    result[value] = entry
      ? { open: true, start: formatTime(entry.start_time), end: formatTime(entry.end_time) }
      : { open: false, start: DEFAULT_START, end: DEFAULT_END };
  }
  return result;
}

/** Card editing the weekly working schedule (one row per weekday, Mon→Sun). */
export default function ScheduleEditor({ staffId }: { staffId: string }) {
  const { data, isLoading, isError, error, refetch } = useSchedule(staffId);
  const replace = useReplaceSchedule(staffId);

  const [days, setDays] = useState<Record<number, DayState>>({});
  const [feedback, setFeedback] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  // Prefill the editable form from the fetched schedule whenever it (re)loads —
  // e.g. on first load and after a save refetch. Syncing local editable state
  // from an async external source is a legitimate use of an effect here, so the
  // React Compiler readiness rule is suppressed only at this reviewed site (it
  // stays on everywhere else). See eslint.config.mjs.
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (data) setDays(buildState(data));
  }, [data]);

  function updateDay(weekday: number, patch: Partial<DayState>) {
    setDays((prev) => ({ ...prev, [weekday]: { ...prev[weekday], ...patch } }));
    setFeedback(null);
    setFormError(null);
  }

  async function onSave() {
    setFeedback(null);
    setFormError(null);

    const entries: ScheduleEntryInput[] = [];
    for (const { value, label } of WEEKDAYS) {
      const day = days[value];
      if (!day?.open) continue;
      if (!day.start || !day.end) {
        setFormError(`Indica as horas de início e fim para ${label}.`);
        return;
      }
      if (day.end <= day.start) {
        setFormError(`A hora de fim deve ser posterior à de início (${label}).`);
        return;
      }
      entries.push({ weekday: value, start_time: day.start, end_time: day.end });
    }

    try {
      await replace.mutateAsync(entries);
      setFeedback("Horário guardado.");
    } catch (err) {
      setFormError(apiErrorMessage(err, "Não foi possível guardar o horário."));
    }
  }

  if (isLoading) {
    return (
      <section className={panel.card}>
        <h2 className={panel.cardTitle}>Horário semanal</h2>
        <LoadingState />
      </section>
    );
  }

  if (isError) {
    return (
      <section className={panel.card}>
        <h2 className={panel.cardTitle}>Horário semanal</h2>
        <ErrorState action={<Button onClick={() => void refetch()}>Tentar novamente</Button>}>
          {apiErrorMessage(error, "Não foi possível carregar o horário.")}
        </ErrorState>
      </section>
    );
  }

  return (
    <section className={panel.card}>
      <h2 className={panel.cardTitle}>Horário semanal</h2>
      <p className={panel.cardMeta}>
        Marca os dias em que trabalhas e define as horas. Guardar substitui todo o horário.
      </p>

      <div className={panel.grid}>
        {WEEKDAYS.map(({ value, label }) => {
          const day = days[value];
          if (!day) return null;
          const startId = `schedule-start-${value}`;
          const endId = `schedule-end-${value}`;
          return (
            <div key={value} className={panel.formRow}>
              <label
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "var(--space-2)",
                  minWidth: "9rem",
                }}
              >
                <input
                  type="checkbox"
                  checked={day.open}
                  onChange={(e) => updateDay(value, { open: e.target.checked })}
                />
                <span>{label}</span>
              </label>

              <label htmlFor={startId} style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
                <span className={panel.cardMeta}>Início</span>
                <Input
                  id={startId}
                  type="time"
                  value={day.start}
                  disabled={!day.open}
                  onChange={(e) => updateDay(value, { start: e.target.value })}
                />
              </label>

              <label htmlFor={endId} style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
                <span className={panel.cardMeta}>Fim</span>
                <Input
                  id={endId}
                  type="time"
                  value={day.end}
                  disabled={!day.open}
                  onChange={(e) => updateDay(value, { end: e.target.value })}
                />
              </label>
            </div>
          );
        })}
      </div>

      {formError ? (
        <p className={panel.feedbackError} role="alert">
          {formError}
        </p>
      ) : null}
      {feedback ? (
        <p className={panel.feedbackSuccess} role="status">
          {feedback}
        </p>
      ) : null}

      <div className={panel.actions}>
        <Button onClick={() => void onSave()} disabled={replace.isPending}>
          {replace.isPending ? "A guardar…" : "Guardar horário"}
        </Button>
      </div>
    </section>
  );
}
