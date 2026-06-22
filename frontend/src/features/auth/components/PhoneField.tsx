"use client";

import { useState } from "react";

import Input from "@/components/ui/Input";

import { COUNTRIES, composeE164, digitsOnly, parseE164 } from "../countries";
import styles from "./PhoneField.module.css";

interface PhoneFieldProps {
  id: string;
  /** Composed E.164 value (or "") — typically from a react-hook-form Controller. */
  value: string;
  onChange: (e164: string) => void;
  onBlur?: () => void;
  invalid?: boolean;
  disabled?: boolean;
}

/**
 * Phone input with a country dropdown (default Portugal). The user types only
 * the national number; the component emits the composed E.164 MSISDN
 * (`+<dial><national>`), so the rest of the form keeps working with a single
 * `msisdn` value.
 */
export default function PhoneField({
  id,
  value,
  onChange,
  onBlur,
  invalid,
  disabled,
}: PhoneFieldProps) {
  // Seed country + national from any initial value once (value is owned here after).
  const seed = parseE164(value);
  const [iso, setIso] = useState(seed.country.iso);
  const [national, setNational] = useState(seed.national);

  const emit = (nextIso: string, nextNational: string) => {
    const c = COUNTRIES.find((x) => x.iso === nextIso) ?? COUNTRIES[0];
    onChange(composeE164(c, nextNational));
  };

  return (
    <div className={styles.row}>
      <select
        aria-label="Indicativo do país"
        className={styles.country}
        value={iso}
        disabled={disabled}
        onChange={(e) => {
          setIso(e.target.value);
          emit(e.target.value, national);
        }}
      >
        {COUNTRIES.map((c) => (
          <option key={c.iso} value={c.iso}>
            {c.flag} {c.name} (+{c.dial})
          </option>
        ))}
      </select>
      <Input
        id={id}
        type="tel"
        inputMode="tel"
        autoComplete="tel-national"
        placeholder="912345678"
        className={styles.number}
        invalid={invalid}
        disabled={disabled}
        value={national}
        onBlur={onBlur}
        onChange={(e) => {
          const next = digitsOnly(e.target.value);
          setNational(next);
          emit(iso, next);
        }}
      />
    </div>
  );
}
