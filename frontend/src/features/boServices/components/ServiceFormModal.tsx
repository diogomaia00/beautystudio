"use client";

import { useForm } from "react-hook-form";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Input from "@/components/ui/Input";
import Modal from "@/components/ui/Modal";
import Select from "@/components/ui/Select";
import { useCategories } from "@/features/services/hooks/useCatalog";
import type { Service } from "@/features/services/types";
import { useStaff } from "@/features/staff/hooks/useStaff";
import { apiErrorMessage } from "@/lib/api";

import panel from "@/features/bo/shared/panel.module.css";

import {
  useCreateService,
  useUpdateService,
} from "../hooks/useServiceMutations";
import type { CreateServiceInput, UpdateServiceInput } from "../types";

interface FormValues {
  name: string;
  category_id: string;
  staff_id: string;
  duration_minutes: string;
  price: string;
  is_quote_only: boolean;
  is_nail_service: boolean;
  is_active: boolean;
  description: string;
}

function toDefaults(service?: Service): FormValues {
  return {
    name: service?.name ?? "",
    category_id: service?.category.id ?? "",
    staff_id: service?.staff.id ?? "",
    duration_minutes: service ? String(service.duration_minutes) : "",
    price: service?.price ?? "",
    is_quote_only: service?.is_quote_only ?? false,
    is_nail_service: service?.is_nail_service ?? false,
    is_active: service?.is_active ?? true,
    description: service?.description ?? "",
  };
}

export default function ServiceFormModal({
  service,
  onClose,
}: {
  /** When provided, the modal edits this service; otherwise it creates a new one. */
  service?: Service;
  onClose: () => void;
}) {
  const isEdit = Boolean(service);
  const categories = useCategories();
  const staff = useStaff();
  const createMutation = useCreateService();
  const updateMutation = useUpdateService(service?.id ?? "");
  const mutation = isEdit ? updateMutation : createMutation;

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<FormValues>({ defaultValues: toDefaults(service) });

  const quoteOnly = watch("is_quote_only");

  const onSubmit = handleSubmit((values) => {
    const base = {
      category_id: values.category_id,
      staff_id: values.staff_id,
      name: values.name.trim(),
      description: values.description.trim(),
      duration_minutes: Number(values.duration_minutes),
      is_quote_only: values.is_quote_only,
      is_nail_service: values.is_nail_service,
      is_active: values.is_active,
      price: values.is_quote_only || values.price.trim() === ""
        ? null
        : values.price.trim(),
    };

    if (isEdit) {
      updateMutation.mutate(base as UpdateServiceInput, { onSuccess: onClose });
    } else {
      createMutation.mutate(base as CreateServiceInput, { onSuccess: onClose });
    }
  });

  return (
    <Modal title={isEdit ? "Editar serviço" : "Novo serviço"} onClose={onClose}>
      <form onSubmit={onSubmit} className={panel.page}>
        <Field
          label="Nome"
          htmlFor="service-name"
          error={errors.name?.message}
        >
          <Input
            id="service-name"
            invalid={Boolean(errors.name)}
            {...register("name", { required: "Indica um nome." })}
          />
        </Field>

        <div className={panel.grid2}>
          <Field
            label="Categoria"
            htmlFor="service-category"
            error={errors.category_id?.message}
          >
            <Select
              id="service-category"
              invalid={Boolean(errors.category_id)}
              disabled={categories.isLoading}
              {...register("category_id", {
                required: "Escolhe uma categoria.",
              })}
            >
              <option value="">Selecionar…</option>
              {(categories.data ?? []).map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </Select>
          </Field>

          <Field
            label="Staff"
            htmlFor="service-staff"
            error={errors.staff_id?.message}
          >
            <Select
              id="service-staff"
              invalid={Boolean(errors.staff_id)}
              disabled={staff.isLoading}
              {...register("staff_id", { required: "Escolhe um staff." })}
            >
              <option value="">Selecionar…</option>
              {(staff.data ?? []).map((member) => (
                <option key={member.id} value={member.id}>
                  {member.first_name} {member.last_name}
                </option>
              ))}
            </Select>
          </Field>
        </div>

        <div className={panel.grid2}>
          <Field
            label="Duração (minutos)"
            htmlFor="service-duration"
            error={errors.duration_minutes?.message}
          >
            <Input
              id="service-duration"
              type="number"
              min={1}
              step={1}
              invalid={Boolean(errors.duration_minutes)}
              {...register("duration_minutes", {
                required: "Indica a duração.",
                min: { value: 1, message: "Tem de ser maior que zero." },
              })}
            />
          </Field>

          <Field
            label="Preço (€)"
            htmlFor="service-price"
            hint={quoteOnly ? "Definido como sob orçamento." : "Opcional."}
            error={errors.price?.message}
          >
            <Input
              id="service-price"
              type="number"
              min={0}
              step="0.01"
              disabled={quoteOnly}
              invalid={Boolean(errors.price)}
              {...register("price")}
            />
          </Field>
        </div>

        <Field label="Descrição" htmlFor="service-description">
          <Input id="service-description" {...register("description")} />
        </Field>

        <div className={panel.formRow}>
          <label>
            <input type="checkbox" {...register("is_quote_only")} /> Sob orçamento
          </label>
          <label>
            <input type="checkbox" {...register("is_nail_service")} /> Serviço de
            unhas
          </label>
          <label>
            <input type="checkbox" {...register("is_active")} /> Ativo
          </label>
        </div>

        {mutation.isError ? (
          <p className={panel.feedbackError} role="alert">
            {apiErrorMessage(
              mutation.error,
              "Não foi possível guardar o serviço.",
            )}
          </p>
        ) : null}

        <div className={panel.actions}>
          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? "A guardar…" : "Guardar"}
          </Button>
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
        </div>
      </form>
    </Modal>
  );
}
