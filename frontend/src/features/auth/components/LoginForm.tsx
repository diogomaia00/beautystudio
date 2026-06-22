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
import { MSISDN_PATTERN, OTP_PATTERN } from "../validation";
import styles from "./AuthForm.module.css";

interface PhoneValues {
  msisdn: string;
}
interface CodeValues {
  code: string;
}

export default function LoginForm() {
  const router = useRouter();
  const [step, setStep] = useState<"phone" | "code">("phone");
  const [msisdn, setMsisdn] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const phoneForm = useForm<PhoneValues>();
  const codeForm = useForm<CodeValues>();
  const requestOtp = useRequestOtp();
  const verifyOtp = useVerifyOtp();

  const submitPhone = phoneForm.handleSubmit(async (values) => {
    setFormError(null);
    try {
      await requestOtp.mutateAsync({ msisdn: values.msisdn, purpose: "login" });
      setMsisdn(values.msisdn);
      setStep("code");
    } catch (error) {
      setFormError(apiErrorMessage(error));
    }
  });

  const submitCode = codeForm.handleSubmit(async (values) => {
    setFormError(null);
    try {
      await verifyOtp.mutateAsync({ msisdn, code: values.code, purpose: "login" });
      router.push("/");
    } catch (error) {
      setFormError(apiErrorMessage(error, "Código inválido ou expirado."));
    }
  });

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h1 className={styles.title}>Entrar</h1>
        <p className={styles.subtitle}>
          {step === "phone"
            ? "Enviamos-te um código por SMS para entrares."
            : `Introduz o código enviado para ${msisdn}.`}
        </p>
      </div>

      {formError && <p className={styles.error}>{formError}</p>}

      {step === "phone" ? (
        <form className={styles.form} onSubmit={submitPhone} noValidate>
          <Field
            label="Telemóvel"
            htmlFor="msisdn"
            hint="Formato internacional, ex. +351912345678"
            error={phoneForm.formState.errors.msisdn?.message}
          >
            <Input
              id="msisdn"
              type="tel"
              inputMode="tel"
              autoComplete="tel"
              placeholder="+351912345678"
              invalid={!!phoneForm.formState.errors.msisdn}
              {...phoneForm.register("msisdn", {
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
              {verifyOtp.isPending ? "A confirmar…" : "Confirmar"}
            </Button>
            <button
              type="button"
              className={styles.linkButton}
              onClick={() => {
                setStep("phone");
                setFormError(null);
              }}
            >
              Usar outro número
            </button>
          </div>
        </form>
      )}

      <p className={styles.footerText}>
        Ainda não tens conta? <Link href="/register">Criar conta</Link>
      </p>
    </div>
  );
}
