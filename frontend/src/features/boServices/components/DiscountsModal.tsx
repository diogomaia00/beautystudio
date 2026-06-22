"use client";

import { useForm } from "react-hook-form";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Input from "@/components/ui/Input";
import Modal from "@/components/ui/Modal";
import Badge from "@/features/bo/shared/Badge";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/features/bo/shared/States";
import type { Service } from "@/features/services/types";
import { apiErrorMessage } from "@/lib/api";

import panel from "@/features/bo/shared/panel.module.css";

import { formatDateRange } from "../format";
import {
  useCreateDiscount,
  useDeleteDiscount,
  useDiscounts,
} from "../hooks/useDiscounts";

interface FormValues {
  percentage: string;
  starts_at: string;
  ends_at: string;
}

/** Convert a `datetime-local` value (local time) to an ISO string. */
function toIso(local: string): string {
  return new Date(local).toISOString();
}

export default function DiscountsModal({
  service,
  onClose,
}: {
  service: Service;
  onClose: () => void;
}) {
  const discounts = useDiscounts(service.id);
  const createMutation = useCreateDiscount(service.id);
  const deleteMutation = useDeleteDiscount(service.id);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    defaultValues: { percentage: "", starts_at: "", ends_at: "" },
  });

  const onSubmit = handleSubmit((values) => {
    createMutation.mutate(
      {
        percentage: values.percentage.trim(),
        starts_at: toIso(values.starts_at),
        ends_at: toIso(values.ends_at),
      },
      { onSuccess: () => reset() },
    );
  });

  return (
    <Modal title={`Descontos · ${service.name}`} onClose={onClose}>
      <div className={panel.page}>
        {discounts.isLoading ? (
          <LoadingState />
        ) : discounts.isError ? (
          <ErrorState>
            {apiErrorMessage(
              discounts.error,
              "Não foi possível carregar os descontos.",
            )}
          </ErrorState>
        ) : (discounts.data ?? []).length === 0 ? (
          <EmptyState title="Sem descontos">
            Adiciona um desconto sazonal no formulário abaixo.
          </EmptyState>
        ) : (
          <div className={panel.tableWrap}>
            <table className={panel.table}>
              <thead>
                <tr>
                  <th>Percentagem</th>
                  <th>Período</th>
                  <th>Estado</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {(discounts.data ?? []).map((discount) => (
                  <tr key={discount.id}>
                    <td>{discount.percentage}%</td>
                    <td>
                      {formatDateRange(discount.starts_at, discount.ends_at)}
                    </td>
                    <td>
                      {discount.is_active ? (
                        <Badge tone="success">Ativo</Badge>
                      ) : (
                        <Badge tone="neutral">Inativo</Badge>
                      )}
                    </td>
                    <td>
                      <Button
                        type="button"
                        variant="secondary"
                        size="sm"
                        disabled={deleteMutation.isPending}
                        onClick={() => deleteMutation.mutate(discount.id)}
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

        {deleteMutation.isError ? (
          <p className={panel.feedbackError} role="alert">
            {apiErrorMessage(
              deleteMutation.error,
              "Não foi possível remover o desconto.",
            )}
          </p>
        ) : null}

        <form onSubmit={onSubmit} className={panel.card}>
          <p className={panel.cardTitle}>Adicionar desconto</p>

          <div className={panel.grid3}>
            <Field
              label="Percentagem (%)"
              htmlFor="discount-percentage"
              error={errors.percentage?.message}
            >
              <Input
                id="discount-percentage"
                type="number"
                min={1}
                max={100}
                step="0.01"
                invalid={Boolean(errors.percentage)}
                {...register("percentage", {
                  required: "Indica a percentagem.",
                })}
              />
            </Field>

            <Field
              label="Início"
              htmlFor="discount-starts"
              error={errors.starts_at?.message}
            >
              <Input
                id="discount-starts"
                type="datetime-local"
                invalid={Boolean(errors.starts_at)}
                {...register("starts_at", { required: "Indica o início." })}
              />
            </Field>

            <Field
              label="Fim"
              htmlFor="discount-ends"
              error={errors.ends_at?.message}
            >
              <Input
                id="discount-ends"
                type="datetime-local"
                invalid={Boolean(errors.ends_at)}
                {...register("ends_at", { required: "Indica o fim." })}
              />
            </Field>
          </div>

          {createMutation.isError ? (
            <p className={panel.feedbackError} role="alert">
              {apiErrorMessage(
                createMutation.error,
                "Não foi possível adicionar o desconto.",
              )}
            </p>
          ) : null}

          <div className={panel.actions}>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? "A adicionar…" : "Adicionar"}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
}
