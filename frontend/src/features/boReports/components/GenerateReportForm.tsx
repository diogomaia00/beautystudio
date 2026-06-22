"use client";

import { useForm } from "react-hook-form";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";
import { apiErrorMessage } from "@/lib/api";

import { useGenerateReport } from "../hooks/useGenerateReport";
import { monthLabel } from "../format";
import type { MonthlyReport } from "../types";

import panel from "@/features/bo/shared/panel.module.css";

interface FormValues {
  year: number;
  month: number;
}

interface GenerateReportFormProps {
  /** For admins, the active staff id sent with the request. Staff pass undefined. */
  staffId?: string;
  /** True when the signed-in user is the admin. */
  isAdmin: boolean;
  /** Called after a successful generation, with the resulting report. */
  onGenerated?: (report: MonthlyReport) => void;
}

export default function GenerateReportForm({
  staffId,
  isAdmin,
  onGenerated,
}: GenerateReportFormProps) {
  const now = new Date();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    defaultValues: { year: now.getFullYear(), month: now.getMonth() + 1 },
  });

  const generate = useGenerateReport();

  const onSubmit = handleSubmit((values) => {
    generate.reset();
    generate.mutate(
      {
        year: Number(values.year),
        month: Number(values.month),
        ...(isAdmin && staffId ? { staff_id: staffId } : {}),
      },
      { onSuccess: (report) => onGenerated?.(report) },
    );
  });

  return (
    <form className={panel.card} onSubmit={onSubmit} noValidate>
      <h2 className={panel.cardTitle}>Gerar relatório</h2>
      <p className={panel.cardMeta}>
        Calcula o relatório de um mês. Voltar a gerar o mesmo período atualiza os
        valores.
      </p>

      <div className={panel.formRow}>
        <Field
          label="Ano"
          htmlFor="report-year"
          error={errors.year ? "Ano inválido (2000-2100)." : undefined}
        >
          <Input
            id="report-year"
            type="number"
            min={2000}
            max={2100}
            invalid={!!errors.year}
            {...register("year", {
              required: true,
              valueAsNumber: true,
              min: 2000,
              max: 2100,
            })}
          />
        </Field>

        <Field label="Mês" htmlFor="report-month">
          <Select
            id="report-month"
            {...register("month", { required: true, valueAsNumber: true })}
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
              <option key={m} value={m}>
                {monthLabel(m)}
              </option>
            ))}
          </Select>
        </Field>

        <Button type="submit" disabled={generate.isPending}>
          {generate.isPending ? "A gerar…" : "Gerar"}
        </Button>
      </div>

      {generate.isError ? (
        <p className={panel.feedbackError} role="alert">
          {apiErrorMessage(generate.error, "Não foi possível gerar o relatório.")}
        </p>
      ) : null}
      {generate.isSuccess ? (
        <p className={panel.feedbackSuccess} role="status">
          Relatório gerado com sucesso.
        </p>
      ) : null}
    </form>
  );
}
