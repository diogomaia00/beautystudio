"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Input from "@/components/ui/Input";
import { apiErrorMessage } from "@/lib/api";

import { useRequestOtp, useVerifyOtp } from "../hooks/useAuthActions";
import type { SignupData } from "../types";
import { MSISDN_PATTERN, OTP_PATTERN, todayISO, validateBirthday } from "../validation";
import PhoneField from "./PhoneField";
import styles from "./AuthForm.module.css";

interface DetailsValues extends SignupData {
  msisdn: string;
}
interface CodeValues {
  code: string;
}

export default function RegisterForm() {
  const router = useRouter();
  const [step, setStep] = useState<"details" | "code">("details");
  const [details, setDetails] = useState<DetailsValues | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  // Real-time validation (e.g. birthday) so errors show as the user fills in.
  const detailsForm = useForm<DetailsValues>({
    mode: "onChange",
    defaultValues: { msisdn: "" },
  });
  const codeForm = useForm<CodeValues>();
  const requestOtp = useRequestOtp();
  const verifyOtp = useVerifyOtp();
  const errors = detailsForm.formState.errors;

  const submitDetails = detailsForm.handleSubmit(async (values) => {
    setFormError(null);
    try {
      await requestOtp.mutateAsync({ msisdn: values.msisdn, purpose: "signup" });
      setDetails(values);
      setStep("code");
    } catch (error) {
      setFormError(apiErrorMessage(error));
    }
  });

  const submitCode = codeForm.handleSubmit(async (values) => {
    if (!details) return;
    setFormError(null);
    try {
      await verifyOtp.mutateAsync({
        msisdn: details.msisdn,
        code: values.code,
        purpose: "signup",
        first_name: details.first_name,
        last_name: details.last_name,
        email: details.email,
        birthday: details.birthday,
      });
      router.push("/");
    } catch (error) {
      setFormError(apiErrorMessage(error, "Código inválido ou expirado."));
    }
  });

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h1 className={styles.title}>Criar conta</h1>
        <p className={styles.subtitle}>
          {step === "details"
            ? "Precisamos de alguns dados para criares a tua conta."
            : `Introduz o código enviado para ${details?.msisdn}.`}
        </p>
      </div>

      {formError && <p className={styles.error}>{formError}</p>}

      {step === "details" ? (
        <form className={styles.form} onSubmit={submitDetails} noValidate>
          <Field label="Nome" htmlFor="first_name" error={errors.first_name?.message}>
            <Input
              id="first_name"
              autoComplete="given-name"
              invalid={!!errors.first_name}
              {...detailsForm.register("first_name", { required: "Indica o teu nome." })}
            />
          </Field>
          <Field label="Apelido" htmlFor="last_name" error={errors.last_name?.message}>
            <Input
              id="last_name"
              autoComplete="family-name"
              invalid={!!errors.last_name}
              {...detailsForm.register("last_name", { required: "Indica o teu apelido." })}
            />
          </Field>
          <Field label="Email" htmlFor="email" error={errors.email?.message}>
            <Input
              id="email"
              type="email"
              autoComplete="email"
              invalid={!!errors.email}
              {...detailsForm.register("email", {
                required: "Indica o teu email.",
                pattern: { value: /^[^@\s]+@[^@\s]+\.[^@\s]+$/, message: "Email inválido." },
              })}
            />
          </Field>
          <Field
            label="Data de nascimento"
            htmlFor="birthday"
            hint="Tens de ter pelo menos 12 anos."
            error={errors.birthday?.message}
          >
            <Input
              id="birthday"
              type="date"
              max={todayISO()}
              invalid={!!errors.birthday}
              {...detailsForm.register("birthday", {
                required: "Indica a tua data de nascimento.",
                validate: validateBirthday,
              })}
            />
          </Field>
          <Field
            label="Telemóvel"
            htmlFor="msisdn"
            hint="Escolhe o país e escreve o número, ex. 912345678"
            error={errors.msisdn?.message}
          >
            <Controller
              control={detailsForm.control}
              name="msisdn"
              defaultValue=""
              rules={{
                required: "Indica o teu telemóvel.",
                pattern: { value: MSISDN_PATTERN, message: "Número inválido." },
              }}
              render={({ field, fieldState }) => (
                <PhoneField
                  id="msisdn"
                  value={field.value}
                  onChange={field.onChange}
                  onBlur={field.onBlur}
                  invalid={!!fieldState.error}
                />
              )}
            />
          </Field>
          <div className={styles.actions}>
            <Button type="submit" size="lg" disabled={requestOtp.isPending}>
              {requestOtp.isPending ? "A enviar…" : "Enviar código"}
            </Button>
          </div>
        </form>
      ) : (
        <form className={styles.form} onSubmit={submitCode} noValidate>
          <Field label="Telemóvel" htmlFor="msisdn-sent">
            <Input id="msisdn-sent" type="tel" value={details?.msisdn ?? ""} readOnly disabled />
          </Field>
          <Field
            label="Código"
            htmlFor="code"
            hint="6 dígitos · válido 5 minutos"
            error={codeForm.formState.errors.code?.message}
          >
            <Input
              id="code"
              type="text"
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={6}
              placeholder="000000"
              autoFocus
              invalid={!!codeForm.formState.errors.code}
              {...codeForm.register("code", {
                required: "Introduz o código.",
                pattern: { value: OTP_PATTERN, message: "O código tem 6 dígitos." },
              })}
            />
          </Field>
          <div className={styles.actions}>
            <Button type="submit" size="lg" disabled={verifyOtp.isPending}>
              {verifyOtp.isPending ? "A criar conta…" : "Criar conta"}
            </Button>
            <button
              type="button"
              className={styles.linkButton}
              onClick={() => {
                setStep("details");
                setFormError(null);
                codeForm.reset();
              }}
            >
              Editar dados
            </button>
          </div>
        </form>
      )}

      <p className={styles.footerText}>
        Já tens conta? <Link href="/login">Entrar</Link>
      </p>
    </div>
  );
}
