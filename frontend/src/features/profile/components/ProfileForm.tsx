"use client";

import { useForm } from "react-hook-form";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";
import { useCurrentUser } from "@/features/auth/hooks/useCurrentUser";
import type { NotificationChannel } from "@/features/auth/types";
import { apiErrorMessage } from "@/lib/api";

import { useUpdateProfile } from "../hooks/useUpdateProfile";
import styles from "./ProfileForm.module.css";

interface FormValues {
  first_name: string;
  last_name: string;
  email: string;
  birthday: string;
  preferred_channel: NotificationChannel;
}

const CHANNELS: { value: NotificationChannel; label: string }[] = [
  { value: "whatsapp", label: "WhatsApp" },
  { value: "sms", label: "SMS" },
  { value: "email", label: "Email" },
];

export default function ProfileForm() {
  const { data: user, isLoading } = useCurrentUser();
  const update = useUpdateProfile();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    values: user
      ? {
          first_name: user.first_name,
          last_name: user.last_name,
          email: user.email,
          birthday: user.birthday ?? "",
          preferred_channel: user.preferred_channel,
        }
      : undefined,
  });

  if (isLoading) return <p className={styles.status}>A carregar…</p>;

  if (!user || user.role !== "client") {
    return (
      <div className={styles.card}>
        <p>Inicia sessão como cliente para veres o teu perfil.</p>
        <Button href="/login" size="sm">
          Entrar
        </Button>
      </div>
    );
  }

  const onSubmit = handleSubmit((values) => {
    update.mutate(values);
  });

  return (
    <form className={styles.card} onSubmit={onSubmit} noValidate>
      <Field label="Telemóvel" htmlFor="msisdn" hint="Contacta o staff para alterar o número.">
        <Input id="msisdn" value={user.msisdn} disabled readOnly />
      </Field>

      <Field label="Nome" htmlFor="first_name" error={errors.first_name?.message}>
        <Input
          id="first_name"
          invalid={!!errors.first_name}
          {...register("first_name", { required: "Indica o teu nome." })}
        />
      </Field>

      <Field label="Apelido" htmlFor="last_name" error={errors.last_name?.message}>
        <Input
          id="last_name"
          invalid={!!errors.last_name}
          {...register("last_name", { required: "Indica o teu apelido." })}
        />
      </Field>

      <Field label="Email" htmlFor="email" error={errors.email?.message}>
        <Input
          id="email"
          type="email"
          invalid={!!errors.email}
          {...register("email", {
            required: "Indica o teu email.",
            pattern: { value: /^[^@\s]+@[^@\s]+\.[^@\s]+$/, message: "Email inválido." },
          })}
        />
      </Field>

      <Field label="Data de nascimento" htmlFor="birthday" error={errors.birthday?.message}>
        <Input
          id="birthday"
          type="date"
          invalid={!!errors.birthday}
          {...register("birthday", { required: "Indica a tua data de nascimento." })}
        />
      </Field>

      <Field
        label="Canal preferido"
        htmlFor="preferred_channel"
        hint="Tentamos sempre o WhatsApp primeiro; este é o canal a privilegiar a seguir."
      >
        <Select id="preferred_channel" {...register("preferred_channel")}>
          {CHANNELS.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </Select>
      </Field>

      {update.isError && <p className={styles.error}>{apiErrorMessage(update.error)}</p>}
      {update.isSuccess && <p className={styles.success}>Perfil atualizado.</p>}

      <div className={styles.actions}>
        <Button type="submit" size="lg" disabled={update.isPending}>
          {update.isPending ? "A guardar…" : "Guardar"}
        </Button>
      </div>
    </form>
  );
}
