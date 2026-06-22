"use client";

import { useForm } from "react-hook-form";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Input from "@/components/ui/Input";
import Modal from "@/components/ui/Modal";
import Select from "@/components/ui/Select";
import type { EducationType, StaffEducation } from "@/features/staff/types";
import { apiErrorMessage } from "@/lib/api";

import {
  useCreateEducation,
  useUpdateEducation,
} from "../hooks/useEducations";
import { EDUCATION_TYPES } from "../types";

import panel from "@/features/bo/shared/panel.module.css";

interface FormValues {
  education_type: EducationType;
  provider: string;
  title: string;
  completed_on: string;
  description: string;
}

interface EducationFormModalProps {
  staffId: string;
  /** When set, edits this entry; otherwise creates a new one. */
  education?: StaffEducation;
  onClose: () => void;
}

export default function EducationFormModal({
  staffId,
  education,
  onClose,
}: EducationFormModalProps) {
  const isEdit = !!education;
  const create = useCreateEducation(staffId);
  const update = useUpdateEducation(staffId);
  const pending = create.isPending || update.isPending;
  const error = create.error ?? update.error;
  const isError = create.isError || update.isError;

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    defaultValues: {
      education_type: education?.education_type ?? "formation",
      provider: education?.provider ?? "",
      title: education?.title ?? "",
      completed_on: education?.completed_on ?? "",
      description: education?.description ?? "",
    },
  });

  const onSubmit = handleSubmit((values) => {
    const payload = {
      education_type: values.education_type,
      provider: values.provider.trim(),
      title: values.title.trim(),
      completed_on: values.completed_on,
      description: values.description.trim(),
    };

    if (isEdit && education) {
      update.mutate(
        { id: education.id, input: payload },
        { onSuccess: onClose },
      );
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  });

  return (
    <Modal
      title={isEdit ? "Editar formação" : "Nova formação"}
      onClose={onClose}
    >
      <form onSubmit={onSubmit} noValidate className={panel.page}>
        <Field label="Tipo" htmlFor="education-type">
          <Select id="education-type" {...register("education_type")}>
            {EDUCATION_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </Select>
        </Field>

        <Field
          label="Título"
          htmlFor="education-title"
          error={errors.title ? "O título é obrigatório." : undefined}
        >
          <Input
            id="education-title"
            invalid={!!errors.title}
            {...register("title", { required: true })}
          />
        </Field>

        <Field
          label="Entidade"
          htmlFor="education-provider"
          error={errors.provider ? "A entidade é obrigatória." : undefined}
        >
          <Input
            id="education-provider"
            invalid={!!errors.provider}
            {...register("provider", { required: true })}
          />
        </Field>

        <Field
          label="Data de conclusão"
          htmlFor="education-completed-on"
          error={errors.completed_on ? "A data é obrigatória." : undefined}
        >
          <Input
            id="education-completed-on"
            type="date"
            invalid={!!errors.completed_on}
            {...register("completed_on", { required: true })}
          />
        </Field>

        <Field
          label="Descrição"
          htmlFor="education-description"
          hint="Opcional — visível na página pública da equipa."
        >
          <textarea
            id="education-description"
            rows={4}
            {...register("description")}
          />
        </Field>

        {isError ? (
          <p className={panel.feedbackError} role="alert">
            {apiErrorMessage(error, "Não foi possível guardar a formação.")}
          </p>
        ) : null}

        <div className={panel.actions}>
          <Button type="submit" disabled={pending}>
            {pending ? "A guardar…" : "Guardar"}
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={pending}
          >
            Cancelar
          </Button>
        </div>
      </form>
    </Modal>
  );
}
