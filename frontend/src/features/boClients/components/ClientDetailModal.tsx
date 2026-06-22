"use client";

import { useForm } from "react-hook-form";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Input from "@/components/ui/Input";
import Modal from "@/components/ui/Modal";
import Select from "@/components/ui/Select";
import Badge from "@/features/bo/shared/Badge";
import {
  ErrorState,
  LoadingState,
} from "@/features/bo/shared/States";
import type { Service } from "@/features/services/types";
import { apiErrorMessage, boApiClient } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

import panel from "@/features/bo/shared/panel.module.css";

import { formatChannel, formatDate, fullName } from "../format";
import { useClient, useSetBlacklist } from "../hooks/useClient";
import {
  useCreateDuration,
  useDeleteDuration,
  useDurations,
} from "../hooks/useDurations";
import type { Client } from "../types";

interface DurationFormValues {
  service_id: string;
  duration_minutes: string;
}

/** Services list for the duration override picker (kept local to the modal). */
function useServicesList() {
  return useQuery({
    queryKey: ["bo", "services", "list-picker"],
    queryFn: () => boApiClient.get<Service[]>("/services/"),
    staleTime: 60_000,
  });
}

export default function ClientDetailModal({
  client,
  onClose,
}: {
  client: Client;
  onClose: () => void;
}) {
  const detail = useClient(client.id);
  const durations = useDurations(client.id);
  const services = useServicesList();
  const blacklistMutation = useSetBlacklist(client.id);
  const createDuration = useCreateDuration(client.id);
  const deleteDuration = useDeleteDuration(client.id);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<DurationFormValues>({
    defaultValues: { service_id: "", duration_minutes: "" },
  });

  const current = detail.data ?? client;
  const isBlacklisted = current.blacklisted;

  const onSubmit = handleSubmit((values) => {
    const minutes = Number(values.duration_minutes);
    createDuration.mutate(
      { service_id: values.service_id, duration_minutes: minutes },
      { onSuccess: () => reset() },
    );
  });

  return (
    <Modal title={`Cliente · ${fullName(client)}`} onClose={onClose}>
      <div className={panel.page}>
        {detail.isLoading ? (
          <LoadingState label="A carregar cliente…" />
        ) : detail.isError ? (
          <ErrorState
            action={
              <Button
                type="button"
                variant="secondary"
                onClick={() => detail.refetch()}
              >
                Tentar novamente
              </Button>
            }
          >
            {apiErrorMessage(detail.error, "Não foi possível carregar o cliente.")}
          </ErrorState>
        ) : (
          <>
            <section className={panel.card}>
              <p className={panel.cardTitle}>Contactos</p>
              <div className={panel.grid2}>
                <p className={panel.cardMeta}>Telemóvel: {current.msisdn}</p>
                <p className={panel.cardMeta}>Email: {current.email}</p>
                <p className={panel.cardMeta}>
                  Aniversário: {formatDate(current.birthday)}
                </p>
                <p className={panel.cardMeta}>
                  Canal preferido: {formatChannel(current.preferred_channel)}
                </p>
              </div>
              <div className={panel.actions}>
                {isBlacklisted ? (
                  <Badge tone="error">Lista negra</Badge>
                ) : current.is_active ? (
                  <Badge tone="success">Ativo</Badge>
                ) : (
                  <Badge tone="neutral">Inativo</Badge>
                )}
              </div>
            </section>

            <section className={panel.card}>
              <p className={panel.cardTitle}>Histórico de presenças</p>
              <div className={panel.actions}>
                <Badge tone="info">
                  Marcadas: {detail.data?.attendance.booked ?? 0}
                </Badge>
                <Badge tone="success">
                  Feitas: {detail.data?.attendance.made ?? 0}
                </Badge>
                <Badge tone="warning">
                  Canceladas: {detail.data?.attendance.canceled ?? 0}
                </Badge>
                <Badge tone="error">
                  Faltas: {detail.data?.attendance.no_show ?? 0}
                </Badge>
              </div>
            </section>

            <section className={panel.card}>
              <p className={panel.cardTitle}>Lista negra</p>
              <p className={panel.cardMeta}>
                {isBlacklisted
                  ? "Este cliente está na lista negra e não consegue marcar pela app. Remove-o para voltar a permitir marcações."
                  : "Ao colocar o cliente na lista negra, ele deixa de conseguir marcar pela app (as marcações existentes não são afetadas)."}
              </p>
              {blacklistMutation.isError ? (
                <p className={panel.feedbackError} role="alert">
                  {apiErrorMessage(
                    blacklistMutation.error,
                    "Não foi possível atualizar a lista negra.",
                  )}
                </p>
              ) : null}
              <div className={panel.actions}>
                <Button
                  type="button"
                  variant={isBlacklisted ? "secondary" : "primary"}
                  disabled={blacklistMutation.isPending}
                  onClick={() => blacklistMutation.mutate(!isBlacklisted)}
                >
                  {blacklistMutation.isPending
                    ? "A atualizar…"
                    : isBlacklisted
                      ? "Remover da lista negra"
                      : "Colocar na lista negra"}
                </Button>
              </div>
            </section>

            <section className={panel.card}>
              <p className={panel.cardTitle}>Durações por serviço</p>
              <p className={panel.cardMeta}>
                Define o tempo habitual deste cliente para um serviço; substitui a
                duração predefinida ao marcar.
              </p>

              {durations.isLoading ? (
                <LoadingState />
              ) : durations.isError ? (
                <ErrorState>
                  {apiErrorMessage(
                    durations.error,
                    "Não foi possível carregar as durações.",
                  )}
                </ErrorState>
              ) : (durations.data ?? []).length === 0 ? (
                <p className={panel.cardMeta}>Sem durações personalizadas.</p>
              ) : (
                <div className={panel.tableWrap}>
                  <table className={panel.table}>
                    <thead>
                      <tr>
                        <th>Serviço</th>
                        <th>Duração</th>
                        <th>Ações</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(durations.data ?? []).map((duration) => (
                        <tr key={duration.id}>
                          <td>{duration.service_name}</td>
                          <td>{duration.duration_minutes} min</td>
                          <td>
                            <Button
                              type="button"
                              variant="secondary"
                              size="sm"
                              disabled={deleteDuration.isPending}
                              onClick={() =>
                                deleteDuration.mutate(duration.service)
                              }
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

              {deleteDuration.isError ? (
                <p className={panel.feedbackError} role="alert">
                  {apiErrorMessage(
                    deleteDuration.error,
                    "Não foi possível remover a duração.",
                  )}
                </p>
              ) : null}

              <form onSubmit={onSubmit} className={panel.formRow}>
                <Field
                  label="Serviço"
                  htmlFor="duration-service"
                  error={errors.service_id?.message}
                >
                  <Select
                    id="duration-service"
                    disabled={services.isLoading}
                    invalid={Boolean(errors.service_id)}
                    {...register("service_id", {
                      required: "Escolhe um serviço.",
                    })}
                  >
                    <option value="">Seleciona um serviço</option>
                    {(services.data ?? []).map((service) => (
                      <option key={service.id} value={service.id}>
                        {service.name}
                      </option>
                    ))}
                  </Select>
                </Field>

                <Field
                  label="Duração (min)"
                  htmlFor="duration-minutes"
                  error={errors.duration_minutes?.message}
                >
                  <Input
                    id="duration-minutes"
                    type="number"
                    min={1}
                    step={1}
                    invalid={Boolean(errors.duration_minutes)}
                    {...register("duration_minutes", {
                      required: "Indica a duração.",
                      min: { value: 1, message: "Mínimo de 1 minuto." },
                    })}
                  />
                </Field>

                <Button type="submit" disabled={createDuration.isPending}>
                  {createDuration.isPending ? "A adicionar…" : "Adicionar"}
                </Button>
              </form>

              {services.isError ? (
                <p className={panel.feedbackError} role="alert">
                  {apiErrorMessage(
                    services.error,
                    "Não foi possível carregar os serviços.",
                  )}
                </p>
              ) : null}

              {createDuration.isError ? (
                <p className={panel.feedbackError} role="alert">
                  {apiErrorMessage(
                    createDuration.error,
                    "Não foi possível adicionar a duração.",
                  )}
                </p>
              ) : null}
            </section>
          </>
        )}
      </div>
    </Modal>
  );
}
