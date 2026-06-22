"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Input from "@/components/ui/Input";
import { apiErrorMessage } from "@/lib/api";

import { useRequestOtp, useVerifyOtp } from "../hooks/useAuthActions";
import type { SignupData } from "../types";
import { MSISDN_PATTERN, OTP_PATTERN } from "../validation";
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

  const detailsForm = useForm<DetailsValues>();
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
          <Field label="Data de nascimento" htmlFor="birthday" error={errors.birthday?.message}>
            <Input
              id="birthday"
              type="date"
              invalid={!!errors.birthday}
              {...detailsForm.register("birthday", { required: "Indica a tua data de nascimento." })}
            />
          </Field>
          <Field
            label="Telemóvel"
            htmlFor="msisdn"
            hint="Formato internacional, ex. +351912345678"
            error={errors.msisdn?.message}
          >
            <Input
              id="msisdn"
              type="tel"
              inputMode="tel"
              autoComplete="tel"
              placeholder="+351912345678"
              invalid={!!errors.msisdn}
              {...detailsForm.register("msisdn", {
                required: "Indica o teu telemóvel.",
                pattern: { value: MSISDN_PATTERN, message: "Número inválido." },
              })}
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
